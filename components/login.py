import re
from dash import html, dcc, callback_context
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import supabase
from data.loader import NAMES_DICT

from app import app

from configparser import ConfigParser
config = ConfigParser()
config.read('static/config/config.ini')
url: str = config.get('supabase','url')
key: str = config.get('supabase','key')

supabase_client = supabase.create_client(url, key)

def is_authenticated():
    try: 
        if supabase_client.auth.get_user() == None: 
            return False
        return True
    except Exception as e:
        print(e)
        return False
    
user_details = html.Div([
                    html.Hr(),
                    html.P(supabase_client.auth.get_user().user.email if supabase_client.auth.get_user() else NAMES_DICT['MESSAGE_USER_NOT_LOGGED'], id="user-email"),
                    dbc.Button(NAMES_DICT['LOGOUT_BUTTON'], id="logout-button", color="danger", className="mt-2"),
                    html.Div(id="logout-alert"),
                ], style={"text-align": "center"}, className='mt-auto')

# Layout da página de login
login_layout = dbc.Container(
    [
        html.Div([
            html.H1("Personal Budget",
                    className="display-5 text-primary fw-bolder mt-3"),
            html.P("By Vitor Rocha", className="text-muted fs-6"),
            html.Hr(className="my-3")
        ], style={"text-align": "center"}),
        dbc.Input(id="login-email", type="text", placeholder=NAMES_DICT['MESSAGE_EMAIL']),
        dbc.Input(id="login-password", type="password", placeholder=NAMES_DICT['MESSAGE_PASSWORD'], className="mt-2"),
        dbc.Button(NAMES_DICT['LOGIN_BUTTON'], id="login-button", color="primary", className="mt-3"),
        html.Div(id="login-alert", className="mt-3"),
        # local para o botão de registro
        html.Div([
            html.Hr(className="my-3"),  # Nova linha horizontal adicionada aqui
            html.P(NAMES_DICT['MESSAGE_LOGIN_REGISTER_QUESTION']),
            dbc.Button(NAMES_DICT['MESSAGE_LOGIN_REGISTER_LINK'], id="register-link", color="link")
        ], style={"text-align": "center"}),
        # Layout da página de registro
        dbc.Modal(
            [
                dbc.ModalHeader(NAMES_DICT['MESSAGE_LOGIN_MODAL_REGISTER_TITLE']),
                dbc.ModalBody(
                    [
                        dbc.Input(id="register-email", type="email", placeholder=NAMES_DICT['MESSAGE_EMAIL'], className="mt-2"),
                        dbc.Input(id="register-password", type="password", placeholder=NAMES_DICT['MESSAGE_PASSWORD'], className="mt-2"),
                        dbc.Input(id="register-password-confirm", type="password", placeholder=NAMES_DICT['MESSAGE_LOGIN_MODAL_REGISTER_PASSWORD_CONFIRM'], className="mt-2"),
                        dbc.Button(NAMES_DICT['MESSAGE_LOGIN_MODAL_REGISTER_BUTTON'], id="register-button", color="primary", className="mt-3"),
                        html.Div(id="register-alert", className="mt-3"),
                    ]
                ),
            ],
            id="register-modal",
            style={"background-color": "rgba(17, 140, 79, 0.05)"},
            size="lg",
            is_open=False,
            centered=True,
        ),
        
        dbc.Row([
            user_details,
        ], style={"display": "none"}),
    ],
    className="mt-5",
    style={"max-width": "500px"}
)

