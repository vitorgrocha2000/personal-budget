from data.tables.supabase_access import SupabaseAccess

class AccessAccount(SupabaseAccess):
    def __init__(self):
        super().__init__("account")

