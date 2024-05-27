from dash import html, dcc
from dash.dependencies import Input, Output, State
from datetime import date, datetime, timedelta
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from app import app
import locale

from data.loader import NAMES_DICT

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
# locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')

card_icon = {
    'color': 'white',
    'textAlign': 'center',
    'font-size': 30,
    'margin': 'auto',
}

graph_margin = dict(l=10, r=10, t=25, b=0, pad=2)

# =========  Layout  =========== #
layout = dbc.Col([
    dbc.Row([
        # Saldo Total
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend(NAMES_DICT['BALANCE_TITLE'],
                                style={'font-size': '1.3rem', 'color': 'black'}),
                    html.H5(f"{NAMES_DICT['CURRENCY']} 9.300,00", id="value-saldo-dashboards",
                            style={'font-size': '1.2rem'})
                ], style={'padding-left': '20px', 'padding-top': '10px', 'margin-right': 0}),

                dbc.Card(
                    html.Div(className='fa fa-balance-scale', style=card_icon),
                    color='warning',
                    style={'max-width': 75, 'height': 90},
                )
            ])
        ], width=4),
        # Receita
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend(NAMES_DICT['REVENUES_TITLE'],
                                style={'font-size': '1.3rem', 'color': 'black'}),
                    html.H5(f"{NAMES_DICT['CURRENCY']} 15.000,00",
                            id='value-receita-dashboards', style={'font-size': '1.2rem'})
                ], style={'padding-left': '20px', 'padding-top': '10px', 'margin-right': 0}),

                dbc.Card(
                    html.Div(className='fa fa-smile-o', style=card_icon),
                    color='success',
                    style={'max-width': 75, 'height': 90},
                )
            ])
        ], width=4),
        # Despesa
        dbc.Col([
            dbc.CardGroup([
                dbc.Card([
                    html.Legend(NAMES_DICT['EXPENSES_TITLE'],
                                style={'font-size': '1.3rem', 'color': 'black'}),
                    html.H5(f"{NAMES_DICT['CURRENCY']} 5.700,00",
                            id='value-despesas-dashboards', style={'font-size': '1.2rem'})
                ], style={'padding-left': '20px', 'padding-top': '10px', 'margin-right': 0}),

                dbc.Card(
                    html.Div(className='fa fa-meh-o', style=card_icon),
                    color='danger',
                    style={'max-width': 75, 'height': 90},
                )
            ])
        ], width=4)
    ], style={"margin": "10px"}),

    dbc.Row([
        dbc.Col([
            dbc.Card([

                html.Legend(NAMES_DICT['FILTER_COMPONENT_TITLE'], className="card-title"),

                html.Label(NAMES_DICT['FILTER_COMPONENT_CATEGORIES_REVENUE'],),
                html.Div(
                    dcc.Dropdown(
                        id="dropdown-receita",
                        clearable=False,
                        style={"width": "100%"},
                        persistence=True,
                        persistence_type="session",
                        multi=True)
                ),

                html.Label(NAMES_DICT['FILTER_COMPONENT_CATEGORIES_EXPENSES'],
                           style={"margin-top": "10px"}),
                dcc.Dropdown(
                    id="dropdown-despesa",
                    clearable=False,
                    style={"width": "100%"},
                    persistence=True,
                    persistence_type="session",
                    multi=True
                ),
                html.Legend(NAMES_DICT['FILTER_COMPONENT_DATE_TITLE'], style={
                    "margin-top": "10px"}),
                dcc.DatePickerRange(
                    month_format=NAMES_DICT['DATE_FORMAT'],  # como formato para dia mes ano em portugues = 'dia/mês/ano'
                    end_date_placeholder_text=NAMES_DICT['FILTER_COMPONENT_DATE_PLACEHOLDER'],
                    start_date=datetime.today() - timedelta(days=365),
                    end_date=datetime.today(),
                    updatemode='singledate',
                    id='date-picker-config')

            ], style={"height": "100%", "padding": "20px"})
        ], width=12),

    ], style={"margin": "10px"}),
    
    dbc.Row([
        dbc.Col(dbc.Card(dcc.Graph(id="graph1",
                                   config={
                                       "displayModeBar": True,
                                       "displaylogo": False,
                                       "modeBarButtonsToRemove": ["pan2d", "lasso2d"]
                                   }), style={"padding": "15px", }), width=12),
        ], style={"margin": "10px"}),  

    dbc.Row([
            dbc.Col(dbc.Card(dcc.Graph(id="graph2", config={'displayModeBar': False}),
                    style={"padding": "10px"}), width=6),
            dbc.Col(dbc.Card(dcc.Graph(id="graph3", config={'displayModeBar': False}),
                    style={"padding": "10px"}), width=3),
            dbc.Col(dbc.Card(dcc.Graph(id="graph4", config={'displayModeBar': False}),
                    style={"padding": "10px"}), width=3),
            ], style={"margin": "10px"})

])


