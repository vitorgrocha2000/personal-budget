from data.tables import AccessCategory, AccessTransaction, AccessAccount
import pandas as pd

## criação de caixinhas de memória para manipular os dados do dataframe
## ----------------------------------------------  Categorias --------------------------------------------- ##
new_category = AccessCategory()
if new_category.supabase.auth.get_user() is not None:
    df_category = new_category.retrieve()
    df_category_expenses = df_category[df_category['category_type_id'] == 2]
    list_category_expenses = df_category_expenses.to_dict()
    df_category_revenues = df_category[df_category['category_type_id'] == 1]
    list_category_revenues = df_category_revenues.to_dict()

    ## -----------------------------------------------  Transações -------------------------------------------- ##
    new_transaction = AccessTransaction()
    df_revenues = new_transaction.retrieve('transaction_type_id', '1' )
    df_revenues["date"] = pd.to_datetime(df_revenues["date"])
    df_revenues["date"] = df_revenues["date"].apply(lambda x: x.date())
    df_revenues['category'] = df_revenues['category_id'].apply(lambda x: df_category_revenues[df_category_revenues['id'] == x]['name'].values[0])
    df_revenues_aux = df_revenues.to_dict()

    df_expenses = new_transaction.retrieve('transaction_type_id', '2')
    df_expenses["date"] = pd.to_datetime(df_expenses["date"])
    df_expenses["date"] = df_expenses["date"].apply(lambda x: x.date())
    df_expenses['category'] = df_expenses['category_id'].apply(lambda x: df_category_expenses[df_category_expenses['id'] == x]['name'].values[0])
    df_expenses_aux = df_expenses.to_dict()

    new_account = AccessAccount()
    df_account = new_account.retrieve()
    list_account = df_account.to_dict()
else:
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


# new_transaction_type = Access_transaction_type()
# df_transaction_type = new_transaction.retrieve('transactionType')

# new_product = Access_product()
# df_product = new_product.retrieve('product')

# new_company = Access_company()
# df_company = new_company.retrieve('company')

# new_account_type = Access_account_type()
# df_account_type = new_account_type.retrieve('accountType')
## ----------------------------------------------  NOMES PARA OS COMPONENTES --------------------------------------------- ##
MODAL_ADD_TRANSACTION_REVENUE_TITLE = 'Receita'
MODAL_ADD_TRANSACTION_EXPENSE_TITLE = 'Despesa'
MODAL_IMPORT_STATEMENT_TITLE = 'Importar Extrato'
MODAL_IMPORT_STATEMENT_BUTTON_NAME = 'Adicionar transações'
CARD_BALANCE_NAME = 'Saldo'
CARD_REVENUE_NAME = 'Receitas'
CARD_EXPENSES_NAME = 'Despesas'

