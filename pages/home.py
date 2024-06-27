import dash
from dash import html

dash.register_page(__name__, path='/')

layout = html.Div([
    html.H1('Advanced Databases 2024 project', style={'filter': 'brightness(1.5)', 'textAlign': 'center'}),  # Brighter text
    html.H2(
        [
            'The data comes from Airly, an application responsible for monitoring air conditions all around the world: ',
            html.A(
                'source', 
                href='https://airly.org/pl/', 
                target='_blank',  # Opens the link in a new tab
                style={'color': 'darkblue', 'textDecoration': 'none'}  # Styles the link
            )
        ],
        style={'filter': 'brightness(1.5)'},
    ),
    html.H2('Prepared by:', style={'filter': 'brightness(1.5)'}),  # Darker text
    html.Ul([
        html.Li('Michał Ściubisz', style={'filter': 'brightness(2)'}),  # Slightly brighter text
        html.Li('Tomisław Tarnawski', style={'filter': 'brightness(2)'}),  # Slightly brighter text
        html.Li('Wojciech Tokarz', style={'filter': 'brightness(2)'}),  # Slightly brighter text
        html.Li('Jakub Wąsik', style={'filter': 'brightness(2)'}),  # Slightly brighter text
    ])
])

