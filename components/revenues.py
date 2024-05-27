import dash_ag_grid as dag
from dash import html, dcc, callback_context, exceptions
from dash.dependencies import Input, Output, State
from dash.dash_table import FormatTemplate
from dash.dash_table.Format import Group, Format, Scheme, Sign, Symbol
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

from data.loader import NAMES_DICT
from data.tables import AccessCategory, AccessTransaction, AccessAccount

from app import app

# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        html.Legend(NAMES_DICT['TABLE_REVENUES_TITLE']),
        html.Div(id="table-revenues"),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(
                id='bar-graph-revenues', style={"margin-right": "20px"}, config={'displayModeBar': False}),
        ], width=9),

        dbc.Col([
            dbc.Card(
                dbc.CardBody([
                    html.H4(NAMES_DICT['REVENUES_TITLE']),
                    html.Legend("€ -", id="value_revenue_card",
                                style={'font-size': '3rem'}),
                    html.H6(NAMES_DICT['REVENUES_TOTAL']),
                ], style={'text-align': 'center', 'padding-top': '30px'}))
        ], width=3),
    ], style={'align-items': 'center'}),

], style={"padding": "10px"})

# =========  Callbacks  =========== #
# Tabela

@app.callback(
    Output('table-revenues', 'children'),
    Input('store-revenues', 'data'),
    State(f'stored-cat-revenues', 'data'),
)
def create_ag_grid(data, data_cat):
    df = pd.DataFrame(data)
    df_cat = pd.DataFrame(data_cat)
    categories = df_cat['name'].to_list()    
    ## modificar o df se na coluna transaction_type_id for 1 colocar "Receita" e se for 2 colocar "Despesa"
    df['transaction_type'] = df['transaction_type_id'].apply(lambda x: NAMES_DICT['REVENUE_TITLE'] if x == 1 else NAMES_DICT['EXPENSE_TITLE'])
    
    access_account = AccessAccount()
    df_account = access_account.retrieve()
    df['account_id'] = df['account_id'].apply(lambda x: df_account[df_account['id'] == x]['name'].values[0])
        
    # Configura o AGGrid
    ag_grid = dag.AgGrid(
        id='interactivity-datatable-revenues',
        columnDefs=[
            {
                "headerName": "",
                "cellRenderer": "DeleteButton",
                "lockPosition":'left',
                "maxWidth":50,
                "filter": False,
                "cellStyle": {'textAlign': 'center', 'justifyContent': 'center', 'alignItems': 'center', 'padding': '2px'},
                "pinned": "left"
            },
            {'headerName': 'Descrição', 'field': 'description'},
            {
                'headerName': 'Data', 
                'field': 'date',
                "filter": "agDateColumnFilter",
                "sort": "desc"
            },
            {'headerName': 'Valor', 'field': 'value'},
            {'headerName': 'Categoria', 'field': 'category', "cellEditor": "agSelectCellEditor", "cellEditorParams": {"values": categories}},
            {'headerName': 'Tipo Transação', 'field': 'transaction_type', 'editable': False},
            {'headerName': 'Conta', 'field': 'account_id', "cellEditor": "agSelectCellEditor", "cellEditorParams": {"values": df_account['name'].to_list()}}
        ],
        rowData=df.to_dict('records'),
        columnSize="sizeToFit",
        defaultColDef={"filter": True, "editable": True},
        dashGridOptions={"animateRows": False},
    )
    
    return ag_grid

## callback para atualizar dados no store quando a tabela é editada
@app.callback(
    Output('store-revenues', 'data'),
    Input('interactivity-datatable-revenues', "cellValueChanged"),
    Input('interactivity-datatable-revenues', "cellRendererData"),
    State('store-revenues', 'data'),
    prevent_initial_call=True
)
def update_data_table(edited_row_data, delete_button, store_data):
    
    access_transaction = AccessTransaction()
    df_revenues = pd.DataFrame(store_data)
    
    if edited_row_data is not None:
        for item in edited_row_data:
            edited_row = item['data']
            edited_row.pop('transaction_type')     
            edited_revenue_row: dict = edited_row.copy()
            edited_revenue_row.pop('id')
            edited_revenue_row.pop('category')   
            response = access_transaction.update(edited_revenue_row, 'id', edited_row['id'])
            if response is None:
                return store_data        
            
            df_revenues.loc[df_revenues['id'] == edited_row['id']] = edited_row.values()
        
        data_return = df_revenues.to_dict()
        return data_return
    elif delete_button is not None:
        row_index = delete_button['rowIndex']
        item_to_delete = df_revenues.iloc[row_index]
        print(item_to_delete)
        
        response = access_transaction.delete('id', item_to_delete['id'])       
        df_revenues = df_revenues.drop(df_revenues.index[row_index])
        
        data_return = df_revenues.to_dict()
        return data_return
    else:
        return store_data


# Bar Graph
@app.callback(
    Output('bar-graph-revenues', 'figure'),
    [Input('store-revenues', 'data')]
)
def bar_chart(data):
    df = pd.DataFrame(data)
    df.rename(columns={
        'value': 'Valor',
        'date': 'Data',
        'description': 'Descrição',
        'transaction_type_id': 'Tipo Transação',
        'category_id': 'ID da Categoria',
        'account_id': 'ID da Conta',
        'category': 'Categoria'
    }, inplace=True)
    
    df_grouped = df.groupby("Categoria").sum()[["Valor"]].reset_index()
    graph = px.bar(df_grouped, x='Categoria', y='Valor', title=NAMES_DICT['BAR_GRAPH_TITLE'],
                   color='Categoria',
                   labels={'Valor': f"Valor ({NAMES_DICT['CURRENCY']})", 'Categoria': 'Categoria'},
                   width=1000,
                   )

    # Atualiza o layout
    graph.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Categoria",
        yaxis_title=f"Valor",
        yaxis=dict(
            tickprefix=f"{NAMES_DICT['CURRENCY']} ",  # Prefixo para o eixo Y
            title_font=dict(
                size=16,
                color='black',
            ),
        ),
        xaxis=dict(
            title_font=dict(
                size=16,
                color='black',
            ),
        )
    )

    return graph


# Simple card


@app.callback(
    Output('value_revenue_card', 'children'),
    Input('store-revenues', 'data')
)
def display_desp(data):
    df = pd.DataFrame(data)
    value = df['value'].sum()

    return f"€ {value:.2f}"
