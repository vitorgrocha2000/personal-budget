from dash import html, dcc
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd

from app import app
from components import expenses, revenues, sidebar, dashboards, login

from data.loader import df_revenues_aux, df_expenses_aux, list_category_revenues, list_category_expenses

from data.tables import AccessCategory, AccessTransaction, AccessAccount
# =========  Layout  =========== #
app.layout = dbc.Container(children=[
    dcc.Location(id='url_index'),  # Moved here
    dcc.Store(id='store-revenues', data=df_revenues_aux),
    dcc.Store(id="store-expenses", data=df_expenses_aux),
    dcc.Store(id='stored-cat-revenues', data=list_category_revenues),
    dcc.Store(id='stored-cat-expenses', data=list_category_expenses),
    dcc.Store(id='login-redirect-trigger'),
    dcc.Store(id='logout-redirect-trigger'),
    dbc.Row([
        html.Div(id="page-content"),
    ])
], fluid=True,)

@app.callback(
    [
        Output('page-content', 'children'),
        Output('store-revenues', 'data', allow_duplicate=True),
        Output('store-expenses', 'data', allow_duplicate=True),
        Output('stored-cat-revenues', 'data', allow_duplicate=True),
        Output('stored-cat-expenses', 'data', allow_duplicate=True),
    ], 
    [
        Input('url_index', 'pathname'), 
        Input('login-redirect-trigger', 'data'), 
        Input('logout-redirect-trigger', 'data')
    ],
    prevent_initial_call=True
)
def render_page(pathname, login_redirect_trigger, logout_redirect_trigger):
    if not login.is_authenticated():
        df_category = pd.DataFrame()
        df_category_expenses = pd.DataFrame()
        list_category_expenses = {}
        df_category_revenues = pd.DataFrame()
        list_category_revenues = {}
        df_revenues = pd.DataFrame()
        df_revenues_aux = {}
        df_expenses = pd.DataFrame()
        df_expenses_aux = {}
        df_account = pd.DataFrame()
        list_account = {}
        return login.login_layout, df_revenues_aux, df_expenses_aux, list_category_revenues, list_category_expenses
    else:
        new_category = AccessCategory()
        df_category = new_category.retrieve()
        df_category_expenses = df_category[df_category['category_type_id'] == 2]
        list_category_expenses = df_category_expenses.to_dict()
        df_category_revenues = df_category[df_category['category_type_id'] == 1]
        list_category_revenues = df_category_revenues.to_dict()
        
        new_transaction = AccessTransaction()
        df_revenues = new_transaction.retrieve('transaction_type_id', '1' )
        if not df_revenues.empty:
            df_revenues["date"] = pd.to_datetime(df_revenues["date"])
            df_revenues["date"] = df_revenues["date"].apply(lambda x: x.date())
            df_revenues['category'] = df_revenues['category_id'].apply(lambda x: df_category_revenues[df_category_revenues['id'] == x]['name'].values[0])
            df_revenues_aux = df_revenues.to_dict()
        else:
            df_revenues_aux = {}

        df_expenses = new_transaction.retrieve('transaction_type_id', '2')
        if not df_expenses.empty:      
            df_expenses["date"] = pd.to_datetime(df_expenses["date"])
            df_expenses["date"] = df_expenses["date"].apply(lambda x: x.date())
            df_expenses['category'] = df_expenses['category_id'].apply(lambda x: df_category_expenses[df_category_expenses['id'] == x]['name'].values[0])
            df_expenses_aux = df_expenses.to_dict()
        else:
            df_expenses_aux = {}

        new_account = AccessAccount()
        df_account = new_account.retrieve()
        
        if pathname == '/' or pathname == '/dashboards' or pathname is None:
            component_layout = dashboards.layout
        elif pathname == '/expenses':
            component_layout = expenses.layout
        elif pathname == '/revenues':
            component_layout = revenues.layout
        else:
            component_layout = html.Div()
            
        page_layout = dbc.Row([
                            dbc.Col([
                                sidebar.layout,
                                login.user_details,
                            ], md=2, className="sticky-sidebar"),
                            dbc.Col([
                                component_layout,
                            ], md=10, className='px-2')
                        ])

        return page_layout, df_revenues_aux, df_expenses_aux, list_category_revenues, list_category_expenses

if __name__ == '__main__':
    app.run_server(debug=True)