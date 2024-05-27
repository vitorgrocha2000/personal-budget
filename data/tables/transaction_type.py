from data.tables.supabase_access import SupabaseAccess

class AccessTransactionType(SupabaseAccess):
    def __init__(self):
        super().__init__("transactionType")
