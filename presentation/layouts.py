from dash import html, dcc
import pandas as pd

def create_main_layout(initial_df, initial_race_info, initial_incidents):
    """Cria o layout principal da aplicação"""
    return html.Div([
        html.Div([
            html.H1('Race Data Visualization', style={'textAlign': 'center'}),
            
            html.Div(id='race-info', style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f0f0f0', 'margin': '10px 0', 'borderRadius': '5px'}),
            
            dcc.Upload(
                id='upload-data',
                children=html.Div(['Drag and Drop or ', html.A('Select XML File')]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
                    'textAlign': 'center', 'margin': '10px 0'
                }
            ),
            
            html.P('📁 Maximum file size: 20MB • 🔒 Your data is not stored or persisted on the server - processed in memory only', 
                   style={'textAlign': 'center', 'fontSize': '12px', 'color': '#666', 'margin': '0'}),
            
            dcc.Loading(
                id='loading',
                type='circle',
                children=html.Div(id='upload-status')
            ),
            
            create_filters_section(),
            
            create_tabs_section(),
            
            dcc.Loading(
                id='loading-tabs',
                type='circle',
                parent_style={'position': 'relative', 'minHeight': '80px'},
                children=html.Div(id='tabs-content')
            ),
            
            # Data stores
            dcc.Store(id='stored-data', data=initial_df.to_dict('records')),
            dcc.Store(id='stored-race-info', data=initial_race_info),
            dcc.Store(id='stored-incidents', data=initial_incidents),
            dcc.Store(id='standings-lap-store'),
            dcc.Store(id='laptimes-tab-store', data='laptimes-charts'),
            dcc.Store(id='events-tab-store', data='events-chat')
        ], className='main-container')
    ])

def create_filters_section():
    """Cria a seção de filtros"""
    return html.Div([
        html.Div([
            html.Label('Select Class:', style={'fontSize': '12px', 'marginBottom': '2px'}),
            dcc.Dropdown(id='class-filter', multi=True, placeholder='All Classes', style={'fontSize': '12px', 'minWidth': '220px'}),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.Label('Select Drivers:', style={'fontSize': '12px', 'marginBottom': '2px'}),
            dcc.Dropdown(id='driver-filter', multi=True, placeholder='All Drivers', style={'fontSize': '12px', 'minWidth': '220px'}),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.Label('Select Team:', style={'fontSize': '12px', 'marginBottom': '2px'}),
            dcc.Dropdown(id='car-filter', multi=True, placeholder='All Teams', style={'fontSize': '12px', 'minWidth': '220px'}),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.Label('Select Vehicle:', style={'fontSize': '12px', 'marginBottom': '2px'}),
            dcc.Dropdown(id='veh-filter', multi=True, placeholder='All Vehicles', style={'fontSize': '12px', 'minWidth': '220px'}),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.Label('Select Car Type:', style={'fontSize': '12px', 'marginBottom': '2px'}),
            dcc.Dropdown(id='cartype-filter', multi=True, placeholder='All Car Types', style={'fontSize': '12px', 'minWidth': '220px'}),
        ], style={'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
    ])

def create_tabs_section():
    """Cria a seção de tabs"""
    return dcc.Tabs(id='tabs', value='tab-standings', children=[
        dcc.Tab(label='Standings', value='tab-standings'),
        dcc.Tab(label='Position', value='tab-position'),
        dcc.Tab(label='Gap', value='tab-gap'),
        dcc.Tab(label='Lap Times', value='tab-laptimes'),
        dcc.Tab(label='Fuel', value='tab-fuel'),
        dcc.Tab(label='Tires', value='tab-tires'),
        dcc.Tab(label='Events', value='tab-incidents')
    ])