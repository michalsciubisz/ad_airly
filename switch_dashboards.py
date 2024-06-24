import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Import your separate Dash apps
from dashboard_ver1 import dash_app as dashboard1
from dashboard_ver2 import dash_app as dashboard2
from dashboard_ver3 import dash_app as dashboard3

# Main Dash app for navigationz
app = dash.Dash(__name__)

# Define navigation buttons or tabs
navigation_buttons = html.Div([
    html.Button('Dashboard 1', id='btn-1', n_clicks=0, style={'marginRight': '10px'}),
    html.Button('Dashboard 2', id='btn-2', n_clicks=0, style={'marginRight': '10px'}),
    html.Button('Dashboard 3', id='btn-3', n_clicks=0, style={'marginRight': '10px'}),
])

# Layout of the main app
app.layout = html.Div([
    html.H1('Dashboard Navigation'),
    navigation_buttons,
    html.Div(id='dashboard-container')
])

# Callbacks to switch between Dashboards
@app.callback(
    Output('dashboard-container', 'children'),
    [Input('btn-1', 'n_clicks'),
     Input('btn-2', 'n_clicks'),
     Input('btn-3', 'n_clicks')]
)
def display_dashboard(btn1_clicks, btn2_clicks, btn3_clicks):
    ctx = dash.callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'btn-1':
        return dashboard1.layout
    elif button_id == 'btn-2':
        return dashboard2.layout
    elif button_id == 'btn-3':
        return dashboard3.layout
    else:
        # Default to displaying the first dashboard
        return dashboard1.layout

if __name__ == '__main__':
    app.run_server(debug=True)