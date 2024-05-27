import traceback
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash import html, dcc, callback_context, exceptions, dash_table
from dash.dependencies import Input, Output, State
from data.tables import AccessStatementMapper, AccessCategory, AccessStatementType
from utils import StatemantTransform
from app import app
import dash
import pandas as pd

import yfinance as yf
from data.loader import NAMES_DICT

## Function to create a modal to import a bank statement and return the modal
def modal_import_statement(modal_id: str, modal_title: str):
    modal_import = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(modal_title), close_button=True),
        dbc.ModalBody([
            html.Div(id='div-data-import-statement', 
                children=[
                    dcc.Dropdown(options=[f"{NAMES_DICT['MESSAGE_LOADING']}"], id='select-bank', value=NAMES_DICT['MESSAGE_LOADING']),
                    dcc.Upload(id='upload-data-import-statement', contents=None, multiple=False),
                    dbc.Row([
                        dbc.Col([
                            dbc.Select(id='select-currency-statement',),
                            dcc.Dropdown(id='select-columns-statement',),
                            dag.AgGrid(id='table-data-import-statement',),
                            dcc.Dropdown(id='select-column-description',),
                            dcc.Dropdown(id='select-column-transaction-date',),
                            dcc.Dropdown(id='select-column-value',),                            
                            dcc.Dropdown(id='select-column-category',options=[],value=None,),                            
                            dcc.Dropdown(id='select-column-transaction-type',options=[],value=None,), 
                            dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_ADD_BUTTON_NAME'], id="add-statement", className="ml-auto"),
                            dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_CREATE_TEMPLATE_BUTTON_NAME'], id="add-template", className="ml-auto"),
                            dbc.Input(placeholder='Ex.: OUT ...', id='input-expense-note', value=""),
                            dbc.Input(placeholder='Ex.: IN ...', id='input-revenue-note'),
                            dbc.Input(placeholder='Ex.: Golden Bank ...', id='input-bank-name', value=""),
                            dbc.Input(placeholder='Ex.: 1', id='input-lines-ignore', value="0"),
                        ], width=12),
                    ], style={"display": "none"}),
                ]
            ),
            dcc.Store(id='temporary-contents-statement', storage_type='memory'),
        ]),
    ],
    id=modal_id, 
    )
    return modal_import

