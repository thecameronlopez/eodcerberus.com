from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy.orm import selectinload

from app.extensions import db
from app.models import Deduction, LineItem, Location, Tender, Ticket, Transaction, User

"""
Reporting service output templates.

Money values are integer cents.

Canonical `user_eod` response shape:
{
    "success": true,
    "report_type": "user_eod",
    "meta": {
        "report_date_start": "YYYY-MM-DD",
        "report_date_end": "YYYY-MM-DD",
        "user_id": int
    },
    "report": {
        "user": {
            "id": int,
            "first_name": str,
            "last_name": str,
            "location_id": int,
            "location_name": str
        },
        "sales": {"subtotal": int, "tax_total": int, "total_sold": int},
        "receipts": {
            "total_received": int,
            "by_payment_type": [
                {"payment_type_id": int, "payment_type_name": str, "amount": int}
            ]
        },
        "balances": {"balance_owed": int},
        "breakdowns": {
            "by_sales_category": [
                {
                    "sales_category_id": int,
                    "sales_category_name": str,
                    "subtotal": int,
                    "tax_total": int,
                    "total": int
                }
            ]
        },
        "deductions": {"count": int, "total_deductions": int},
        "cash": {"cash_received_gross": int, "cash_after_deductions": int},
        "tickets": [
            {
                "id": int,
                "ticket_number": int,
                "ticket_date": "YYYY-MM-DD",
                "subtotal": int,
                "tax_total": int,
                "total": int,
                "total_paid": int,
                "balance_owed": int,
                "is_open": bool
            }
        ]
    }
}
"""


