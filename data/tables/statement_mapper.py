from data.tables.supabase_access import SupabaseAccess

class AccessStatementMapper(SupabaseAccess):
    def __init__(self):
        super().__init__("statementMapper")