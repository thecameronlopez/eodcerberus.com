from flask_login import current_user
from app.handlers.errors.domain import PermissionDenied


def _require_authenticated():
    if not current_user.is_authenticated:
        raise PermissionDenied("Authentication required.")
    
def _require_admin():
    _require_authenticated()
    if not getattr(current_user, "is_admin", False):
        raise PermissionDenied("Admin access required.")


def register_resource(
    bp,
    url_prefix,
    crud,
    *,
    require_auth=True,
    create_admin_only=False,
    write_admin_only=False,
):
    @bp.get(f"/{url_prefix}/<int:id>", endpoint=f"{url_prefix}_read_one")
    def get_item(id):
        if require_auth:
            _require_authenticated()
        return crud.get(id)
    
    
    @bp.get(f"/{url_prefix}", endpoint=f"{url_prefix}_read_all")
    def list_items():
        if require_auth:
            _require_authenticated()
        return crud.list()
    
    
    @bp.post(f"/{url_prefix}", endpoint=f"{url_prefix}_create")
    def create_item():
        if create_admin_only or write_admin_only:
            _require_admin()
        elif require_auth:
            _require_authenticated()
        return crud.create()
    
    
    @bp.patch(f"/{url_prefix}/<int:id>")
    def update_item(id):
        if write_admin_only:
            _require_admin()
        elif require_auth:
            _require_authenticated()
        return crud.update(id)
    
    
    @bp.delete(f"/{url_prefix}/<int:id>", endpoint=f"{url_prefix}_delete")
    def delete_item(id):
        if write_admin_only:
            _require_admin()
        elif require_auth:
            _require_authenticated()
        return crud.delete(id)