class ReportingService:
    SUPPORTED_REPORT_TYPES = {"user_eod", "location", "multi_user", "master"}

    def build(
        self,
        report_type: str,
        *,
        start: date | str,
        end: date | str | None = None,
        user_id: int | None = None,
        user_ids: list[int] | None = None,
        location_id: int | None = None,
        location_ids: list[int] | None = None,
        include_ticket_details: bool = True,
    ) -> dict:
        report_type = (report_type or "").strip().lower()
        if report_type not in self.SUPPORTED_REPORT_TYPES:
            raise ValueError(f"Unsupported report type: {report_type}")

        start_date, end_date = self._normalize_dates(start, end)
        user_ids = self._normalize_int_list(user_ids)
        location_ids = self._normalize_int_list(location_ids)

        if report_type == "user_eod":
            target_user_id = int(user_id or (user_ids[0] if user_ids else 0))
            if target_user_id <= 0:
                raise ValueError("user_eod requires user_id")
            return self._build_user_eod(
                user_id=target_user_id,
                start_date=start_date,
                end_date=end_date,
                include_ticket_details=include_ticket_details,
            )

        if report_type == "location":
            target_location_id = int(location_id or (location_ids[0] if location_ids else 0))
            if target_location_id <= 0:
                raise ValueError("location report requires location_id")
            return self._build_location_report(
                location_id=target_location_id,
                start_date=start_date,
                end_date=end_date,
                include_ticket_details=include_ticket_details,
            )

        if report_type == "multi_user":
            if not user_ids:
                raise ValueError("multi_user report requires user_ids")
            return self._build_multi_user_report(
                user_ids=user_ids,
                start_date=start_date,
                end_date=end_date,
                include_ticket_details=include_ticket_details,
            )

        return self._build_master_report(
            start_date=start_date,
            end_date=end_date,
            location_ids=location_ids,
            include_ticket_details=include_ticket_details,
        )

    def _build_user_eod(
        self,
        *,
        user_id: int,
        start_date: date,
        end_date: date,
        include_ticket_details: bool,
    ) -> dict:
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        tickets = self._load_tickets(
            start_date=start_date,
            end_date=end_date,
            user_ids=[user_id],
        )
        deductions = self._load_deductions(
            start_date=start_date,
            end_date=end_date,
            user_ids=[user_id],
        )
        payload = self._build_user_payload(
            user=user,
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=include_ticket_details,
        )
        return {
            "success": True,
            "report_type": "user_eod",
            "meta": {
                "report_date_start": start_date.isoformat(),
                "report_date_end": end_date.isoformat(),
                "user_id": user_id,
            },
            "report": payload,
        }

    def _build_location_report(
        self,
        *,
        location_id: int,
        start_date: date,
        end_date: date,
        include_ticket_details: bool,
    ) -> dict:
        location = db.session.get(Location, location_id)
        if not location:
            raise ValueError(f"Location {location_id} not found")

        users = self._load_users(location_ids=[location_id])
        user_map = {u.id: u for u in users}

        tickets = self._load_tickets(
            start_date=start_date,
            end_date=end_date,
            location_ids=[location_id],
        )
        deductions = self._load_deductions(
            start_date=start_date,
            end_date=end_date,
            user_ids=list(user_map.keys()),
        )

        aggregate = self._build_aggregate_payload(
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=include_ticket_details,
        )
        users_payload = self._build_per_user_payloads(
            users=user_map,
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=False,
        )

        aggregate["location"] = self._serialize_location(location)
        aggregate["users"] = users_payload

        return {
            "success": True,
            "report_type": "location",
            "meta": {
                "report_date_start": start_date.isoformat(),
                "report_date_end": end_date.isoformat(),
                "location_id": location_id,
            },
            "report": aggregate,
        }

    def _build_multi_user_report(
        self,
        *,
        user_ids: list[int],
        start_date: date,
        end_date: date,
        include_ticket_details: bool,
    ) -> dict:
        users = self._load_users(user_ids=user_ids)
        user_map = {u.id: u for u in users}
        effective_user_ids = list(user_map.keys())

        tickets = self._load_tickets(
            start_date=start_date,
            end_date=end_date,
            user_ids=effective_user_ids,
        )
        deductions = self._load_deductions(
            start_date=start_date,
            end_date=end_date,
            user_ids=effective_user_ids,
        )

        aggregate = self._build_aggregate_payload(
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=include_ticket_details,
        )
        aggregate["users"] = self._build_per_user_payloads(
            users=user_map,
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=False,
        )

        return {
            "success": True,
            "report_type": "multi_user",
            "meta": {
                "report_date_start": start_date.isoformat(),
                "report_date_end": end_date.isoformat(),
                "user_ids": effective_user_ids,
            },
            "report": aggregate,
        }

    def _build_master_report(
        self,
        *,
        start_date: date,
        end_date: date,
        location_ids: list[int] | None,
        include_ticket_details: bool,
    ) -> dict:
        users = self._load_users(location_ids=location_ids)
        user_map = {u.id: u for u in users}
        effective_user_ids = list(user_map.keys())

        tickets = self._load_tickets(
            start_date=start_date,
            end_date=end_date,
            user_ids=effective_user_ids if effective_user_ids else None,
            location_ids=location_ids,
        )
        deductions = self._load_deductions(
            start_date=start_date,
            end_date=end_date,
            user_ids=effective_user_ids if effective_user_ids else None,
        )

        aggregate = self._build_aggregate_payload(
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=include_ticket_details,
        )
        aggregate["users"] = self._build_per_user_payloads(
            users=user_map,
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=False,
        )
        aggregate["locations"] = self._build_per_location_payloads(
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=False,
        )

        return {
            "success": True,
            "report_type": "master",
            "meta": {
                "report_date_start": start_date.isoformat(),
                "report_date_end": end_date.isoformat(),
                "location_ids": location_ids or [],
            },
            "report": aggregate,
        }

    @staticmethod
    def _normalize_dates(start: date | str, end: date | str | None) -> tuple[date, date]:
        start_date = ReportingService._to_date(start)
        end_date = ReportingService._to_date(end) if end else start_date
        if end_date < start_date:
            raise ValueError("end date cannot be before start date")
        return start_date, end_date

    @staticmethod
    def _to_date(value: date | str) -> date:
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            return date.fromisoformat(value)
        raise ValueError(f"Invalid date value: {value!r}")

    @staticmethod
    def _normalize_int_list(values: list[int] | None) -> list[int]:
        if not values:
            return []
        return [int(v) for v in values if int(v) > 0]

    def _load_users(
        self,
        *,
        user_ids: list[int] | None = None,
        location_ids: list[int] | None = None,
    ) -> list[User]:
        q = db.session.query(User).options(selectinload(User.location))
        if user_ids:
            q = q.filter(User.id.in_(user_ids))
        if location_ids:
            q = q.filter(User.location_id.in_(location_ids))
        return q.all()

    def _load_tickets(
        self,
        *,
        start_date: date,
        end_date: date,
        user_ids: list[int] | None = None,
        location_ids: list[int] | None = None,
    ) -> list[Ticket]:
        q = (
            db.session.query(Ticket)
            .options(
                selectinload(Ticket.user).selectinload(User.location),
                selectinload(Ticket.location),
                selectinload(Ticket.transactions)
                .selectinload(Transaction.line_items)
                .selectinload(LineItem.sales_category),
                selectinload(Ticket.transactions)
                .selectinload(Transaction.tenders)
                .selectinload(Tender.payment_type),
            )
            .filter(Ticket.ticket_date >= start_date, Ticket.ticket_date <= end_date)
        )
        if user_ids:
            q = q.filter(Ticket.user_id.in_(user_ids))
        if location_ids:
            q = q.filter(Ticket.location_id.in_(location_ids))
        return q.all()

    def _load_deductions(
        self,
        *,
        start_date: date,
        end_date: date,
        user_ids: list[int] | None = None,
    ) -> list[Deduction]:
        q = (
            db.session.query(Deduction)
            .options(selectinload(Deduction.user))
            .filter(Deduction.date >= start_date, Deduction.date <= end_date)
        )
        if user_ids:
            q = q.filter(Deduction.user_id.in_(user_ids))
        return q.all()

    def _build_per_user_payloads(
        self,
        *,
        users: dict[int, User],
        tickets: list[Ticket],
        deductions: list[Deduction],
        include_ticket_details: bool,
    ) -> list[dict]:
        tickets_by_user: dict[int, list[Ticket]] = defaultdict(list)
        for ticket in tickets:
            tickets_by_user[int(ticket.user_id)].append(ticket)

        deductions_by_user: dict[int, list[Deduction]] = defaultdict(list)
        for deduction in deductions:
            deductions_by_user[int(deduction.user_id)].append(deduction)

        payload = []
        for uid in sorted(users.keys()):
            user = users[uid]
            payload.append(
                self._build_user_payload(
                    user=user,
                    tickets=tickets_by_user.get(uid, []),
                    deductions=deductions_by_user.get(uid, []),
                    include_ticket_details=include_ticket_details,
                )
            )
        return payload

    def _build_per_location_payloads(
        self,
        *,
        tickets: list[Ticket],
        deductions: list[Deduction],
        include_ticket_details: bool,
    ) -> list[dict]:
        tickets_by_location: dict[int, list[Ticket]] = defaultdict(list)
        for ticket in tickets:
            tickets_by_location[int(ticket.location_id)].append(ticket)

        deductions_by_location: dict[int, list[Deduction]] = defaultdict(list)
        for deduction in deductions:
            location_id = int(deduction.user.location_id) if deduction.user else None
            if location_id:
                deductions_by_location[location_id].append(deduction)

        location_ids = set(tickets_by_location.keys()) | set(deductions_by_location.keys())
        payload = []
        for location_id in sorted(location_ids):
            tickets_for_location = tickets_by_location.get(location_id, [])
            location_obj = (
                tickets_for_location[0].location if tickets_for_location else db.session.get(Location, location_id)
            )
            aggregate = self._build_aggregate_payload(
                tickets=tickets_for_location,
                deductions=deductions_by_location.get(location_id, []),
                include_ticket_details=include_ticket_details,
            )
            aggregate["location"] = self._serialize_location(location_obj)
            payload.append(aggregate)
        return payload

    def _build_user_payload(
        self,
        *,
        user: User,
        tickets: list[Ticket],
        deductions: list[Deduction],
        include_ticket_details: bool,
    ) -> dict:
        payload = self._build_aggregate_payload(
            tickets=tickets,
            deductions=deductions,
            include_ticket_details=include_ticket_details,
        )
        payload["user"] = self._serialize_user(user)
        return payload

    def _build_aggregate_payload(
        self,
        *,
        tickets: list[Ticket],
        deductions: list[Deduction],
        include_ticket_details: bool,
    ) -> dict:
        line_items = [li for ticket in tickets for li in ticket.line_items]
        tenders = [td for ticket in tickets for td in ticket.tenders]

        sales, by_sales_category = self._aggregate_sales(line_items)
        receipts, by_payment_type, cash_received_gross = self._aggregate_receipts(tenders)
        total_deductions = sum(int(d.amount or 0) for d in deductions)

        payload = {
            "sales": sales,
            "receipts": {
                "total_received": receipts,
                "by_payment_type": by_payment_type,
            },
            "balances": {
                "balance_owed": sales["total_sold"] - receipts,
            },
            "breakdowns": {
                "by_sales_category": by_sales_category,
            },
            "deductions": {
                "count": len(deductions),
                "total_deductions": total_deductions,
            },
            "cash": {
                "cash_received_gross": cash_received_gross,
                "cash_after_deductions": cash_received_gross - total_deductions,
            },
            "tickets": [self._serialize_ticket(ticket) for ticket in tickets] if include_ticket_details else [],
        }
        return payload

    @staticmethod
    def _aggregate_sales(line_items: list[LineItem]) -> tuple[dict, list[dict]]:
        subtotal = 0
        tax_total = 0
        total_sold = 0

        by_category: dict[tuple[int, str], dict] = {}
        for item in line_items:
            line_subtotal = int((item.unit_price or 0) * (item.quantity or 0))
            line_tax = int(item.tax_amount or 0)
            line_total = int(item.total or 0)

            subtotal += line_subtotal
            tax_total += line_tax
            total_sold += line_total

            category_id = int(item.sales_category_id)
            category_name = item.sales_category.name if item.sales_category else f"Category #{category_id}"
            key = (category_id, category_name)
            if key not in by_category:
                by_category[key] = {
                    "sales_category_id": category_id,
                    "sales_category_name": category_name,
                    "subtotal": 0,
                    "tax_total": 0,
                    "total": 0,
                }
            by_category[key]["subtotal"] += line_subtotal
            by_category[key]["tax_total"] += line_tax
            by_category[key]["total"] += line_total

        sorted_categories = sorted(
            by_category.values(),
            key=lambda row: (-row["total"], row["sales_category_name"]),
        )
        return (
            {
                "subtotal": subtotal,
                "tax_total": tax_total,
                "total_sold": total_sold,
            },
            sorted_categories,
        )

    @staticmethod
    def _aggregate_receipts(tenders: list[Tender]) -> tuple[int, list[dict], int]:
        total_received = 0
        cash_received_gross = 0
        by_payment_type: dict[tuple[int, str], dict] = {}

        for tender in tenders:
            amount = int(tender.amount or 0)
            total_received += amount

            payment_type_id = int(tender.payment_type_id)
            payment_type_name = (
                tender.payment_type.name if tender.payment_type else f"Payment #{payment_type_id}"
            )
            key = (payment_type_id, payment_type_name)
            if key not in by_payment_type:
                by_payment_type[key] = {
                    "payment_type_id": payment_type_id,
                    "payment_type_name": payment_type_name,
                    "amount": 0,
                }
            by_payment_type[key]["amount"] += amount

            if payment_type_name.strip().lower() == "cash":
                cash_received_gross += amount

        sorted_payment_types = sorted(
            by_payment_type.values(),
            key=lambda row: (-row["amount"], row["payment_type_name"]),
        )
        return total_received, sorted_payment_types, cash_received_gross

    @staticmethod
    def _serialize_user(user: User) -> dict:
        return {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "location_id": user.location_id,
            "location_name": user.location.name if user.location else None,
        }

    @staticmethod
    def _serialize_location(location: Location | None) -> dict | None:
        if not location:
            return None
        return {
            "id": location.id,
            "name": location.name,
            "code": location.code,
            "current_tax_rate": float(location.current_tax_rate) if location.current_tax_rate is not None else None,
        }

    @staticmethod
    def _serialize_ticket(ticket: Ticket) -> dict:
        return {
            "id": ticket.id,
            "ticket_number": ticket.ticket_number,
            "ticket_date": ticket.ticket_date.isoformat() if ticket.ticket_date else None,
            "subtotal": int(ticket.subtotal or 0),
            "tax_total": int(ticket.tax_total or 0),
            "total": int(ticket.total or 0),
            "total_paid": int(ticket.total_paid or 0),
            "balance_owed": int(ticket.balance_owed or 0),
            "is_open": bool(ticket.is_open),
        }


def build_user_eod_report(
    user: User,
    report_date_start: date,
    report_date_end: date | None = None,
) -> dict:
    service = ReportingService()
    return service.build(
        "user_eod",
        start=report_date_start,
        end=report_date_end,
        user_id=user.id,
    )
