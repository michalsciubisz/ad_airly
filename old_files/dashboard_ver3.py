import dash
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
from dash import dcc, html
from dash.dependencies import Input, Output
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from datetime import date, timedelta, datetime
from database import app, db, DustMeasurements, GasMeasurements, AQIIndicator, Location

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dashboard3/', external_stylesheets=external_stylesheets)

# Define today's date
today = date.today()

# Zdefiniowanie rozłożenia wykresów
dash_app.layout = html.Div([
    html.Div([
        html.H1('Air Quality Dashboards',
                style={'textAlign': 'center', 'color': '#FFFFFF', 'marginBottom': '0', 'fontSize': '20px'}),

        dcc.Interval(
            id='interval-component',
            interval=60 * 1000,  # Update every 60 seconds
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
                value='Kraków',
                style={'width': '150px', 'display': 'inline-block'}
            ),
            html.Label('Date Range',
                       style={'fontWeight': 'bold', 'color': '#FFFFFF', 'marginRight': '10px', 'marginLeft': '20px'}),
            dcc.DatePickerRange(
                id='date-picker-range',
                start_date=today,
                end_date=today,
                style={'display': 'inline-block'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'backgroundColor': '#1A1A1A', 'padding': '10px'}),
    ], style={'marginBottom': '10px'}),

    html.Div([
        html.Div([
            html.H3(
                    style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='pm10_pm25_scatter_fig', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1.3', 'padding': '5px'}),

        html.Div([
            html.H3(
                    style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='pm10_pm25_hist_fig', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'}),

        html.Div([
            html.H3(
                    style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='aqi_level_fig', style={'height': '250px'})
        ], style={'flex': '0.6', 'padding': '5px'}),
    ], style={'display': 'flex', 'marginBottom': '10px'}),

    html.Div([
        html.Div([
            html.H3(
                    style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='o3_co_fig', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'}),

        html.Div([
            html.H3(
                    style={'textAlign': 'center', 'fontSize': '16px', 'color': '#FFFFFF', 'margin': '10px'}),
            dcc.Graph(id='so2_no2_fig', style={'height': '250px', 'borderRadius': '10px'})
        ], style={'flex': '1', 'padding': '5px'}),
    ], style={'display': 'flex'}),

], style={'maxWidth': '1800px', 'margin': 'auto', 'backgroundColor': '#1A1A1A', 'padding': '10px',
          'borderRadius': '10px'})

# Callbacks żeby grafy się odświezaly
@dash_app.callback(
    [Output('pm10_pm25_scatter_fig', 'figure'),
     Output('pm10_pm25_hist_fig', 'figure'),
     Output('o3_co_fig', 'figure'),
     Output('so2_no2_fig', 'figure'),
     Output('aqi_level_fig', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('city-dropdown', 'value')]
)
# Dynamiczna zmiana danych w trakcie działania systemu
def update_output(n, start_date, end_date, city):
    if start_date and end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        end_date_adjusted = end_date + timedelta(days=1) - timedelta(seconds=1)
        graphs = update_graphs(city, start_date, end_date_adjusted)
        return (
            graphs[0],  # pm10_pm25_scatter_fig
            graphs[1],  # pm10_pm25_hist_fig
            graphs[2],  # o3_co_fig
            graphs[3],  # so2_no2_fig
            graphs[4]  # aqi_level_fig
        )
    else:
        empty_fig = {'data': [], 'layout': {}}
        return (
            empty_fig,  # pm10_pm25_scatter_fig
            empty_fig,  # pm10_pm25_hist_fig
            empty_fig,  # o3_co_fig
            empty_fig,  # so2_no2_fig
            empty_fig  # aqi_level_fig
        )


# Funkcja do znalezienia dnia tygodnia
def find_day_of_week(df):
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['day_of_week'] = df['timestamp'].dt.strftime('%A')
    return df

dark_layout = dict(
    plot_bgcolor='#2E2E2E',  # Ciemne szare tło dla wykresów
    paper_bgcolor='#2E2E2E',  # Bardzo ciemne tło dla ogólnego tła
    font=dict(color='#FFFFFF'),  # Biały kolor czcionki
    margin=dict(t=50, b=10, l=10, r=10),  # Małe marginesy
)

# Uaktualnianie grafów
def update_graphs(city, start_date, end_date):
    location = Location.query.filter_by(city=city).first()
    loc_id = location.id

    # Zebranie danych dotyczących pyłów
    pm_data = db.session.query(DustMeasurements.timestamp, DustMeasurements.pm10, DustMeasurements.pm25) \
        .filter(DustMeasurements.location_id == loc_id) \
        .filter(DustMeasurements.timestamp >= start_date) \
        .filter(DustMeasurements.timestamp <= end_date) \
        .group_by(DustMeasurements.timestamp) \
        .order_by(DustMeasurements.timestamp.desc()) \
        .all()

    pm_df = pd.DataFrame(pm_data, columns=['timestamp', 'pm10', 'pm25'])
    pm_df = find_day_of_week(pm_df)

    # Wybranie palety kolorów
    color_palette_pm10 = px.colors.qualitative.Vivid
    color_palette_pm25 = px.colors.qualitative.Dark24

    # Dodanie wykresu punktowego
    pm10_pm25_scatter_fig = go.Figure()

    # Dodanie ścieżki kolejnego wskaźnika
    for i, day in enumerate(pm_df['day_of_week'].unique()):
        day_data = pm_df[pm_df['day_of_week'] == day]
        pm10_pm25_scatter_fig.add_trace(go.Scatter(x=day_data['timestamp'], y=day_data['pm10'],
                                                   mode='markers', name=f'PM₁₀ - {day}',
                                                   marker=dict(color=color_palette_pm10[i])))
        pm10_pm25_scatter_fig.add_trace(go.Scatter(x=day_data['timestamp'], y=day_data['pm25'],
                                                   mode='markers', name=f'PM₂₅ - {day}',
                                                   marker=dict(color=color_palette_pm25[i])))

    # Update layout
    pm10_pm25_scatter_fig.update_layout(
        title='PM₁₀ and PM₂₅ levels by day',
        xaxis_title='Timestamp',
        yaxis_title='PM value',
        showlegend=True,
        legend_title_text='Day of Week',
        legend_tracegroupgap=10,
        **dark_layout
    )

    # Histogram rozłożenia wartości współczynników PM10 oraz PM25
    pm10_pm25_hist_fig = px.histogram(pm_df, x='pm10', histfunc='count', opacity=0.75,
                                      labels={'pm10': 'PM10', 'y': 'Count'},
                                      title='Histogram of PM10')

    pm10_pm25_hist_fig.add_trace(px.histogram(pm_df, x='pm25', histfunc='count', opacity=0.75,
                                              color_discrete_sequence=['orange']).data[0])

    pm10_pm25_hist_fig.update_layout(
        barmode='overlay',
        title='Histogram of PM₁₀ and PM₂₅',
        xaxis_title='PM value',
        yaxis_title='Count',
        legend=dict(x=0.7, y=0.95, bgcolor='rgba(0,0,0,0)', bordercolor='rgba(0,0,0,0)'),
        **dark_layout
    )

    # Zebranie danych dotyczących gazów
    gas_data = db.session.query(GasMeasurements.timestamp, GasMeasurements.o3, GasMeasurements.co, GasMeasurements.so2,
                                GasMeasurements.no2) \
        .filter(GasMeasurements.location_id == loc_id) \
        .filter(GasMeasurements.timestamp >= start_date) \
        .filter(GasMeasurements.timestamp <= end_date) \
        .group_by(GasMeasurements.timestamp) \
        .order_by(GasMeasurements.timestamp.desc()) \
        .all()

    gas_df = pd.DataFrame(gas_data, columns=['timestamp', 'o3', 'co', 'so2', 'no2'])
    gas_df = find_day_of_week(gas_df)

    # Wybranie palety kolorów
    color_palette_gas = px.colors.qualitative.Dark24

    # Trend zmian O₃ oraz CO
    o3_co_fig = go.Figure()
    for i, day in enumerate(gas_df['day_of_week'].unique()):
        day_data = gas_df[gas_df['day_of_week'] == day]
        o3_co_fig.add_trace(go.Scatter(x=day_data['timestamp'], y=day_data['o3'],
                                       mode='lines+markers', name=f'O₃ - {day}',
                                       line=dict(color=color_palette_gas[i])))
        o3_co_fig.add_trace(go.Scatter(x=day_data['timestamp'], y=day_data['co'],
                                       mode='lines+markers', name=f'CO - {day}',
                                       line=dict(color=color_palette_gas[i + 1])))

    o3_co_fig.update_layout(
        title='O₃ and CO levels by day',
        xaxis_title='Timestamp',
        yaxis_title='Gas value',
        showlegend=True,
        legend_title_text='Day of Week',
        legend_tracegroupgap=10,
        **dark_layout
    )

    # Utworzenie wykresu powierzchniowego
    so2_no2_fig = go.Figure()

    # Dodanie ścieżek
    so2_no2_fig.add_trace(go.Scatter(x=gas_df['timestamp'], y=gas_df['so2'], fill='tozeroy', mode='lines', name='SO₂',
                                     line=dict(color='orange')))
    so2_no2_fig.add_trace(go.Scatter(x=gas_df['timestamp'], y=gas_df['no2'], fill='tozeroy', mode='lines', name='NO₂',
                                     line=dict(color='#00CCFF')))

    so2_no2_fig.update_layout(
        title='SO₂/NO₂ Area Chart',
        xaxis_title='Timestamp',
        yaxis_title='Gas concentration',
        showlegend=True,
        legend_title_text='Gas type',
        **dark_layout
    )

    # Wskaźnik poziomu AQI
    aqi_data = db.session.query(GasMeasurements.timestamp, AQIIndicator.level) \
        .join(AQIIndicator, GasMeasurements.id == AQIIndicator.gas_measurement_id) \
        .filter(GasMeasurements.location_id == loc_id) \
        .filter(GasMeasurements.timestamp >= start_date) \
        .filter(GasMeasurements.timestamp <= end_date) \
        .group_by(GasMeasurements.timestamp) \
        .order_by(GasMeasurements.timestamp.desc()) \
        .all()

    aqi_df = pd.DataFrame(aqi_data, columns=['timestamp', 'level'])
    aqi_df = find_day_of_week(aqi_df)

    aqi_df['day_of_week'] = pd.Categorical(aqi_df['day_of_week'],
                                           categories=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                                                       'Saturday', 'Sunday'], ordered=True)

    # Zliczenie ilości wystąpień poszczególnych poziomów
    agg_df = aqi_df.groupby(['day_of_week', 'level'], observed=False).size().reset_index(name='count')
    heatmap_data = agg_df.pivot(index='day_of_week', columns='level', values='count').fillna(0)

    # Utworzenie heatmapy
    aqi_level_fig = px.imshow(heatmap_data,
                              labels=dict(x='', y="Day of Week", color="Count"),
                              x=heatmap_data.columns,
                              y=heatmap_data.index,
                              color_continuous_scale='viridis')

    aqi_level_fig.update_layout(title='AQI levels across days',
                                yaxis_title='Day of Week',
                                **dark_layout)

    return pm10_pm25_scatter_fig, pm10_pm25_hist_fig, o3_co_fig, so2_no2_fig, aqi_level_fig


if __name__ == '__main__':
    dash_app.run_server(debug=True)
