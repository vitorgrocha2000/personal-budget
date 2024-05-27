from data.tables.supabase_access import SupabaseAccess

class AccessProduct(SupabaseAccess):
    def __init__(self):
        super().__init__("product")