# =========  Callbacks  =========== #
## Dropdown Receita e também card de receita total
@app.callback([Output("dropdown-receita", "options"),
               Output("dropdown-receita", "value"),
               Output("value-receita-dashboards", "children")],
              Input("store-revenues", "data"))
def manage_dropdown_receitas(data):
    df_dropdown_receitas = pd.DataFrame(data)
    if not df_dropdown_receitas.empty:
        valor_receita_total = df_dropdown_receitas['value'].sum()
        dropdown_marks = df_dropdown_receitas['category'].unique().tolist()
    else:
        valor_receita_total = 0
        dropdown_marks = []
        df_dropdown_receitas = pd.DataFrame(columns=['category'])

    return [([{"label": x, "value": x} for x in df_dropdown_receitas['category'].unique()]), dropdown_marks, locale.format_string("€ %.2f", valor_receita_total, grouping=True)]

## Dropdown Despesa e também card de despesa total

@app.callback([Output("dropdown-despesa", "options"),
               Output("dropdown-despesa", "value"),
               Output("value-despesas-dashboards", "children")],
              Input("store-expenses", "data"))
def manage_dropdown_despesas(data):
    df_dropdown_despesas = pd.DataFrame(data)
    if not df_dropdown_despesas.empty:
        valor_despesa_total = df_dropdown_despesas['value'].sum()
        dropdown_marks = df_dropdown_despesas['category'].unique().tolist()
    else:
        valor_despesa_total = 0
        dropdown_marks = []
        df_dropdown_despesas = pd.DataFrame(columns=['category'])

    return [([{"label": x, "value": x} for x in df_dropdown_despesas['category'].unique()]), dropdown_marks, locale.format_string("€ %.2f", valor_despesa_total, grouping=True)]

## Card de valor total subtraindo as despesas das receitas

@app.callback(
    Output("value-saldo-dashboards", "children"),
    [Input("store-expenses", "data"),
     Input("store-revenues", "data")])
def saldo_total(despesas, receitas):
    valor_despesas = pd.DataFrame(despesas)
    valor_receitas = pd.DataFrame(receitas)
    
    if not valor_despesas.empty and not valor_receitas.empty:
        valor_despesas = valor_despesas['value'].sum()
        valor_receitas = valor_receitas['value'].sum()
    else:
        valor_despesas = 0
        valor_receitas = 0
    
    valor_saldo = valor_receitas - valor_despesas

    return locale.format_string(f"{NAMES_DICT['CURRENCY']} %.2f", valor_saldo, grouping=True)


# Gráfico 1
@app.callback(
    Output('graph1', 'figure'),
    [Input('store-expenses', 'data'),
     Input('store-revenues', 'data'),
     Input("dropdown-despesa", "value"),
     Input("dropdown-receita", "value"),
     Input('date-picker-config', 'start_date'),
     Input('date-picker-config', 'end_date')])
def atualiza_grafico1(data_despesa, data_receita, despesa, receita, start_date, end_date):
    
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)

    if not df_ds.empty and not df_rc.empty:
        df_ds = df_ds.sort_values(by="date")
        df_ds = df_ds.groupby("date").sum(numeric_only=True)
        df_rc = df_rc.sort_values(by="date")
        df_rc = df_rc.groupby("date").sum(numeric_only=True)

        df_acum = pd.merge(df_rc[['value']], df_ds[['value']], on="date", how="outer", suffixes=(
            '_revenues', '_expenses')).fillna(0).sort_values(by="date")
    

        df_acum["balance"] = df_acum["value_revenues"] - df_acum["value_expenses"]
        df_acum["accumulated"] = df_acum["balance"].cumsum()

        date_filter = (df_acum.index > start_date) & (df_acum.index <= end_date)
        df_acum = df_acum.loc[date_filter]
    else:
        df_acum = pd.DataFrame(columns=['value_revenues', 'value_expenses', 'balance', 'accumulated'])

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        name='Fluxo de Caixa',
        x=df_acum.index,
        y=df_acum['accumulated'],
        mode='lines',
        line=dict(color='rgb(0, 0, 255)', width=2,
                  smoothing=0.3, shape='spline'),
        fill='tozeroy',
        fillcolor='rgba(0, 0, 255, 0.1)',
        hovertemplate='%{y:$,.2f}',
    ))

    fig.update_layout(
        margin=graph_margin,
        height=300,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(
            tickformat="$,.2f"
        ),
        xaxis=dict(
            tickmode='auto',
            tickformat='%b %Y'
        )
    )

    return fig