## Function to create a callback to manage the div to upload the statement and return the callback, when the statement is uploaded, the data is stored in a store and the div is replaced by a table with the data
def callback_manage_div_upload_data(id_div_data_import_statement, id_modal_import_statement, id_store_statement):
    @app.callback(
        Output(id_div_data_import_statement, 'children'),
        Output(id_modal_import_statement, 'size'),
        Input(id_store_statement, 'data'),
        State('select-columns-statement', 'value'),
    )
    def div_upload_data(data: dict, selected_columns: list):
        if data:
            if 'transactions' in data:
                if data['transactions'] is not None:
                    categories = AccessCategory()
                    list_categories = categories.retrieve()
                    list_categories = list_categories['name'].unique().tolist()
                    
                    df_combined = pd.DataFrame(data['transactions'])
                    df_combined['value'] = pd.to_numeric(df_combined['value'], errors='coerce')
                    df_combined['value'] = df_combined['value'].apply(lambda x: f'$ {x:.2f}'.replace('.', ','))
                    df_combined['date'] = df_combined['date'].replace('-', pd.NaT)
                    df_combined['date'] = pd.to_datetime(df_combined['date'], format='mixed', errors='coerce')
                    df_combined = df_combined.sort_values(by='date', ascending=False)
                    df_combined['transaction_type'] = df_combined['transaction_type_id'].apply(lambda x: NAMES_DICT['REVENUE_TITLE'] if x == 1 else NAMES_DICT['EXPENSE_TITLE'])
                    cols = df_combined.columns.tolist()
                    cols = cols[-1:] + cols[:-1]
                    df_combined = df_combined[cols]
                    default_column_defs = [
                        {
                            "headerName": "",
                            "cellRenderer": "DeleteButton",
                            "lockPosition":'left',
                            "maxWidth":50,
                            "filter": False,
                            "cellStyle": {'textAlign': 'center', 'justifyContent': 'center', 'alignItems': 'center', 'padding': '2px'},
                            "pinned": "left"
                        },
                        {'headerName': NAMES_DICT['PROPERTY_DESCRIPTION'], 'field': 'description'},
                        {
                            'headerName': NAMES_DICT['PROPERTY_DATE'], 
                            'field': 'date',
                            "filter": "agDateColumnFilter",
                            "sort": "desc",
                            "cellEditor": {"function": "DatePicker"}
                        },
                        {'headerName': NAMES_DICT['PROPERTY_VALUE'], 'field': 'value'},
                        {'headerName': NAMES_DICT['PROPERTY_CATEGORY'], 'field': 'category', "cellEditor": "agSelectCellEditor", "cellEditorParams": {"values": list_categories}},
                        {'headerName': NAMES_DICT['PROPERTY_TRANSACTION_TYPE'], 'field': 'transaction_type', 'editable': False},
                    ]
                    
                    columnDefs = default_column_defs
                    if selected_columns:
                        for column in selected_columns:
                            columnDefs.append({'headerName': column, 'field': column})            
                    
                    ag_grid = dag.AgGrid(
                        id='table-data-import-statement',
                        columnDefs=columnDefs,
                        rowData=df_combined.to_dict('records'),
                        columnSize="sizeToFit",
                        defaultColDef={"filter": True, "editable": True},
                        dashGridOptions={"animateRows": False},
                    )
                    
                    df_columns = df_combined.drop(['description', 'date', 'value', 'category', 'transaction_type', 'transaction_type_id'], axis=1)
                    
                    form = html.Div([
                        dbc.Row([
                                dbc.Col([
                                dbc.Label(NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_CURRENCY']),
                                dbc.Select(
                                    id='select-currency-statement',
                                    options=[{'label': 'Euro', 'value': 'EUR'}, {'label': 'Real', 'value': 'BRL'}, {'label': 'Dólar', 'value': 'USD'}],
                                    value='EUR',
                                ),
                            ], width=6, style={"padding-right": "20px"}),
                            dbc.Col([
                                dbc.Label(NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_OTHERS_COLUMNS']),
                                dcc.Dropdown(
                                    id='select-columns-statement',
                                    options=[{'label': col, 'value': col} for col in df_columns.columns],
                                    value=selected_columns,
                                    multi=True,
                                    placeholder=NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_SELECT_COLUMNS_PLACEHOLDER']
                                )
                            ], width=6),
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Col([
                                ag_grid
                            ], width=12),
                        ], className='mb-3'), 
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_ADD_BUTTON_NAME'], id="add-statement", className="ml-auto")   
                            ]),
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Select(
                                    id="select-bank",
                                    options=[],
                                    value=None,
                                ),
                                dcc.Upload(id='upload-data-import-statement',),
                                dcc.Dropdown(id='select-column-description',),
                                dcc.Dropdown(id='select-column-transaction-date',),
                                dcc.Dropdown(id='select-column-value',),                            
                                dcc.Dropdown(id='select-column-category',options=[],value=None,),                            
                                dcc.Dropdown(id='select-column-transaction-type',options=[],value=None,), 
                                dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_CREATE_TEMPLATE_BUTTON_NAME'], id="add-template", className="ml-auto"),
                                dbc.Input(placeholder='Ex.: OUT ...', id='input-expense-note', value=""),
                                dbc.Input(placeholder='Ex.: IN ...', id='input-revenue-note'),
                                dbc.Input(placeholder='Ex.: Golden Bank ...', id='input-bank-name', value=""),
                                dbc.Input(placeholder='Ex.: 1', id='input-lines-ignore', value="0"),
                            ], width=12),
                        ], style={"display": "none"}),
                    ])           
                                
                    return form, 'xl'
            
            ## else if the data is a transform statement, it means that the user uploaded a statement from another bank and has to select the columns to transform the statement
            elif 'transform' in data:
                if data['transform'] is not None and 'transactions' not in data:
                    try:
                        df_combined = pd.DataFrame(data['transform'])
                    except:
                        print('Error: data can not be transformed to a dataframe')
                        df_combined = pd.DataFrame()                    
                    
                    columns_values: dict = {'description': None, 'date': None, 'value': None, 'category': None, 'transaction_type': None}
                    if not df_combined.empty:
                        columns_to_select = df_combined.drop(columns_values.keys(), axis=1).columns.tolist()
                        if 'selected_columns' in data:
                            columns_values = data['selected_columns']
                        df_combined = df_combined.loc[:, list(columns_values.keys())]
                    else:
                        columns_to_select = []
                        
                    if 'input_lines_ignore' in data:
                        lines_ignore = data['input_lines_ignore']
                    else:
                        lines_ignore = 0
                        
                    if 'input_bank_name' in data:
                        input_bank_name = data['input_bank_name']
                    else:
                        input_bank_name = ""
                        
                    if 'file_type' in data:
                        file_type = data['file_type']
                        if file_type == 'pdf':
                            display_ignore_lines = "none"
                        elif file_type == 'csv':
                            display_ignore_lines = "none"
                        elif file_type == 'xlsx' or file_type == 'xls':
                            display_ignore_lines = "block"
                    else:
                        file_type = None
                        
                    df_combined = df_combined.loc[:, list(columns_values.keys())] 
                                                            
                    default_column_defs = [
                        {'headerName': NAMES_DICT['PROPERTY_DESCRIPTION'], 'field': 'description'},
                        {'headerName': NAMES_DICT['PROPERTY_DATE'], 'field': 'date'},
                        {'headerName': NAMES_DICT['PROPERTY_VALUE'], 'field': 'value'},
                        {'headerName': NAMES_DICT['PROPERTY_CATEGORY'], 'field': 'category'},
                        {'headerName': NAMES_DICT['PROPERTY_TRANSACTION_TYPE'], 'field': 'transaction_type'},
                    ]         
                    
                    ag_grid = dag.AgGrid(
                        id='table-data-import-statement',
                        columnDefs=default_column_defs,
                        rowData=df_combined.to_dict('records'),
                        columnSize="sizeToFit",
                        defaultColDef={"filter": False, "editable": False, "suppressMovable": True},
                        dashGridOptions={"animateRows": False, "overlayNoRowsTemplate": f"<span style=\"padding: 10px; \">{NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_AG_GRID_NO_DATA']}</span>"},
                        dangerously_allow_code=True
                    )

                    form = html.Div([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label(NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_CURRENCY']),                                
                                dbc.Select(
                                    id='select-currency-statement',
                                    options=[{'label': 'Euro', 'value': 'EUR'}, {'label': 'Real', 'value': 'BRL'}, {'label': 'Dólar', 'value': 'USD'}],
                                    value='EUR',
                                ),
                            ], width=6, style={"padding-right": "20px"}),
                            dbc.Col([
                                dbc.Label(NAMES_DICT['MESSEGE_UPLOAD_STATEMENT_NAME_BANK']),
                                dbc.Input(placeholder='Ex.: Golden Bank ...', id='input-bank-name', value=input_bank_name)
                            ], width=6),
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label(NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_LINES_IGNORE']),
                                dbc.Input(placeholder='Ex.: 1', id='input-lines-ignore', value=lines_ignore)
                            ], width=6, style={"padding-right": "20px", "display": display_ignore_lines}), 
                        ], className='mb-3'),  
                        dbc.Row([
                            dbc.Accordion([
                                dbc.AccordionItem(children=[
                                    dbc.Row([
                                        dbc.Col([
                                            dbc.Label(NAMES_DICT['MESSEGE_UPLOAD_STATEMENT_REVENUE_NOTE']),
                                            dbc.Input(placeholder='Ex.: IN ...', id='input-revenue-note', value="")
                                        ], width=6, style={"padding-right": "20px"}),
                                        dbc.Col([
                                            dbc.Label(NAMES_DICT['MESSEGE_UPLOAD_STATEMENT_EXPENSE_NOTE']),
                                            dbc.Input(placeholder='Ex.: OUT ...', id='input-expense-note', value="")
                                        ], width=6)
                                    ], className='mb-3'),
                                ], title=NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_DIRECTION_NOTE'])
                            ], flush=True, start_collapsed=True, id=f'accordion-{id}'),
                        ]),                                          
                        
                        dbc.Row([
                            dbc.Label(NAMES_DICT['MESSEGE_UPLOAD_STATEMENT_SELECT_COLUMNS']),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='select-column-description',
                                    options=[{'label': col, 'value': col} for col in columns_to_select],
                                    value=columns_values.get('description'),
                                    placeholder=NAMES_DICT['LABEL_SELECT']                                    
                                ),
                            ], class_name='px-1'),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='select-column-transaction-date',
                                    options=[{'label': col, 'value': col} for col in columns_to_select],
                                    value=columns_values.get('date'),
                                    placeholder=NAMES_DICT['LABEL_SELECT']                                    
                                ),
                            ], class_name='px-1'),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='select-column-value',
                                    options=[{'label': col, 'value': col} for col in columns_to_select],
                                    value=columns_values.get('value'),
                                    placeholder=NAMES_DICT['LABEL_SELECT']                                    
                                ),                            
                            ], class_name='px-1'),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='select-column-category',
                                    options=[{'label': col, 'value': col} for col in columns_to_select],
                                    value=columns_values.get('category'),
                                    placeholder=NAMES_DICT['LABEL_SELECT']                                    
                                ),                            
                            ], class_name='px-1'),
                            dbc.Col([
                                dcc.Dropdown(
                                    id='select-column-transaction-type',
                                    options=[{'label': col, 'value': col} for col in columns_to_select],
                                    value=columns_values.get('transaction_type'),
                                    placeholder=NAMES_DICT['LABEL_SELECT']                                    
                                ),                            
                            ], class_name='px-1'),
                        ], className='mb-1'),
                        
                        dbc.Row([
                            dbc.Col([
                                ag_grid
                            ], width=12),
                        ], className='mb-3'),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_CREATE_TEMPLATE_BUTTON_NAME'], id="add-template", className="ml-auto")   
                            ]),
                        ], className='mb-3'),
                                          
                        dbc.Row([
                            dbc.Col([
                                dcc.Dropdown(
                                    id="select-bank",
                                    options=[],
                                    value=None,
                                ),
                                dcc.Upload(id='upload-data-import-statement',),
                                dcc.Dropdown(id='select-columns-statement',),
                                dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_ADD_BUTTON_NAME'], id="add-statement", className="ml-auto")
                            ], width=12),
                        ], style={"display": "none"}),
                    ])
                    
                    return form, 'xl'  
                else:
                    return None, 'md'              
                
        else:
            statement_mapper = AccessStatementMapper()
            df_statement_mapper = statement_mapper.retrieve()
            if not df_statement_mapper.empty:
                banks_options = [{'label': bank, 'value': bank} for bank in df_statement_mapper['bank_name'].unique()] + [{'label': NAMES_DICT['UPLOAD_STATEMENT_OTHER_BANK'], 'value': NAMES_DICT['UPLOAD_STATEMENT_OTHER_BANK']}]
            else:
                banks_options = [] + [{'label': NAMES_DICT['UPLOAD_STATEMENT_OTHER_BANK'], 'value': NAMES_DICT['UPLOAD_STATEMENT_OTHER_BANK']}]
            upload = [
                dbc.Row([
                    dbc.Col([
                        dbc.Label(NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_BANK']),
                        dcc.Dropdown(
                            id="select-bank",
                            options=banks_options,
                            value=banks_options[0]["value"],
                        ),
                    ]),
                ], class_name="mb-3"),
                dcc.Upload(
                    id='upload-data-import-statement',
                    children=html.Div([
                        NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_1'],
                        html.A(NAMES_DICT['MESSAGE_UPLOAD_STATEMENT_2'], className="text-primary", style={
                        "text-decoration": "none", "cursor": "pointer", "font-weight": "bold"})
                    ]),
                    style={
                        'width': '100',
                        'height': '4rem',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '4%',
                        'textAlign': 'center',
                    },
                    multiple=False
                ),
                dbc.Row([
                    dbc.Col([
                        dbc.Select(id='select-currency-statement',),
                        dcc.Dropdown(id='select-columns-statement',),
                        dag.AgGrid(id='table-data-import-statement',),
                        dcc.Dropdown(id='select-column-description',),
                        dcc.Dropdown(id='select-column-transaction-date',),
                        dcc.Dropdown(id='select-column-value',),                            
                        dcc.Dropdown(id='select-column-category',options=[],value=None,),                            
                        dcc.Dropdown(id='select-column-transaction-type',options=[],value=None,),                            
                        dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_ADD_BUTTON_NAME'], id="add-statement", className="ml-auto"),
                        dbc.Button(NAMES_DICT['MODAL_IMPORT_STATEMENT_CREATE_TEMPLATE_BUTTON_NAME'], id="add-template", className="ml-auto"),
                        dbc.Input(placeholder='Ex.: OUT ...', id='input-expense-note', value=""),
                        dbc.Input(placeholder='Ex.: IN ...', id='input-revenue-note'),
                        dbc.Input(placeholder='Ex.: Golden Bank ...', id='input-bank-name', value=""),
                        dbc.Input(placeholder='Ex.: 1', id='input-lines-ignore', value="0"),
                    ], width=12),
                ], style={"display": "none"}),
            ]
            return upload, 'md'
        
    
@app.callback(
    Output('table-data-import-statement', 'columnDefs'),
    Input('select-columns-statement', 'value'),
    State('table-data-import-statement', 'columnDefs'),
    prevent_initial_call=True
)
def update_columns(selected_columns, columnDefs):
    default_columns = ['description', 'date', 'value', 'category', 'transaction_type']

    # Filtra as colunas padrão
    new_columnDefs = [col for col in columnDefs if 'field' in col and col['field'] in default_columns]

    # Adiciona as novas colunas selecionadas
    new_columns = [{'headerName': column, 'field': column} for column in selected_columns if column not in default_columns]
    new_columnDefs.extend(new_columns)
    
    # Adiciona a definição do botão de exclusão
    new_columnDefs.insert(0, {
        "headerName": "",
        "cellRenderer": "DeleteButton",
        "lockPosition":'left',
        "maxWidth":50,
        "filter": False,
        "cellStyle": {'textAlign': 'center', 'justifyContent': 'center', 'alignItems': 'center', 'padding': '2px'},
        "pinned": "left"
    })

    return new_columnDefs


## Unique callback for store the statement when it is uploaded, convert the values of the statement to the selected currency and remove the row using cellRendererData
@app.callback(
    Output('temporary-contents-statement', 'data'),
    [
        Input('upload-data-import-statement', 'contents'),
        Input('modal_import_statement_id', 'is_open'),
        Input('add-statement', 'n_clicks'),
        Input('input-lines-ignore', 'value'),
        Input('select-currency-statement', 'value'),
        Input("table-data-import-statement", "cellRendererData"),
        Input('select-column-description', 'value'),
        Input('select-column-transaction-date', 'value'),
        Input('select-column-value', 'value'),
        Input('select-column-category', 'value'),
        Input('select-column-transaction-type', 'value'),
        Input('add-template', 'n_clicks')
    ],
    [
        State('upload-data-import-statement', 'filename'),
        State('select-bank', 'value'),
        State('temporary-contents-statement', 'data'),
        State('input-expense-note', 'value'),
        State('input-revenue-note', 'value'),
        State('input-bank-name', 'value'),
    ],
    prevent_initial_call=True
)
def manage_statement_storage(contents, modal_import_statement_is_open, add_statement_button, ignore_lines, currency, cell_renderer_data, description_column, transaction_date_column, value_column, category_column, transaction_type_column, create_template, upload_filename, selected_bank, temporary_data, expense_note, revenue_note, bank_name):
    ctx = callback_context
    if not ctx.triggered:
        raise exceptions.PreventUpdate
            
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
    ## Check if the modal is open and the statement is uploaded 
    if triggered_id == 'modal_import_statement_id' and not modal_import_statement_is_open:
        return None
    elif triggered_id == 'add-statement' and add_statement_button is not None:
        return None
        
    elif triggered_id == 'upload-data-import-statement' and contents is not None:
        statement_transform = StatemantTransform(contents)
        statement_mapper = AccessStatementMapper()
        statement_type = AccessStatementType()
        
        if selected_bank == NAMES_DICT['UPLOAD_STATEMENT_OTHER_BANK']:
            file_type = statement_transform.get_file_extension(upload_filename)
            df = None
            try:
                content_type, content_string = statement_transform.contents.split(',')
                statement_transform.contents = content_string
                df = statement_transform.get_dataframe(statement_transform.contents, file_type, ignore_lines)
            except Exception as e:
                print(f'Error decoding file: {e}')
            finally:
                df_transaction = statement_transform.new_dataframe(df)
            
            if len(df_transaction) == 0:
                temporary_data = {}
                temporary_data['transform'] = df_transaction.to_dict()
                temporary_data['contents'] = statement_transform.contents
                temporary_data['file_type'] = file_type     
                print("------------------- df_transaction is empty --------------------")
                print(temporary_data)           
                return temporary_data
            else:
                temporary_data = {}
                temporary_data['transform'] = df_transaction.to_dict('records')
                temporary_data['contents'] = statement_transform.contents
                temporary_data['file_type'] = file_type
                print("------------------- df_transaction is not empty --------------------")
                print(temporary_data)
                return temporary_data
            
        elif selected_bank is not None and selected_bank != NAMES_DICT['UPLOAD_STATEMENT_OTHER_BANK']:
            mapper: pd.DataFrame = statement_mapper.retrieve('bank_name', selected_bank)
            mapper = mapper.to_dict(orient='records')[0]
            mapper['statement_type'] = statement_type.retrieve('id', mapper['statement_type_id']).iloc[0]['name']
            print(mapper)
            try:
                content_type, content_string = statement_transform.contents.split(',')
                statement_transform.contents = content_string
                df_transaction = statement_transform.transform_statement(mapper, statement_transform.contents)
            except Exception as e:
                print('Error: Statement is not for the selected bank - ' + str(e))
                return None
            return {'transactions': df_transaction.to_dict('records')}
        
    ## Convert the values of the statement to the selected currency
    elif triggered_id == 'select-currency-statement':
        if currency != 'EUR':
            if temporary_data:
                if 'transactions' in temporary_data:
                    df = pd.DataFrame(temporary_data['transactions'])
                elif 'transform' in temporary_data:
                    df = pd.DataFrame(temporary_data['transform'])
                    if len(df['date']) == 0 or len(df['value']) == 0:
                        return temporary_data
                df['date'] = pd.to_datetime(df['date'])
                start_date = df['date'].min()
                end_date = df['date'].max()
                
                from_currency = currency
                to_currency = 'EUR'
                
                exchange_rates = yf.download(f'{from_currency}{to_currency}=X', start=start_date, end=end_date)['Close']
                
                for index, transaction in df.iterrows():
                    transaction_date = transaction['date'].date()
                    exchange_rate = exchange_rates.get(str(transaction_date))
                    if exchange_rate:
                        df.at[index, 'value'] *= exchange_rate
                        
                return {'transactions': df.to_dict('records')}
            else:
                print('No data to convert')
        else:
            return temporary_data
        
    ## Remove the row using cellRendererData
    elif triggered_id == 'table-data-import-statement':
        if cell_renderer_data:
            row_index = cell_renderer_data['rowIndex']

            df = pd.DataFrame(temporary_data['transactions'])
            df = df.drop(df.index[row_index])

            return {'transactions': df.to_dict('records')}
        else:
            print('No data to delete')

        return temporary_data  
    
    elif triggered_id.startswith('select-column'):
        if temporary_data:
            df = pd.DataFrame(temporary_data['transform'])
            
            if 'contents' in temporary_data:
                contents = temporary_data['contents']
            else:
                contents = None
                
            if 'file_type' in temporary_data:
                file_type = temporary_data['file_type']
            else:
                file_type = None
            
            selected_columns = {'description': description_column, 'date': transaction_date_column, 'value': value_column, 'category': category_column, 'transaction_type': transaction_type_column}
            for column_name, column_value in selected_columns.items():
                if column_value is not None:
                    df[column_name] = df[column_value]
                
            temporary_data['transform'] = df.to_dict('records')
            temporary_data['selected_columns'] = selected_columns

            return temporary_data 
        else:
            print('No data to update')
            
    elif triggered_id == 'add-template' and create_template is not None:
        if temporary_data:
            if 'transform' in temporary_data:
                access_statement_type = AccessStatementType()
                df = pd.DataFrame(temporary_data['transform'])
                if ignore_lines:
                    ignore_lines = int(ignore_lines)
                else:
                    ignore_lines = 0
                    
                if bank_name == "":
                    return dash.no_update
                
                if 'file_type' in temporary_data:
                    file_type = temporary_data['file_type']
                
                file_type_id = access_statement_type.retrieve('name', file_type)
                new_statement_mapper = {
                    'bank_name': bank_name,
                    'transaction_date': transaction_date_column,
                    'transaction_description': description_column,
                    'transaction_value': value_column,
                    'transaction_type': transaction_type_column,
                    'revenue_note': revenue_note,
                    'expense_note': expense_note,
                    'ignore_lines': ignore_lines,    
                    'statement_type_id': file_type_id.iloc[0]['id'] if not file_type_id.empty else None,
                }
                statement_mapper = AccessStatementMapper()
                statement_mapper.insert(pd.DataFrame([new_statement_mapper]))
                statement_transform = StatemantTransform(contents)
                new_statement_mapper['statement_type'] = file_type
                print(new_statement_mapper)

                df_transaction = statement_transform.transform_statement(new_statement_mapper, df)
                return {'transactions': df_transaction.to_dict('records')}
            
    elif triggered_id == 'input-lines-ignore':
        if temporary_data:
            df = pd.DataFrame(temporary_data['transform'])
            statement_transform = StatemantTransform(temporary_data['contents'])
            
            try:
                ignore_lines = int(ignore_lines)
            except:
                ignore_lines = 0            
            if 'file_type' in temporary_data:
                file_type = temporary_data['file_type']
            else:
                file_type = statement_transform.get_file_extension(upload_filename)
                
            if ignore_lines > 0:
                try:
                    statement_transform.contents = statement_transform.get_dataframe(statement_transform.contents, file_type, ignore_lines)                        
                    df = statement_transform.new_dataframe(statement_transform.contents)
                    temporary_data['transform'] = df.to_dict('records')
                    return temporary_data
                except Exception as e:
                    traceback.print_exc()
                    print('Error: ' + str(e))
                    return dash.no_update
            else:
                return dash.no_update

        else:
            print('No data to update')
            dash.no_update
            
    else:
        print('Any trigger was activated')
        return dash.no_update        
