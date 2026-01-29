# from datetime import date as DTdate
# from app.models import (
#     Transaction, 
#     LineItem, 
#     Deduction, 
#     User, 
#     PaymentTypeEnum, 
#     SalesCategoryEnum
#     )
# from app.extensions import db
# from sqlalchemy.orm import selectinload


# class FinancialReportService:
#     def __init__(
#         self,
#         *, 
#         start_date: DTdate, 
#         end_date: DTdate = None, 
#         location_id: int | list[int] = None, 
#         user_ids: int | list[int] = None,
#         report_type: str = "operations",
#         subject: User | None = None
#         ):
#         self.start_date = start_date
#         self.end_date = end_date or start_date
#         if location_id is not None:
#             if isinstance(location_id, int):
#                 self.location_id = [location_id]
#             elif isinstance(location_id, list):
#                 self.location_id = location_id
#             else:
#                 raise ValueError("location_id must be int or list[int]")
#         else:
#             self.location_id = []
#         if user_ids is not None:
#             if isinstance(user_ids, int):
#                 self.user_ids = [user_ids]
#             elif isinstance(user_ids, list):
#                 self.user_ids = user_ids
#             else:
#                 raise ValueError("user_id must be int or list[int]")
#         else:
#             self.user_ids = []
            
#         self.report_type = report_type
#         self.subject=subject
        
#         #Data storage
#         self.line_items = []
#         self.deductions = []
        
#         self.report = {}
        
        
#     #-------------------------
#     # Fetch data
#     #-------------------------
#     def fetch(self):
#         # Master report has no filters
#         tx_query = db.session.query(Transaction).options(selectinload(Transaction.line_items)).filter(
#             Transaction.posted_date.between(self.start_date, self.end_date)
#         )

#         # ---------------------
#         # Apply filters for transactions
#         # ---------------------
#         if self.report_type in ["user_eod", "multi_user"] and self.user_ids:
#             tx_query = tx_query.filter(Transaction.user_id.in_(self.user_ids))
#         elif self.report_type in ["location", "multi_location"] and self.location_id:
#             if isinstance(self.location_id, list):
#                 tx_query = tx_query.filter(Transaction.location_id.in_(self.location_id))
#             else:
#                 tx_query = tx_query.filter(Transaction.location_id == self.location_id)

#         # Get all line items directly
#         self.line_items = [li for tx in tx_query.all() for li in tx.line_items]

#         # ---------------------
#         # Fetch deductions
#         # ---------------------
#         ded_query = db.session.query(Deduction).filter(
#             Deduction.date.between(self.start_date, self.end_date)
#         )

#         # User filter always takes priority
#         if self.report_type in ["user_eod", "multi_user"] and self.user_ids:
#             ded_query = ded_query.filter(Deduction.user_id.in_(self.user_ids))

#         # Location filter (only if no user_ids)
#         elif self.location_id:
#             ded_query = ded_query.join(Deduction.user)
#             if isinstance(self.location_id, list):
#                 ded_query = ded_query.filter(User.location_id.in_(self.location_id))
#             else:
#                 ded_query = ded_query.filter(User.location_id == self.location_id)

#         self.deductions = ded_query.all()

        
        
    
#     #-------------------------
#     # Build report
#     #-------------------------
#     def build(self):
#         categories = {
#             str(cat): {"subtotal": 0, "tax": 0, "total": 0}
#             for cat in SalesCategoryEnum
#         }
#         payments = {
#             str(p): {"subtotal": 0, "tax": 0, "total": 0}
#             for p in PaymentTypeEnum
#         }
        
#         grand = {"subtotal": 0, "tax": 0, "total": 0}
        
#         #aggregate line items
#         for li in self.line_items:
#             sign = -1 if li.is_return else 1
            
#             subtotal = sign * (li.unit_price or 0)
#             tax = sign * (li.tax_amount or 0)
#             total = subtotal + tax if li.taxable else subtotal
            
#             category = str(li.category)
#             payment = str(li.payment_type)
            
#             categories[category]["subtotal"] += subtotal
#             categories[category]["tax"] += tax
#             categories[category]["total"] += total
            
#             payments[payment]["subtotal"] += subtotal
#             payments[payment]["tax"] += tax
#             payments[payment]["total"] += total
            
#             grand["subtotal"] += subtotal
#             grand["tax"] += tax
#             grand["total"] += total
        
        
#         #store report
#         self.report = {
#             "grand": grand,
#             "categories": categories,
#             "payments": payments,
#             "deductions": sum(d.amount for d in self.deductions),
#             "line_item_count": len(self.line_items)
#         }
        
        
#         return self.report
    
#     #-------------------------
#     # Apply Deductions
#     #-------------------------
#     def apply_deductions(self):
#         total_deductions = self.report["deductions"]
        
#         if "cash" in self.report["payments"]:
#             self.report["payments"]["cash"]["total"] -= total_deductions
        
#         self.report["grand"]["total"] -= total_deductions
        
        
        
#     #-------------------------
#     # Validation
#     #-------------------------
#     def validate(self):
#         cat_total = sum(v["total"] for v in self.report["categories"].values()) 
#         pay_total = sum(v["total"] for v in self.report["payments"].values()) 
        
#         if cat_total != pay_total:
#             raise ValueError(f"Mismatch: categories={cat_total}, payments={pay_total}")
        
        
#     #-------------------------
#     # Serialize
#     #-------------------------
#     def serialize(self):
#         if self.report_type in ["user_eod", "multi_user"] and self.subject:
#             self.report["user"] = {
#                 "id": self.subject.id,
#                 "first_name": self.subject.first_name,
#                 "last_name": self.subject.last_name,
#                 "location": self.subject.location.name if self.subject.location else None,
#                 "department": str(self.subject.department)
#             }
#         if self.report_type in ["location", "multi_location"]:
#             if isinstance(self.location_id, int):
#                 self.report["location"] = self.location_id
#             else:
#                 self.report["locations"] = self.location_id
        
#         if self.start_date == self.end_date:
#             self.report["date"] = self.start_date.isoformat()
#         else:
#             self.report["start_date"] = self.start_date.isoformat()
#             self.report["end_date"] = self.end_date.isoformat()
        
#         return self.report
    
    
#     #-------------------------
#     # Public API
#     #-------------------------
#     def generate(self):
#         self.fetch()
#         self.build()
#         print("Before Deductions: ", self.report["payments"]["cash"]["total"], self.report["grand"]["total"])
#         self.validate()
#         self.apply_deductions()
#         print("After deductions:", self.report["payments"]["cash"]["total"], self.report["grand"]["total"])
#         return self.serialize()
    
    
    