from data.tables.supabase_access import SupabaseAccess

class AccessStatementType(SupabaseAccess):
    def __init__(self):
        super().__init__("statementType")