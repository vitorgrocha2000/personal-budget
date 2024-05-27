from data.tables.supabase_access import SupabaseAccess


class AccessAccountType(SupabaseAccess):
    def __init__(self):
        super().__init__("accountType")