# Callback para fazer login
@app.callback(
    [
        Output("login-alert", "children"),
        Output("login-redirect-trigger", "data"),
        Output("user-email", "children"),
    ],
    [Input("login-button", "n_clicks"), Input("login-password", "n_submit")],
    [State("login-email", "value"), State("login-password", "value")]
)
def login(n_clicks, n_submit, login_email, login_password):  # Added new argument here
    if n_clicks or n_submit:
        if not all([login_email, login_password]):
            text_error: str = NAMES_DICT['MESSAGE_LOGIN_EMPTY_FIELDS']
            return html.Div(text_error, style={"color": "red", "margin-top": "10px", "margin-bottom": "10px"}), False
        
        response = supabase_client.auth.sign_in_with_password({"email": login_email, "password": login_password})
        if response.user != None:
            text_success: str = NAMES_DICT['MESSAGE_LOGIN_SUCCESS']
            return html.Div([
                text_success,         
                dcc.Loading(
                    id="loading-1",
                    type="default",
                    loading_state={"is_loading": True},
                    children=html.Div(id="loading-output-1")
                ),], style={"color": "green", "margin-top": "10px", "margin-bottom": "10px"}), True, response.user.email
        else:
            text_error: str = NAMES_DICT['MESSAGE_LOGIN_ERROR']
            return html.Div(text_error, style={"color": "red", "margin-top": "10px", "margin-bottom": "10px"}), False, NAMES_DICT['MESSAGE_USER_NOT_LOGGED']
    else:
        raise PreventUpdate
    
# Callback para registrar um novo usuário
@app.callback(
    Output("register-modal", "is_open"),
    [Input("register-link", "n_clicks")],
    [State("register-modal", "is_open")],
)
def register_modal(n_register_clicks, is_open):
    if n_register_clicks:
        return not is_open
    return is_open

# Callback para fazer o registro
def is_valid_email(email):
    """Check if the email is a valid format."""

    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+([.]\w+)+$'
    if re.match(regex, email):
        return True
    else:
        return False

@app.callback(
    Output("register-alert", "children"),
    [Input("register-button", "n_clicks"), Input("register-password", "n_key_press")],
    [State("register-email", "value"), State("register-password", "value"), State("register-password-confirm", "value")]
)
def register(n_clicks, n_key_press, user_email, user_password, user_password_confirm):
    ctx = callback_context
    if ctx.triggered:
        prop_id = ctx.triggered[0]["prop_id"]
        if prop_id == "register-button.n_clicks" or (prop_id == "register-password.n_key_press" and n_key_press == 13):
            if n_clicks:
                ## verificar se tem algum campo vazio
                if not all([user_email, user_password, user_password_confirm]):
                    text_error: str = NAMES_DICT['MESSAGE_REGISTER_EMPTY_FIELDS']
                    return html.Div(text_error, style={"color": "red", "margin-top": "10px", "margin-bottom": "10px"})
                if not is_valid_email(user_email):
                    text_error: str = NAMES_DICT['MESSAGE_REGISTER_EMAIL_ERROR']
                    return html.Div(text_error, style={"color": "red", "margin-top": "10px", "margin-bottom": "10px"})                
                if user_password != user_password_confirm:
                    text_error: str = NAMES_DICT['MESSAGE_REGISTER_PASSWORD_ERROR']
                    return html.Div(text_error, style={"color": "red", "margin-top": "10px", "margin-bottom": "10px"})               
                
                print("Email:", user_email + " - Password:", user_password)
                response = supabase_client.auth.sign_up(credentials={"email": user_email,"password": user_password,})
                if response.status_code == 200:
                    print(response)
                    # Registro bem-sucedido
                    text_success: str = NAMES_DICT['MESSAGE_REGISTER_SUCCESS'] + user_email
                    return html.Div(text_success, style={"color": "green", "margin-top": "10px", "margin-bottom": "10px"})
                else:
                    print(response)
                    # Falha no registro
                    text_error: str = NAMES_DICT['MESSAGE_REGISTER_ERROR']
                    return html.Div(text_error, style={"color": "red", "margin-top": "10px", "margin-bottom": "10px"})
            else:
                raise PreventUpdate

# Callback para fazer logout
@app.callback(
    [Output("logout-alert", "children"), Output("logout-redirect-trigger", "data")],
    [Input("logout-button", "n_clicks")],
)
def logout(n_clicks):
    if n_clicks:
        response = supabase_client.auth.sign_out()
        if response == None:
            text_success: str = NAMES_DICT['MESSAGE_LOGOUT_SUCCESS']
            return html.Div(text_success, style={"color": "green", "margin-top": "10px", "margin-bottom": "10px"}), True
        else:
            text_error: str = NAMES_DICT['MESSAGE_LOGOUT_ERROR']
            return html.Div(text_error, style={"color": "red", "margin-top": "10px", "margin-bottom": "10px"}), False
    else:
        raise PreventUpdate