## criar um dicionario com os nomes das variaveis como key e os valores como values
NAMES_DICT = {
    'PROPERTY_DATE': 'Data',
    'PROPERTY_DESCRIPTION': 'Descrição',
    'PROPERTY_VALUE': 'Valor',
    'PROPERTY_CATEGORY': 'Categoria',
    'PROPERTY_TRANSACTION_TYPE': 'Tipo de Transação',
    'PROPERTY_ACCOUNT': 'Conta',
    'PROPERTY_BANK': 'Banco',
    'PROPERTY_STATEMENT': 'Extrato',
    'PROPERTY_FILE': 'Arquivo',
    'PROPERTY_DATE': 'Data',
    'CURRENCY': '€',
    'REVENUE_TITLE': 'Receita',
    'EXPENSE_TITLE': 'Despesa',
    'REVENUES_TITLE': 'Receitas',
    'EXPENSES_TITLE': 'Despesas',
    'SIDEBAR_STATEMENTS': 'Extratos',
    'SIDEBAR_EXPENSES_ANALYSIS': 'Analisar Despesas',
    'SIDEBAR_REVENUES_ANALYSIS': 'Analisar Receitas',
    'SIDEBAR_DASHBOARD': 'Dashboard',
    'SIDEBAR_USER_DETAILS': 'Detalhes do Usuário',
    'MODAL_IMPORT_STATEMENT_TITLE': 'Importar Extrato',
    'MODAL_IMPORT_STATEMENT_ADD_BUTTON_NAME': 'Adicionar transações',
    'MODAL_IMPORT_STATEMENT_CREATE_TEMPLATE_BUTTON_NAME': 'Criar template',
    'BALANCE_TITLE': 'Saldo',
    'FILTER_COMPONENT_TITLE': 'Filtros',
    'FILTER_COMPONENT_CATEGORIES_REVENUE': 'Categorias de Receitas',
    'FILTER_COMPONENT_CATEGORIES_EXPENSES': 'Categorias de Despesas',
    'FILTER_COMPONENT_DATE_TITLE': 'Período de Análise',
    'FILTER_COMPONENT_DATE_PLACEHOLDER': 'Data...',
    'DATE_FORMAT': 'DD/MM/YYYY',
    'TABLE_REVENUES_TITLE': 'Tabela de receitas',
    'TABLE_REVENUES_TOTAL_LABEL': 'Total de receitas',
    'TABLE_EXPENSES_TITLE': 'Tabela de despesas',
    'TABLE_EXPENSES_TOTAL_LABEL': 'Total de despesas',
    'REVENUES_TOTAL': 'Total de Receitas',
    'EXPENSES_TOTAL': 'Total de Despesas',
    'BAR_GRAPH_TITLE': 'Distribuição',
    'LABEL_SELECT': 'Selecione...',
    'LOGIN_BUTTON': 'Entrar',
    'LOGOUT_BUTTON': 'Sair',
    'MESSAGE_NO_DATA': 'Nenhum dado encontrado',
    'MESSAGE_LOADING': 'Carregando...',
    'MESSAGE_LOGIN_SUCCESS': 'Login bem-sucedido. Redirecionando...',
    'MESSAGE_LOGIN_ERROR': 'Usuário ou senha inválidos. Tente novamente.',
    'MESSAGE_LOGOUT_SUCCESS': 'Logout bem-sucedido. Redirecionando...',
    'MESSAGE_LOGOUT_ERROR': 'Falha ao fazer logout. Por favor, tente novamente.',
    'MESSAGE_LOGIN_REGISTER_QUESTION': 'Não tem uma conta? ',
    'MESSAGE_LOGIN_REGISTER_LINK': 'Registre-se',
    'MESSAGE_LOGIN_MODAL_REGISTER_TITLE': 'Criar uma conta',
    'MESSAGE_LOGIN_MODAL_REGISTER_BUTTON': 'Registrar',
    'MESSAGE_EMAIL': 'E-mail',
    'MESSAGE_PASSWORD': 'Senha',
    'MESSAGE_LOGIN_MODAL_REGISTER_PASSWORD_CONFIRM': 'Confirme a senha',
    'MESSAGE_USER_NOT_LOGGED': 'Utilizador não autenticado',
    'MESSAGE_REGISTER_SUCCESS': 'Registro bem-sucedido. Por favor, verifique seu e-mail: ',
    'MESSAGE_REGISTER_ERROR': 'Falha ao registrar. Por favor, tente novamente.',
    'MESSAGE_REGISTER_PASSWORD_ERROR': 'As senhas não coincidem. Por favor, tente novamente.',
    'MESSAGE_REGISTER_EMAIL_ERROR': 'E-mail inválido. Por favor, insira um e-mail válido.',
    'MESSAGE_REGISTER_EMPTY_FIELDS': 'Por favor, preencha todos os campos.',
    'MESSAGE_UPLOAD_STATEMENT_1': 'Arraste e solte ou ',
    'MESSAGE_UPLOAD_STATEMENT_2': 'Selecione do seu computador',
    'MESSAGE_UPLOAD_STATEMENT_CURRENCY': 'Moeda do Extrato: ',
    'MESSAGE_UPLOAD_STATEMENT_OTHERS_COLUMNS': 'Selecione outras colunas: ',
    'MESSAGE_UPLOAD_STATEMENT_BANK': 'Selecione o banco',
    'MESSAGE_UPLOAD_STATEMENT_SELECT_COLUMNS_PLACEHOLDER': 'Selecione...',
    'MESSEGE_UPLOAD_STATEMENT_NAME_BANK': 'Nome do Banco: ',
    'MESSEGE_UPLOAD_STATEMENT_REVENUE_NOTE': 'Nota de Receita: ',
    'MESSEGE_UPLOAD_STATEMENT_EXPENSE_NOTE': 'Nota de Despesa: ',
    'MESSEGE_UPLOAD_STATEMENT_SELECT_COLUMNS': 'Selecione as colunas do extrato de acordo com a tabela: ',
    'MESSAGE_UPLOAD_STATEMENT_LINES_IGNORE': 'Quantas linhas no início do CSV a serem ignoradas: ',
    'MESSAGE_UPLOAD_STATEMENT_DIRECTION_NOTE': 'Se a transação não é identificada com o valor positivo (+) e negativo (-), selecione qual a descrição que indica a direção da transação:',
    'MESSAGE_UPLOAD_STATEMENT_AG_GRID_NO_DATA': 'Sem dados para exibir, verifique se o arquivo tem linhas para serem removidas para carregar a tabela.',
    'UPLOAD_STATEMENT_OTHER_BANK': 'Outro banco',
}