from data.tables.supabase_access import SupabaseAccess

class AccessCompany(SupabaseAccess):
    def __init__(self):
        super().__init__("company")
