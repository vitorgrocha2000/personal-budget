from data.tables.supabase_access import SupabaseAccess

class AccessTransaction(SupabaseAccess):
    def __init__(self):
        super().__init__("transaction")