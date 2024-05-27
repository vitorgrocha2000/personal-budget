from dash.dependencies import Input, Output, State
from dash import callback_context, dash
from app import app
import pandas as pd
from data.tables import AccessCategory, AccessTransaction, AccessAccount

## Callback to manage categories in modals ##
def callback_manage_category_modal(id):
    access_category = AccessCategory()

    @app.callback(
        [
            Output(f"select_{id}", "options"),
            Output(f'checklist-selected-style-{id}', 'options'),
            Output(f'checklist-selected-style-{id}', 'value'),
            Output(f'stored-cat-{id}s', 'data'),
            Output(f"input-add-{id}", "value")
        ],
        [
            Input(f"add-category-{id}", "n_clicks"),
            Input(f"remove-category-{id}", 'n_clicks')
        ],
        [
            State(f"input-add-{id}", "value"),
            State(f'checklist-selected-style-{id}', 'value'),
            State(f'stored-cat-{id}s', 'data')
        ]
    )
    def manage_category(n, n2, txt, check_delete, categories_dict):
        if n and not (txt == "" or txt == None):
            categories = list(categories_dict["name"])
            
            if txt in categories:
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Categoria já existe"
            elif txt == "":
                return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Digite um nome para a categoria"
            access_category.insert(pd.DataFrame({'name': [txt], 'category_type_id': [1 if id == 'revenue' else 2]}))
            categories.append(txt)
            
        elif n2:
            categories = list(categories_dict["name"])
            if len(check_delete) > 0:
                for i in check_delete:
                    status_code = access_category.delete('name', i)
                    if status_code == 200:
                        categories.remove(i)
                    elif status_code == 400:
                        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, "Erro ao deletar categoria"

        else:
            categories = list(categories_dict["name"].values())
        options = [{"label": name, "value": name} for name in categories]
        data_return = {'name': categories}

        return [options, options, [], data_return, ""]
    return manage_category

## Callback to open modals ##
def callback_open_modal(id_button, id_modal):
    @app.callback(
        Output(id_modal, "is_open"),
        [Input(id_button, "n_clicks")],
        [State(id_modal, "is_open")],
    )
    def toggle_modal(n1, is_open):
        if n1:
            return not is_open
        return is_open
    return toggle_modal

