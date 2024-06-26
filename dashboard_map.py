import dash
import dash_leaflet as dl
from dash import dcc, html
from dash.dependencies import Input, Output
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date, timedelta, datetime
from database import app, db, DustMeasurements, GasMeasurements, AQIIndicator, Location

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/contamination_map/', external_stylesheets=external_stylesheets)

# Define the layout of the Dash app
dash_app.layout = html.Div([
    html.H1('Air Contamination Map', style={'text-align': 'center'}),

    html.Div([
        html.Div([
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=date(2024, 6, 21),
                end_date_placeholder_text='Select a date!'
            ),
            html.Div(id='output_date', style={'text-align': 'center', 'margin-bottom': '10px'})
        ], style={'position': 'absolute', 'top': '90px', 'left': '50%', 'transform': 'translateX(-50%)', 'background-color': 'white', 'padding': '10px', 'border-radius': '5px', 'z-index': '1000'}),

        # Centering the map container
        html.Div([
            dl.Map(style={'width': '100%', 'height': '700px'}, center=[52, 19], zoom=6, children=[
                dl.TileLayer(),
                dl.LayerGroup(id='layer')
            ])
        ], style={'position': 'relative', 'width': '100%', 'height': '600px'}),  # Relative positioning container for map

    ]),  # Relative positioning container for map and date picker

], style={'maxWidth': '1800px', 'margin': 'auto'})

@dash_app.callback(
    [Output('layer', 'children'),
     Output('output_date', 'children')],
    [Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_output(start_date, end_date):
    if start_date and end_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_date_adjusted = end_date + timedelta(days=1) - timedelta(seconds=1)
        markers = update_map(start_date, end_date_adjusted)
        return (
            markers,
            f'You have selected from {start_date} to {end_date}'
        )
    else:
        return (
            [],
            'Please select a date range'
        )

# Function to update the map with markers
def update_map(start_date, end_date):
    locations = Location.query.all()
    markers = []

    for location in locations:
        loc_id = location.id

        dust_data = db.session.query(DustMeasurements).filter(
            DustMeasurements.location_id == loc_id,
            DustMeasurements.timestamp >= start_date,
            DustMeasurements.timestamp <= end_date
        ).all()

        gas_data = db.session.query(GasMeasurements).filter(
            GasMeasurements.location_id == loc_id,
            GasMeasurements.timestamp >= start_date,
            GasMeasurements.timestamp <= end_date
        ).all()

        # Extract values
        pm10_values = [dust.pm10 for dust in dust_data if dust.pm10 is not None]
        pm25_values = [dust.pm25 for dust in dust_data if dust.pm25 is not None]
        no2_values = [gas.no2 for gas in gas_data if gas.no2 is not None]
        o3_values = [gas.o3 for gas in gas_data if gas.o3 is not None]
        so2_values = [gas.so2 for gas in gas_data if gas.so2 is not None]
        co_values = [gas.co for gas in gas_data if gas.co is not None]

        def average(values):
            if values:
                avg = sum(values) / len(values)
                return f"{avg:.2f}"
            else:
                return 'N/A'

        popup_text = html.Div([
            html.P(f"Location: {location.city}", style={'font-size': '14px', 'margin-bottom': '5px'}),
            html.P(f"Average PM10: {average(pm10_values)}", style={'font-size': '14px', 'margin-bottom': '5px'}),
            html.P(f"Average PM2.5: {average(pm25_values)}", style={'font-size': '14px', 'margin-bottom': '5px'}),
            html.P(f"Average NO2: {average(no2_values)}", style={'font-size': '14px', 'margin-bottom': '5px'}),
            html.P(f"Average O3: {average(o3_values)}", style={'font-size': '14px', 'margin-bottom': '5px'}),
            html.P(f"Average SO2: {average(so2_values)}", style={'font-size': '14px', 'margin-bottom': '5px'}),
            html.P(f"Average CO: {average(co_values)}", style={'font-size': '14px', 'margin-bottom': '5px'})
        ])

        marker = dl.Marker(position=[location.latitude, location.longitude], 
                           children=dl.Popup(popup_text))
        markers.append(marker)

    return markers


if __name__ == '__main__':
    dash_app.run_server(debug=True)
