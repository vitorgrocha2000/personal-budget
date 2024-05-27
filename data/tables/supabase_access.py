import traceback
import pandas as pd
from supabase import create_client, Client
from configparser import ConfigParser
config = ConfigParser()
config.read('static/config/config.ini')
url: str = config.get('supabase','url')
key: str = config.get('supabase','key')

class SupabaseAccess:
    def __init__(self, name_table:str):
        self.supabase: Client=create_client(url,key)
        self.name_table = name_table
        
    def retrieve(self, condition=None, value_condition=None):
        if(condition !=None and value_condition!=None):
            response = self.supabase.table(self.name_table).select("*").eq(condition, value_condition).execute()
            df_data = pd.DataFrame(response.data)
            return df_data
        else:
            response = self.supabase.table(self.name_table).select("*").execute()  
            df_data = pd.DataFrame(response.data)
            return df_data
    
    def insert(self, df_data: pd.DataFrame):
        response = self.supabase.table(self.name_table).insert(df_data.to_dict(orient='records')).execute()
        return response 
    
    def update(self, updates: dict, column_name, value):
        response = self.supabase.table(self.name_table).update(updates).eq(column_name, value).execute()
        return response
    
    def delete(self, column_name, value):
        try:
            response =self.supabase.table(self.name_table).delete().eq(column_name, value).execute()
            return 200 
        except Exception as e:
            traceback.print_exc()
            print(e)
            return 400



