import pandas as pd
from app import app
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import html, dcc, dash_table, callback_context
import dash
import os

from data.loader import NAMES_DICT, list_category_revenues, list_category_expenses, list_account

## Services ##
from utils import StatemantTransform
from components import login
from .modals.modal_add_transaction import modal_add_transaction
from .modals.modal_callback import calback_add_transactions, callback_manage_category_modal, callback_open_modal
from .modals.modal_import_statement import modal_import_statement, callback_manage_div_upload_data

# ========= Layout ========= #
layout = dbc.Col([
    html.Div([
        html.H1("Personal Budget",
                className="display-5 text-primary fw-bolder mt-3"),
        html.P("By Vitor Rocha", className="text-muted fs-6"),
        html.Hr(className="my-3")
    ], style={"text-align": "center"}),

    # Section to add revenue and/or expense ----------------------------------
    dbc.Row([
        dbc.Col([
            dbc.Button(color='success', id='new-revenue',
                       children=['+ Receita'])
        ], width=6),
        dbc.Col([
            dbc.Button(color='danger', id='new-expense',
                       children=['- Despesa'])
        ], width=6)
    ], style={'text-align': 'center'}),
    # bot]ao de importar csv
    dbc.Row([
        dbc.Col([
            dbc.Button(color='primary', id='open_modal_button',
                       children=[NAMES_DICT['MODAL_IMPORT_STATEMENT_TITLE']])
        ], width=12)
    ], style={'text-align': 'center'}, className='mt-3'),

    ### Modal importar extrato ###
    modal_import_statement(
        'modal_import_statement_id', 
        NAMES_DICT['MODAL_IMPORT_STATEMENT_TITLE'], 
    ),
    
    ### Modal revenue ###
    modal_add_transaction('revenue', NAMES_DICT['REVENUE_TITLE'], list_category_revenues, list_account),   
    
    ### Modal expense ###
    modal_add_transaction('expense', NAMES_DICT['EXPENSE_TITLE'], list_category_expenses, list_account),

    # seção de navegação--------------------
    html.Hr(),
    dcc.Location(id='url', refresh=False),
    dbc.Nav([
        dbc.NavItem(dbc.NavLink(
            NAMES_DICT['SIDEBAR_DASHBOARD'], href="/dashboards", active="exact", id="dashboard-link")),
        dbc.NavItem([
            dbc.NavLink(NAMES_DICT['SIDEBAR_STATEMENTS'], id="statements-toggle", active="exact")], id="statements-link"),
        dbc.Collapse([
            dbc.NavLink(NAMES_DICT['SIDEBAR_EXPENSES_ANALYSIS'],
                        href="/expenses", active="exact", style={"marginLeft": "20px", "fontSize": "0.9em"}, id="expenses-link"),
            dbc.NavLink(NAMES_DICT['SIDEBAR_REVENUES_ANALYSIS'],
                        href="/revenues", active="exact", style={"marginLeft": "20px", "fontSize": "0.9em"}, id="revenues-link"),
        ], id="statements-collapse", is_open=False),
    ], vertical=True, id='nav-buttons', style={'margin-bottom': '50px'}),

], id='sidebar_inteira')

# =========  Callbacks  =========== #

# # Toggle statements menu collapse com o mouse hover
@app.callback(
    Output("statements-collapse", "is_open"),
    [Input("statements-toggle", "n_clicks"),
     Input('url', 'pathname')],  # Nova entrada
    [State("statements-collapse", "is_open")],
)
def toggle_collapse(n, pathname, is_open):
    ctx = dash.callback_context
    if not ctx.triggered:
        trigger_id = 'No clicks yet'
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == "statements-toggle":
        return not is_open
    elif trigger_id == 'url':
        if pathname == "/expenses" or pathname == "/revenues":
            return True
        elif pathname == "/dashboards":
            return False
    return is_open


# pintar o menu de acordo com a página atual
@app.callback(
    [Output("statements-toggle", "className"),
     Output("dashboard-link", "className"),
     Output("expenses-link", "className"),
     Output("revenues-link", "className")],
    [Input('url', 'pathname')]
)
def update_class(pathname):
    statements_class = ""
    dashboard_class = ""
    expenses_class = ""
    revenues_class = ""

    if pathname == "/dashboards" or pathname == "/":
        dashboard_class = "active-singlelink"
    elif pathname == "/expenses":
        statements_class = "active-grouplink"
        expenses_class = "active-sublink"
    elif pathname == "/revenues":
        statements_class = "active-grouplink"
        revenues_class = "active-sublink"

    return statements_class, dashboard_class, expenses_class, revenues_class

# # open/close modal importar csv
callback_open_modal("open_modal_button", "modal_import_statement_id")
# open/close modal revenue/expense
callback_open_modal("new-revenue", "modal-new-revenue")
callback_open_modal("new-expense", "modal-new-expense")


# gerenciar adicionar revenues e expenses
calback_add_transactions(
    'add-statement', 
    'save_revenue', 
    'save_expense', 
    'temporary-contents-statement', 
    'txt-revenue', 
    'value_revenue', 
    'date-revenue', 
    'select_revenue', 
    'select_account_revenue',
    'txt-expense', 
    'value_expense', 
    'date-expense', 
    'select_expense', 
    'select_account_expense',
    'store-revenues', 
    'store-expenses'
    )

callback_manage_div_upload_data(
    'div-data-import-statement', 
    'modal_import_statement_id', 
    'temporary-contents-statement',
    )