## Gráfico 2 Barras das receitas e despesas por data
@app.callback(
    Output('graph2', 'figure'),
    [Input('store-revenues', 'data'),
     Input('store-expenses', 'data'),
     Input('dropdown-receita', 'value'),
     Input('dropdown-despesa', 'value'),
     Input('date-picker-config', 'start_date'),
     Input('date-picker-config', 'end_date')]
)
def atualiza_grafico2(data_receita, data_despesa, receita, despesa, start_date, end_date):
    df_ds = pd.DataFrame(data_despesa)
    df_rc = pd.DataFrame(data_receita)

    if not df_ds.empty and not df_rc.empty:
    # verifica quais categorias estão marcadas no dropdown-despesas
        df_ds = df_ds[df_ds['category'].isin(despesa)]
        df_ds = df_ds.groupby("date", as_index=False).sum(numeric_only=True)
        # verifica quais categorias estão marcadas no dropdown-receitas
        df_rc = df_rc[df_rc['category'].isin(receita)]
        df_rc = df_rc.groupby("date", as_index=False).sum(numeric_only=True)
        df_rc['Tipo'] = NAMES_DICT['REVENUES_TITLE']
        df_ds['Tipo'] = NAMES_DICT['EXPENSES_TITLE']

        # transforma o dataframa de receitas e despesas em uma tabela única unidos verticalmente
        df_final = pd.concat([df_ds, df_rc], ignore_index=True)

        date_filter = (df_final['date'] > start_date) & (
            df_final['date'] <= end_date)
        df_final = df_final.loc[date_filter]
    else:
        df_final = pd.DataFrame(columns=['date', 'value', 'Tipo'])

    fig = px.bar(df_final, x="date", y="value",
                 color='Tipo', barmode="group",
                 labels={'value': f"{NAMES_DICT['PROPERTY_VALUE']} ({NAMES_DICT['CURRENCY']})", 'date': f"{NAMES_DICT['PROPERTY_DATE']}"},
                 )

    fig.update_layout(
        margin=graph_margin, 
        height=300,
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
            ## dd/mm/yyyy
            tickformat='%m/%Y'
        )
        )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    return fig

# # Gráfico 3

@app.callback(
    Output('graph3', "figure"),
    [Input('store-revenues', 'data'),
     Input('dropdown-receita', 'value'),
     Input('date-picker-config', 'start_date'),
     Input('date-picker-config', 'end_date')]
)
def atualiza_grafico_pie_receita(data_receita, receita, start_date, end_date):
    df = pd.DataFrame(data_receita)
    if not df.empty:
        df = df[df['category'].isin(receita)]

        mask = (df['date'] > start_date) & (df['date'] <= end_date)
        df = df.loc[mask]
    else:
        df = pd.DataFrame(columns=['value', 'date', 'category', 'description', 'transaction_type'])

    fig = px.pie(df, values=df['value'], names=df["category"],
                 hole=.2)
    fig.update_traces(textposition='inside',
                      textinfo='percent+label', showlegend=False)
    fig.update_layout(title={'text': NAMES_DICT['REVENUES_TITLE']})
    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    return fig

# # Gráfico 4


@app.callback(
    Output('graph4', "figure"),
    [Input('store-expenses', 'data'),
     Input('dropdown-despesa', 'value'),
     Input('date-picker-config', 'start_date'),
     Input('date-picker-config', 'end_date')]
)
def atualiza_grafico_pie_despesa(data_despesa, despesa,  start_date, end_date):
    df = pd.DataFrame(data_despesa)
    
    if not df.empty:
        df = df[df['category'].isin(despesa)]

        mask = (df['date'] > start_date) & (df['date'] <= end_date)
        df = df.loc[mask]
    else:
        df = pd.DataFrame(columns=['value', 'date', 'category', 'description', 'transaction_type'])

    fig = px.pie(df, values=df['value'], names=df["category"], hole=.2)
    fig.update_layout(title={'text': NAMES_DICT['EXPENSES_TITLE']})
    fig.update_traces(textposition='inside',
                      textinfo='percent+label', showlegend=False)
    fig.update_layout(margin=graph_margin, height=300)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                      plot_bgcolor='rgba(0,0,0,0)')

    return fig
