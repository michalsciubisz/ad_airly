import dash
from dash import dcc, html, callback
from dash.dependencies import Input, Output
from datetime import date, timedelta, datetime
from database import db, DustMeasurements, GasMeasurements, Location

dash.register_page(__name__)

# Zdefiniowanie daty
today = date.today()

# Utworzenie layoutu
layout = html.Div([
    html.Div([
        html.H1('Air Quality Dashboards',
                style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '0', 'fontSize': '20px'}),

        dcc.Interval(
            id='interval-component',
            interval=60 * 1000,  # Update co 60 sekund
            n_intervals=0
        ),

        html.Div([
            html.Label('City', style={'fontWeight': 'bold', 'color': '#FFFFFF', 'marginRight': '10px'}),
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
                value='',
                multi=True,
                style={'min-width': '150px'}
            ),
            html.Label('Date Range',
                       style={'fontWeight': 'bold', 'color': '#FFFFFF', 'marginRight': '10px', 'marginLeft': '20px'}),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=today,
                end_date=today,
                style={'display': 'inline-block'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'backgroundColor': '#1A1A1A',
                  'padding': '10px'}),
    ], style={'marginBottom': '10px'}),

    html.Div([
        html.Div([
            html.H3(style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='pm10_graph', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'}),

        html.Div([
            html.H3(style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='pm25_graph', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'}),
    ], style={'display': 'flex'}),

    html.Div([
        html.Div([
            html.H3(style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='co_graph', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'}),

        html.Div([
            html.H3(style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='no2_graph', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'}),

        html.Div([
            html.H3(style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='so2_graph', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'})
    ], style={'display': 'flex'}),

], style={'maxWidth': '1800px', 'margin': 'auto', 'backgroundColor': '#1A1A1A', 'padding': '10px',
          'borderRadius': '10px'})


# Callbacks to update graphs
@callback(
    [Output('pm10_graph', 'figure'),
     Output('pm25_graph', 'figure'),
     Output('co_graph', 'figure'),
     Output('no2_graph', 'figure'),
     Output('so2_graph', 'figure')],
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
        )
    else:
        empty_fig = {'data': [], 'layout': {}}
        return (
            empty_fig,  # pm10_graph
            empty_fig,  # pm25_graph
            empty_fig,  # co_graph
            empty_fig,  # no2_graph
            empty_fig,  # so2_graph
        )


dark_layout = dict(
    plot_bgcolor='#2E2E2E',  # Ciemne szare tło dla wykresów
    paper_bgcolor='#2E2E2E',  # Bardzo ciemne tło dla ogólnego tła
    font=dict(color='#FFFFFF'),  # Biały kolor czcionki
    margin=dict(t=50, b=10, l=10, r=10),  # Małe marginesy
)

# Function to update graphs
def update_graphs(cities, start_date, end_date):
    figures = {'pm10': [], 'pm25': [], 'co': [], 'no2': [], 'so2': []}

    for city in cities:
        location = Location.query.filter_by(city=city).first()
        if not location:
            continue
        loc_id = location.id

        pm_data = db.session.query(DustMeasurements.timestamp, DustMeasurements.pm10, DustMeasurements.pm25) \
            .filter(DustMeasurements.location_id == loc_id) \
            .filter(DustMeasurements.timestamp >= start_date) \
            .filter(DustMeasurements.timestamp <= end_date) \
            .group_by(DustMeasurements.timestamp) \
            .order_by(DustMeasurements.timestamp.desc()) \
            .all()

        figures['pm10'].append({'x': [entry.timestamp for entry in pm_data], 'y': [entry.pm10 for entry in pm_data], 'type': 'scatter', 'name': f'PM10 - {city}'})
        figures['pm25'].append({'x': [entry.timestamp for entry in pm_data], 'y': [entry.pm25 for entry in pm_data], 'type': 'scatter', 'name': f'PM2.5 - {city}'})

        gas_data = db.session.query(GasMeasurements.timestamp, GasMeasurements.co, GasMeasurements.no2, GasMeasurements.so2) \
            .filter(GasMeasurements.location_id == loc_id) \
            .filter(GasMeasurements.timestamp >= start_date) \
            .filter(GasMeasurements.timestamp <= end_date) \
            .group_by(GasMeasurements.timestamp) \
            .order_by(GasMeasurements.timestamp.desc()) \
            .all()

        figures['co'].append({'x': [entry.timestamp for entry in gas_data], 'y': [entry.co for entry in gas_data], 'type': 'scatter', 'name': f'CO - {city}'})
        figures['no2'].append({'x': [entry.timestamp for entry in gas_data], 'y': [entry.no2 for entry in gas_data], 'type': 'scatter', 'name': f'NO2 - {city}'})
        figures['so2'].append({'x': [entry.timestamp for entry in gas_data], 'y': [entry.so2 for entry in gas_data], 'type': 'scatter', 'name': f'SO2 - {city}'})

    pm10_fig = {
        'data': figures['pm10'],
        'layout': {'title': 'PM10 Trends',
                   'plot_bgcolor': '#2E2E2E',
                   'paper_bgcolor': '#2E2E2E',
                   'font': {'color': '#FFFFFF'},
                   'xaxis': {'title': 'Timestamp'},
                   'yaxis': {'title': 'PM₁₀ value'},
                   }
    }

    pm25_fig = {
        'data': figures['pm25'],
        'layout': {'title': 'PM25 Trends',
                   'plot_bgcolor': '#2E2E2E',
                   'paper_bgcolor': '#2E2E2E',
                   'font': {'color': '#FFFFFF'},
                   'xaxis': {'title': 'Timestamp'},
                   'yaxis': {'title': 'PM₂₅ value'},
                   }
    }

    co_fig = {
        'data': figures['co'],
        'layout': {'title': 'CO Measurements',
                   'plot_bgcolor': '#2E2E2E',
                   'paper_bgcolor': '#2E2E2E',
                   'font': {'color': '#FFFFFF'},
                   'xaxis': {'title': 'Timestamp'},
                   'yaxis': {'title': 'CO value'},
                   }
    }

    no2_fig = {
        'data': figures['no2'],
        'layout': {'title': 'NO2 Measurements',
                   'plot_bgcolor': '#2E2E2E',
                   'paper_bgcolor': '#2E2E2E',
                   'font': {'color': '#FFFFFF'},
                   'xaxis': {'title': 'Timestamp'},
                   'yaxis': {'title': 'NO₂ value'},
                   }
    }

    so2_fig = {
        'data': figures['so2'],
        'layout': {'title': 'SO2 Measurements',
                   'plot_bgcolor': '#2E2E2E',
                   'paper_bgcolor': '#2E2E2E',
                   'font': {'color': '#FFFFFF'},
                   'xaxis': {'title': 'Timestamp'},
                   'yaxis': {'title': 'SO₂ value'},
                   }
    }

    return pm10_fig, pm25_fig, co_fig, no2_fig, so2_fig