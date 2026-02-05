def register_resource(bp, url_prefix, crud):
    @bp.get(f"/{url_prefix}/<int:id>", endpoint=f"{url_prefix}_read_one")
    def get_item(id):
        return crud.get(id)
    
    
    @bp.get(f"/{url_prefix}", endpoint=f"{url_prefix}_read_all")
    def list_items():
        return crud.list()
    
    
    @bp.post(f"/{url_prefix}", endpoint=f"{url_prefix}_create")
    def create_item():
        return crud.create()
    
    
    @bp.patch(f"/{url_prefix}/<int:id>")
    def update_item(id):
        return crud.update(id)
    
    
    @bp.delete(f"/{url_prefix}/<int:id>", endpoint=f"{url_prefix}_delete")
    def delete_item(id):
        return crud.delete(id)