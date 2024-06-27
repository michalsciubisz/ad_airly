import dash
from dash import dcc, html
from database import app

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, server=app, external_stylesheets=external_stylesheets, use_pages=True)

dash_app.layout = html.Div([
    html.H1('Dashboards Navigation',
                style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '0', 'fontSize': '20px'}),
    html.Div([
        html.Div(
            dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"]) # Dodanie linków do przejść między stronami
        ) for page in dash.page_registry.values()
    ]),
    dash.page_container
], style={'maxWidth': '1800px', 'margin': 'auto', 'backgroundColor': '#1A1A1A', 'padding': '10px',
          'borderRadius': '10px'})

if __name__ == '__main__':
    dash_app.run(debug=True)