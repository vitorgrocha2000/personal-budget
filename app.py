import dash
import dash_bootstrap_components as dbc


# Lista contendo links para os estilos utilizados na aplicação
estilos = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css",
           "https://fonts.googleapis.com/icon?family=Material+Icons", dbc.themes.COSMO]

# URL do arquivo CSS da biblioteca dash_bootstrap_components
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"
# FONT_AWESOME = "https://use.fontawesome.com/releases/v5.10.2/css/all.css"


# Cria uma instância do objeto Dash, passando o nome da aplicação e a lista de estilos como argumentos
app = dash.Dash(__name__, external_stylesheets=estilos +
                [dbc_css, dbc.icons.FONT_AWESOME])


# Define uma configuração para suprimir exceções em caso de callbacks faltantes
app.config['suppress_callback_exceptions'] = True

# Define uma configuração para servir scripts localmente
app.scripts.config.serve_locally = True

# Cria uma instância do servidor Flask que será usada pelo Dash
server = app.server
