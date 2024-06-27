import dash
from dash import dcc, html
from database import app

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, server=app, external_stylesheets=external_stylesheets, use_pages=True)

button_style = {
    'padding': '15px 30px',  
    'margin': '10px', 
    'textAlign': 'center',  
    'textDecoration': 'none',  
    'color': 'black', 
    'fontWeight': 'bold',  
    'borderRadius': '5px',  
    'border': '2px solid #008CBA',  
    'backgroundColor': '#FFFFFF',  
    'display': 'inline-block' 
}

dash_app.layout = html.Div([
    html.H1('Dashboards Navigation',
                style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '0', 'fontSize': '20px'}),
    html.Div([
        html.Div(
             dcc.Link(f"{page['name']}", href=page["relative_path"], style=button_style) # Dodanie linków do przejść między stronami
        ) for page in dash.page_registry.values()
    ], style={'display': 'flex', 'justifyContent': 'center', 'alignItems': 'center'}),
    dash.page_container
], style={'maxWidth': '1800px', 'margin': 'auto', 'backgroundColor': '#1A1A1A', 'padding': '10px',
          'borderRadius': '10px'})

if __name__ == '__main__':
    dash_app.run(debug=True)