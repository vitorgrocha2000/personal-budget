from datetime import datetime, date
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output   
from .modal_callback import callback_manage_category_modal

def modal_add_transaction(id: str, title: str, categories: dict, accounts):
    if categories is not None and not len(categories) == 0:
        categories_list = list(categories['name'].values())
        accounts_list = list(accounts['name'].values())
    else:
        categories_list = []
        accounts_list = []
    
    modal = dbc.Modal([
        dbc.ModalHeader(dbc.ModalTitle(f"Add {title}")),
        dbc.ModalBody([
            dbc.Row([
                dbc.Col([
                    dbc.Label('Descrição: '),
                    dbc.Input(placeholder=f"Ex.: {title.lower()}...", id=f"txt-{id}"),
                ], width=6, style={"padding-right": "20px"}),
                dbc.Col([
                    dbc.Label("Valor: "),
                    dbc.Input(placeholder="Ex.: $100.00",
                              id=f'value_{id}', value="")
                ], width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Data: "),
                    dcc.DatePickerSingle(id=f'date-{id}',
                                         min_date_allowed=date(2020, 1, 1),
                                         max_date_allowed=date(2030, 12, 31),
                                         date=datetime.today(),
                                         style={"width": "100%"}
                                         ),
                ], width=6, style={"padding-right": "20px"}),
                # dbc.Col([
                #     dbc.Label("Extras"),
                #     dbc.Checklist(
                #         options=[
                #             {"label": "Foi recebida", "value": 1},
                #             {"label": "Recorrente", "value": 2}
                #         ],
                #         value=[1],
                #         id=f"switches-input-{id}",
                #         switch=True),
                # ], width=3),
                dbc.Col([
                    dbc.Label("Categoria"),
                    dbc.Select(id=f"select_{id}",
                               options=[{"label": i, "value": i} for i in categories_list],
                               value=categories_list[0] if len(categories_list) > 0 else None), 
                ], width=3, style={"padding-right": "20px"}),
                dbc.Col([
                    dbc.Label("Conta"),
                    dbc.Select(id=f"select_account_{id}",
                               options=[{"label": i, "value": i} for i in accounts_list],
                               value=accounts_list[0] if len(accounts_list) > 0 else None),
                ], width=3)
            ], style={"margin-top": "25px"}),
            
            dbc.Row([
                dbc.Accordion([
                    dbc.AccordionItem(children=[
                        dbc.Row([
                            dbc.Col([
                                    html.Legend("Adicionar categoria", style={
                                                'color': 'green'}),
                                    dbc.Input(
                                        type="text", placeholder="Nova categoria...", id=f"input-add-{id}", value=""),
                                    html.Br(),
                                    dbc.Button(
                                        "Adicionar", className="btn btn-success", id=f"add-category-{id}", style={"margin-top": "20px"}),
                                    dbc.Popover(dbc.PopoverBody(
                                        f"Categoria Salva"), target=f"add-category-{id}", placement="right", trigger="click", delay={"show": 0, "hide": 1000}),
                                    html.Br(),
                                    html.Div(
                                        id=f"category-div-add-{id}", style={}),
                                    ], width=6, style={'padding-right': '20px'}),
                            dbc.Col([
                                    html.Legend("Excluir categorias", style={
                                                'color': 'red'}),
                                    dbc.Checklist(
                                        id=f"checklist-selected-style-{id}",
                                        options=[{"label": i, "value": i}
                                                for i in categories_list],
                                        value=[],
                                        label_checked_style={
                                            "color": "red"},
                                        input_checked_style={"backgroundColor": "#fa7268",
                                                                "borderColor": "#ea6258"},
                                    ),
                                    dbc.Button(
                                        "Remover", color="warning", id=f"remove-category-{id}", style={"margin-top": "20px"}),
                                    ], width=6),
                        ])
                    ], title="Adicionar/Remover Categorias")
                ], flush=True, start_collapsed=True, id=f'accordion-{id}'),
                
                html.Div(id=f"id_teste_{id}", style={
                    "padding-top": "20px"}),
                
                dbc.ModalFooter([
                    dbc.Button(
                        f"Adicionar {title}",
                        id=f"save_{id}",
                        color="success" if id == "revenue" else "danger"
                    ),
                    dbc.Popover(dbc.PopoverBody(
                        f"{title} Salva"), target=f"save_{id}", placement="left", trigger="click", persistence=False),
                ])
                
            ], style={"margin-top": "25px"})
        ])
    ],
        style={"background-color": "rgba(17, 140, 79, 0.05)"},
        id=f'modal-new-{id}',
        size="lg",
        is_open=False,
        centered=True,
        backdrop=True)
    return modal

## Add/Remove categoria revenue/expense
callback_manage_category_modal('revenue')
callback_manage_category_modal('expense')