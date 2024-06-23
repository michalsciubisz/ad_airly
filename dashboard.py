import dash
import plotly.graph_objs as go
from dash import dcc, html
from dash.dependencies import Input, Output
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date, timedelta, datetime
from database import app, db, DustMeasurements, GasMeasurements, AQIIndicator, Location

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard/', external_stylesheets=external_stylesheets)

# Zdefiniowanie rozłożenia wykresów
dash_app.layout = html.Div([
    html.H1('Air Quality Dashboards'),
    
    # Interval component for periodic updates
    dcc.Interval(
        id='interval-component',
        interval=60 * 1000,  # Update every 60 seconds
        n_intervals=0
    ),

    # City dropdown
    html.Div([
        dcc.Dropdown(
            id='city-dropdown',
            options=[
                {'label': 'Bydgoszcz', 'value': 'Bydgoszcz'},
                {'label': 'Kraków', 'value': 'Kraków'},
                {'label': 'Radom', 'value': 'Radom'},
                {'label': 'Gdańsk', 'value': 'Gdańsk'},
                {'label': 'Olsztyn', 'value': 'Olsztyn'},
                {'label': 'Warszawa', 'value': 'Warszawa'},
                {'label': 'Wrocław', 'value': 'Wrocław'}
            ],
            value='Kraków'
        )
    ]),
    html.Div(id='output_city'),

    # Date picker
    html.Div([
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date=date(2024, 6, 21),
            end_date_placeholder_text='Select a date!'
        )
    ]),
    html.Div(id='output_date'),
    
    # Side by side graphs
    html.Div([
        html.Div([
            html.H3('PM10 trend'),
            dcc.Graph(id='pm10_graph', style={'width': '100%', 'height': '400px'})
        ], style={'display': 'inline-block', 'width': '48%', 'padding': '1%'}),
        
        html.Div([
            html.H3('PM25 trend'),
            dcc.Graph(id='pm25_graph', style={'width': '100%', 'height': '400px'})
        ], style={'display': 'inline-block', 'width': '48%', 'padding': '1%'}),
    ]),
    
    # CO wskaźnik wykres
    html.Div([
        html.Div([
            html.H3('CO trend'),
            dcc.Graph(id='co_graph', style={'width': '100%', 'height': '400px'})
        ], style={'display': 'inline-block', 'width': '100%'})
    ]),

    # Side by side NO2 oraz SO2
    html.Div([
        html.Div([
            html.H3('NO2 trend'),
            dcc.Graph(id='no2_graph', style={'width': '100%', 'height': '400px'})
        ], style={'display': 'inline-block', 'width': '48%', 'padding': '1%'}),
        
        html.Div([
            html.H3('SO2 trend'),
            dcc.Graph(id='so2_graph', style={'width': '100%', 'height': '400px'})
        ], style={'display': 'inline-block', 'width': '48%', 'padding': '1%'}),
    ]),

], style={'maxWidth': '1800px', 'margin': 'auto'})

# Callbacks to update graphs
@dash_app.callback(
    [Output('pm10_graph', 'figure'),
     Output('pm25_graph', 'figure'),
     Output('co_graph', 'figure'),
     Output('no2_graph', 'figure'),
     Output('so2_graph', 'figure'),
     Output('output_city', 'children'),
     Output('output_date', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('city-dropdown', 'value')]
)

def update_output(n, start_date, end_date, city):
    if start_date and end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_date_adjusted = end_date + timedelta(days=1) - timedelta(seconds=1)
        graphs = update_graphs(city, start_date, end_date_adjusted)
        return (
            graphs[0],  # pm10_graph
            graphs[1],  # pm25_graph
            graphs[2],  # co_graph
            graphs[3],  # no2_graph
            graphs[4],  # so2_graph
            f'City selected: {city}',
            f'You have selected from {start_date} to {end_date}'
        )
    else:
        empty_fig = {'data': [], 'layout': {}}
        return (
            empty_fig,  # pm10_graph
            empty_fig,  # pm25_graph
            {},  # co_graph (empty figure or placeholder)
            {},  # no2_graph (empty figure or placeholder)
            {},  # so2_graph (empty figure or placeholder)
            'Please select a city',  # output_city
            'Please select a date range'  # output_date
        )

# Function to update graphs
def update_graphs(city, start_date, end_date):

    location = Location.query.filter_by(city=city).first()
    if not location:
        return {}, {}, {}, {}, {}
    loc_id= location.id

    # Example: Fetch data for PM10 and PM25 trends
    pm_data = db.session.query(DustMeasurements.timestamp, DustMeasurements.pm10, DustMeasurements.pm25) \
        .filter(DustMeasurements.location_id == loc_id) \
        .filter(DustMeasurements.timestamp >= start_date) \
        .filter(DustMeasurements.timestamp <= end_date) \
        .group_by(DustMeasurements.timestamp) \
        .order_by(DustMeasurements.timestamp.desc()) \
        .all()

    pm10_fig = {
        'data': [
            {'x': [entry.timestamp for entry in pm_data], 'y': [entry.pm10 for entry in pm_data], 'type': 'scatter', 'name': 'PM10'},
        ],
        'layout': {
            'title': 'PM10 Trends'
        }
    }

    pm25_fig = {
        'data': [
            {'x': [entry.timestamp for entry in pm_data], 'y': [entry.pm25 for entry in pm_data], 'type': 'scatter', 'name': 'PM2.5'},
        ],
        'layout': {
            'title': 'PM25 Trends'
        }
    }

    # fetch data for measurments
    gas_data = db.session.query(GasMeasurements.timestamp, GasMeasurements.co, GasMeasurements.no2, GasMeasurements.so2) \
        .filter(GasMeasurements.location_id == loc_id) \
        .filter(GasMeasurements.timestamp >= start_date) \
        .filter(GasMeasurements.timestamp <= end_date) \
        .group_by(GasMeasurements.timestamp) \
        .order_by(GasMeasurements.timestamp.desc()) \
        .all()

    co_fig = {
        'data': [
            {'x': [entry.timestamp for entry in gas_data], 'y': [entry.co for entry in gas_data], 'type': 'scatter', 'name': 'CO'},
        ],
        'layout': {
            'title': 'CO Measurements'
        }
    }

    no2_fig = {
        'data': [
            {'x': [entry.timestamp for entry in gas_data], 'y': [entry.no2 for entry in gas_data], 'type': 'scatter', 'name': 'NO2'},
        ],
        'layout': {
            'title': 'NO2 Measurements'
        }
    }

    so2_fig = {
        'data': [
            {'x': [entry.timestamp for entry in gas_data], 'y': [entry.so2 for entry in gas_data], 'type': 'scatter', 'name': 'SO2'},
        ],
        'layout': {
            'title': 'SO2 Measurements'
        }
    }

    return pm10_fig, pm25_fig, co_fig, no2_fig, so2_fig

if __name__ == '__main__':
    dash_app.run_server(debug=True)