# gerenciar adicionar receitas e despesas
def calback_add_transactions(
                            id_add_statement_button, 
                            id_save_revenue_button, 
                            id_save_expense_button, 
                            id_store_statement,
                            id_description_revenue,
                            id_value_revenue,
                            id_date_revenue,
                            id_select_category_revenue,
                            id_select_account_revenue,
                            id_description_expense,
                            id_value_expense,
                            id_date_expense,
                            id_select_category_expense,
                            id_select_account_expense,
                            id_store_revenues,
                            id_store_expenses
                            ):
    
    access_transaction = AccessTransaction()
    access_category = AccessCategory()
    access_account = AccessAccount()
    @app.callback(
        [
            Output(id_store_revenues, 'data', allow_duplicate=True),
            Output(id_store_expenses, 'data', allow_duplicate=True),
        ],
        [
            Input(id_add_statement_button, 'n_clicks'),
            Input(id_save_revenue_button, 'n_clicks'),
            Input(id_save_expense_button, 'n_clicks')
        ],
        [
            State(id_store_statement, 'data'),
            State(id_description_revenue, 'value'),
            State(id_value_revenue, 'value'),
            State(id_date_revenue, 'date'),
            State(id_select_category_revenue, 'value'),
            State(id_select_account_revenue, 'value'),
            State(id_description_expense, 'value'),
            State(id_value_expense, 'value'),
            State(id_date_expense, 'date'),
            State(id_select_category_expense, 'value'),
            State(id_select_account_expense, 'value'),
            State(id_store_revenues, 'data'),
            State(id_store_expenses, 'data'),
        ],
        prevent_initial_call=True
    )
    def manage_add_transactions_callback(
        add_statement_button_n_clicks,
        save_revenue_button_n_clicks,
        save_expense_button_n_clicks,
        store_statement_data,
        description_revenue_value,
        revenue_value,
        date_revenue_value,
        select_category_revenue_value,
        select_account_revenue_value,
        description_expense_value,
        expense_value,
        date_expense_value,
        select_category_expense_value,
        select_account_expense_value,
        store_revenues_data,
        store_expenses_data
    ):
        ctx = callback_context
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        df_revenues = pd.DataFrame(store_revenues_data)
        df_expenses = pd.DataFrame(store_expenses_data)
        
        if triggered_id == id_add_statement_button and store_statement_data != {} and add_statement_button_n_clicks is not None:
            df_transaction = pd.DataFrame(store_statement_data['transactions'])
            revenues_transformed = df_transaction[df_transaction['transaction_type_id'] == 1]
            expenses_transformed = df_transaction[df_transaction['transaction_type_id'] == 2]
            print(df_transaction)

            ## TODO: insert in database
            ## access_transaction.insert('transaction', revenues_transformed)
            ## access_transaction.insert('transaction', expenses_transformed)
            df_revenues_new = pd.concat([df_revenues, revenues_transformed])
            df_expenses_new = pd.concat([df_expenses, expenses_transformed])
            
            return df_revenues_new.to_dict(), df_expenses_new.to_dict()

        
        elif triggered_id == id_save_revenue_button and save_revenue_button_n_clicks is not None:
            if not (revenue_value == "" or revenue_value is None):
                select_category_revenue_value = select_category_revenue_value[0] if type(
                    select_category_revenue_value) == list else select_category_revenue_value
                select_account_revenue_value = select_account_revenue_value[0] if type(
                    select_account_revenue_value) == list else select_account_revenue_value
                                
                category_obj = access_category.retrieve("name", select_category_revenue_value)
                
                new_row = [{
                    'value': round(float(revenue_value), 2),
                    'date': pd.to_datetime(date_revenue_value),
                    'description': description_revenue_value,
                    'transaction_type_id': 1,
                    'category_id': category_obj['id'].values[0] if not category_obj.empty else None,
                    'account_id': access_account.retrieve("name", select_account_revenue_value)['id'].values[0],
                    'user_id': access_account.supabase.auth.get_user().user.id
                }]
                

                df_new_row = pd.DataFrame(new_row)
                df_new_row['date'] = df_new_row['date'].astype(str)
                response = access_transaction.insert(df_new_row)

                new_row[0]['category'] = category_obj['name'].values[0] if not category_obj.empty else None
                new_row[0]['date'] = pd.to_datetime(new_row[0]['date'])
                df_revenues = pd.concat([df_revenues, pd.DataFrame(new_row)], ignore_index=True)

                data_return = df_revenues.to_dict()
                return data_return, dash.no_update
        elif triggered_id == id_save_expense_button and save_expense_button_n_clicks is not None:
            if not (expense_value == "" or expense_value is None):
                select_category_expense_value = select_category_expense_value[0] if type(
                    select_category_expense_value) == list else select_category_expense_value
                select_account_expense_value = select_account_expense_value[0] if type(
                    select_account_expense_value) == list else select_account_expense_value
                
                category_obj = access_category.retrieve("name", select_category_expense_value)

                new_row = [{
                    'value': round(float(expense_value), 2),
                    'date': pd.to_datetime(date_expense_value),
                    'description': description_expense_value,
                    'transaction_type_id': 2,
                    'category_id': category_obj['id'].values[0] if not category_obj.empty else None,
                    'account_id': access_account.retrieve("name", select_account_expense_value)['id'].values[0],
                    'user_id': access_account.supabase.auth.get_user().user.id
                }]

                df_new_row = pd.DataFrame(new_row)
                df_new_row['date'] = df_new_row['date'].astype(str)
                access_transaction.insert(df_new_row)
                
                new_row[0]['category'] = category_obj['name'].values[0] if not category_obj.empty else None
                df_expenses = pd.concat([df_expenses, pd.DataFrame(new_row)], ignore_index=True)

                data_return = df_expenses.to_dict()
                return dash.no_update, data_return
        else:
            return dash.no_update, dash.no_update
        
    return manage_add_transactions_callback
