import base64
import pandas as pd
import io
import csv

class StatemantTransform:
    def __init__(self, contents):
        self.contents = contents
        
    def get_file_extension(self, filename):
        # Extrai a extensão do nome do arquivo
        return filename.split('.')[-1].lower()

    def decode_csv(self, content_string):
        # Decodifica o conteúdo base64 e lê o CSV
        decoded = base64.b64decode(content_string)
        return pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    def decode_excel(self, content_string, lines_to_ignore):
        # Decodifica o conteúdo base64 e lê o Excel
        decoded = base64.b64decode(content_string)
        return pd.read_excel(io.BytesIO(decoded), skiprows=lines_to_ignore)
    
    def decode_pdf(self, content_string):
        # Decodifica o conteúdo base64 e lê o PDF
        # TODO: Implementar a leitura de PDF com um mecanismo de OCR
        raise NotImplementedError("PDF decoding is not implemented yet")
    
    def get_dataframe(self, contents: str, statement_type: str, ignore_lines: int):
        if statement_type == 'csv':
            return self.decode_csv(contents)
        elif statement_type == 'xlsx' or statement_type == 'xls':
            df_contents = self.decode_excel(contents, ignore_lines)
            print(df_contents.columns)
            if str(df_contents.columns[0]).startswith('Unnamed') or str(df_contents.columns[1]).startswith('Unnamed'):
                raise ValueError('Error while removing lines: Columns are still unnamed')
            return df_contents
        elif statement_type == 'pdf':
            return self.decode_pdf(contents)
        else:
            raise NotImplementedError("File extension not supported")
    
    def transform_statement(self, statmentMapper: dict, data):
        if isinstance(data, str):
            data = self.get_dataframe(data, statmentMapper['statement_type'], statmentMapper['ignore_lines'])
        elif not isinstance(data, pd.DataFrame):
            pass  ## se não for um DataFrame, não faz nada
        
        if statmentMapper['expense_note'] not in ['', None] and statmentMapper['revenue_note'] not in ['', None]:
            revenues: pd.DataFrame = data[data[statmentMapper['transaction_type']] == statmentMapper['revenue_note']] 
            expenses: pd.DataFrame = data[data[statmentMapper['transaction_type']] == statmentMapper['expense_note']]
        else:
            revenues: pd.DataFrame = data[data[statmentMapper['transaction_value']] > 0]
            expenses: pd.DataFrame = data[data[statmentMapper['transaction_value']] < 0]
            expenses[statmentMapper['transaction_value']] = expenses[statmentMapper['transaction_value']].abs()
            
        revenues_transformed = pd.DataFrame({
            'value': revenues[statmentMapper['transaction_value']],
            'date': pd.to_datetime(revenues[statmentMapper['transaction_date']]),
            'category': 'Outros',
            'description': revenues[statmentMapper['transaction_description']],
            'transaction_type_id': 1,
        })
        
        expenses_transformed = pd.DataFrame({
            'value': expenses[statmentMapper['transaction_value']],
            'date': pd.to_datetime(expenses[statmentMapper['transaction_date']]),
            'category': 'Outros',
            'description': expenses[statmentMapper['transaction_description']],
            'transaction_type_id': 2,
        })
        
        df_transaction = pd.concat([revenues_transformed, expenses_transformed])
        df_transaction.sort_values(by='date', ascending=False, inplace=True)
        
        for column in data.columns:
            if column not in df_transaction.columns:
                df_transaction[column] = data[column]
                
        return df_transaction
        
    def new_dataframe(self, df_content: pd.DataFrame):
        df_transaction = pd.DataFrame(columns=['value', 'date', 'category', 'description', 'transaction_type'])
        
        if isinstance(df_content, pd.DataFrame) and not df_content.empty:
            df_content.dropna(axis=1, how='all', inplace=True)
            for column in df_content.columns:
                if column not in df_transaction.columns:
                    df_transaction[column] = df_content[column]
                    
        return df_transaction

