import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import base64
from utils.parser import parse_xml_scores
from utils.charts import (
    update_position_chart, update_gap_chart, update_class_gap_chart,
    update_laptime_chart, update_laptime_no_pit_chart,
    update_fuel_chart, update_ve_chart, update_tire_wear_chart,
    update_fuel_level_chart, update_ve_level_chart, update_tire_consumption_chart,
    update_consistency_chart, update_tire_degradation_chart
)

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

with open('assets/index.html', 'r') as f:
    app.index_string = f.read()

try:
    with open('/home/ebeninca/repo/rFactor2-lmu-graphs/2025_10_26_01_40_42-54R1.xml', 'r', encoding='utf-8') as f:
        initial_df, initial_race_info, initial_incidents = parse_xml_scores(f.read())
except:
    initial_df = pd.DataFrame()
    initial_race_info = {}
    initial_incidents = {'chat': [], 'incident': [], 'penalty': []}

app.layout = html.Div([
    html.H1('Race Data Visualization', style={'textAlign': 'center'}),
    
    html.Div(id='race-info', style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f0f0f0', 'margin': '10px'}),
    
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ', html.A('Select XML File')]),
        style={
            'width': '100%', 'height': '60px', 'lineHeight': '60px',
            'borderWidth': '1px', 'borderStyle': 'dashed', 'borderRadius': '5px',
            'textAlign': 'center', 'margin': '10px'
        }
    ),
    
    dcc.Loading(
        id='loading',
        type='circle',
        children=html.Div(id='upload-status')
    ),
    
    html.Div([
        html.Div([
            html.Label('Select Drivers:', style={'fontSize': '12px', 'marginBottom': '2px'}),
            dcc.Dropdown(id='driver-filter', multi=True, placeholder='All Drivers', style={'fontSize': '12px'}),
            
            html.Label('Select Class:', style={'fontSize': '12px', 'marginBottom': '2px', 'marginTop': '8px'}),
            dcc.Dropdown(id='class-filter', multi=True, placeholder='All Classes', style={'fontSize': '12px'}),
            
            html.Label('Select Team:', style={'fontSize': '12px', 'marginBottom': '2px', 'marginTop': '8px'}),
            dcc.Dropdown(id='car-filter', multi=True, placeholder='All Teams', style={'fontSize': '12px'}),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
        
        html.Div([
            html.Label('Select Vehicle:', style={'fontSize': '12px', 'marginBottom': '2px'}),
            dcc.Dropdown(id='veh-filter', multi=True, placeholder='All Vehicles', style={'fontSize': '12px'}),
            
            html.Label('Select Car Type:', style={'fontSize': '12px', 'marginBottom': '2px', 'marginTop': '8px'}),
            dcc.Dropdown(id='cartype-filter', multi=True, placeholder='All Car Types', style={'fontSize': '12px'}),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top', 'padding': '10px'}),
    ]),
    
    dcc.Tabs(id='tabs', value='tab-position', children=[
        dcc.Tab(label='Position', value='tab-position'),
        dcc.Tab(label='Gap', value='tab-gap'),
        dcc.Tab(label='Lap Times', value='tab-laptimes'),
        dcc.Tab(label='Fuel', value='tab-fuel'),
        dcc.Tab(label='Tires', value='tab-tires'),
        dcc.Tab(label='Events', value='tab-incidents')
    ]),
    
    dcc.Loading(
        id='loading-tabs',
        type='circle',
        parent_style={'position': 'relative', 'minHeight': '80px'},
        children=html.Div(id='tabs-content')
    ),
    
    dcc.Store(id='stored-data', data=initial_df.to_dict('records')),
    dcc.Store(id='stored-race-info', data=initial_race_info),
    dcc.Store(id='stored-incidents', data=initial_incidents)
])

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('stored-data', 'data'),
     Input('driver-filter', 'value'),
     Input('class-filter', 'value'),
     Input('car-filter', 'value'),
     Input('veh-filter', 'value'),
     Input('cartype-filter', 'value'),
     Input('stored-incidents', 'data')]
)
def render_tab_content(active_tab, data, selected_drivers, selected_classes, selected_cars, selected_veh, selected_cartype, incidents):
    df = pd.DataFrame(data)
    
    if not df.empty:
        if selected_drivers:
            df = df[df['Driver'].isin(selected_drivers)]
        if selected_classes:
            df = df[df['Class'].isin(selected_classes)]
        if selected_cars:
            df = df[df['Car'].isin(selected_cars)]
        if selected_veh:
            df = df[df['VehName'].isin(selected_veh)]
        if selected_cartype:
            df = df[df['CarType'].isin(selected_cartype)]
        
        data = df.to_dict('records')
    
    if active_tab == 'tab-position':
        return dcc.Graph(id='position-chart', figure=update_position_chart(data, None, None))
    elif active_tab == 'tab-gap':
        return html.Div([
            dcc.Graph(id='class-gap-chart', figure=update_class_gap_chart(data, None, None)),
            dcc.Graph(id='gap-chart', figure=update_gap_chart(data, None, None))
        ])
    elif active_tab == 'tab-laptimes':
        return html.Div([
            dcc.Graph(id='laptime-no-pit-chart', figure=update_laptime_no_pit_chart(data, None, None)),
            dcc.Graph(id='laptime-chart', figure=update_laptime_chart(data, None, None)),
            dcc.Graph(id='consistency-chart', figure=update_consistency_chart(data, None, None))
        ])
    elif active_tab == 'tab-fuel':
        return html.Div([
            dcc.Graph(id='fuel-level-chart', figure=update_fuel_level_chart(data, None, None)),
            dcc.Graph(id='fuel-chart', figure=update_fuel_chart(data, None, None)),
            dcc.Graph(id='ve-level-chart', figure=update_ve_level_chart(data, None, None)),
            dcc.Graph(id='ve-chart', figure=update_ve_chart(data, None, None))
        ])
    elif active_tab == 'tab-tires':
        return html.Div([
            dcc.Graph(id='tire-wear-chart', figure=update_tire_wear_chart(data, None, None)),
            dcc.Graph(id='tire-consumption-chart', figure=update_tire_consumption_chart(data, None, None)),
            dcc.Graph(id='tire-degradation-chart', figure=update_tire_degradation_chart(data, None, None))
        ])
    elif active_tab == 'tab-incidents':
        return html.Div([
            dcc.Tabs(id='events-tabs', value='events-chat', children=[
                dcc.Tab(label='💬 Chat', value='events-chat'),
                dcc.Tab(label='⚠️ Incidents', value='events-incidents'),
                dcc.Tab(label='🚨 Penalties', value='events-penalties')
            ]),
            html.Div(id='events-content', style={'padding': '20px'})
        ])

@app.callback(
    [Output('stored-data', 'data'),
     Output('stored-race-info', 'data'),
     Output('stored-incidents', 'data'),
     Output('upload-status', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_data(contents, filename):
    if contents is None:
        return initial_df.to_dict('records'), initial_race_info, initial_incidents, ''
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        df, race_info, incidents = parse_xml_scores(decoded.decode('utf-8'))
        return df.to_dict('records'), race_info, incidents, html.Div(f'✓ {filename} loaded', style={'color': 'green'})
    except Exception as e:
        return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(f'✗ Error: {str(e)}', style={'color': 'red'})

@app.callback(
    [Output('driver-filter', 'options'),
     Output('class-filter', 'options'),
     Output('car-filter', 'options'),
     Output('veh-filter', 'options'),
     Output('cartype-filter', 'options'),
     Output('driver-filter', 'value'),
     Output('class-filter', 'value'),
     Output('car-filter', 'value'),
     Output('veh-filter', 'value'),
     Output('cartype-filter', 'value')],
    Input('stored-data', 'data')
)
def update_filters(data):
    df = pd.DataFrame(data)
    if df.empty:
        return [], [], [], [], [], None, None, None, None, None
    
    drivers = [{'label': d, 'value': d} for d in sorted(df['Driver'].unique())]
    classes = [{'label': c, 'value': c} for c in sorted(df['Class'].unique())]
    cars = [{'label': c, 'value': c} for c in sorted(df['Car'].unique())]
    vehs = [{'label': v, 'value': v} for v in sorted(df['VehName'].unique()) if v]
    cartypes = [{'label': ct, 'value': ct} for ct in sorted(df['CarType'].unique()) if ct]
    
    return drivers, classes, cars, vehs, cartypes, None, None, None, None, None

@app.callback(
    Output('race-info', 'children'),
    Input('stored-race-info', 'data')
)
def update_race_info(race_info):
    if not race_info:
        return ''
    
    race_time = race_info.get('time', '0')
    race_laps = race_info.get('laps', '0')
    
    try:
        time_val = int(race_time)
        laps_val = int(race_laps)
    except:
        time_val = 0
        laps_val = 0
    
    if time_val > 1000:
        hours = time_val // 3600
        minutes = (time_val % 3600) // 60
        duration_text = f"⏱️ {hours}h {minutes}min" if minutes > 0 else f"⏱️ {hours} hours"
    elif time_val > 0:
        duration_text = f"⏱️ {time_val} minutes"
    else:
        duration_text = f"🏁 {laps_val} laps"
    
    server_name = race_info.get('server', '')
    track_length = race_info.get('track_length', '0')
    mech_fail = 'Yes' if race_info.get('mech_fail', '0') == '1' else 'No'
    tire_warmers = 'Yes' if race_info.get('tire_warmers', '0') == '1' else 'No'
    
    first_line = []
    if server_name and server_name != 'Unknown':
        first_line.append(html.Span(f"🖥️ {server_name}", style={'marginRight': '20px'}))
    first_line.extend([
        html.Span(f"📍 {race_info.get('track', 'Unknown')} - {race_info.get('course', 'Unknown')}", style={'marginRight': '20px'}),
        html.Span(f"📏 Track Length: {track_length}m", style={'marginRight': '20px'}),
        html.Span(f"📅 {race_info.get('date', 'Unknown')}", style={'marginRight': '20px'}),
        html.Span(duration_text)
    ])
    
    return html.Div([
        html.H3('Race Information', style={'marginBottom': '10px'}),
        html.Div(first_line),
        html.Div([
            html.Span(f"🔧 Mech Fail: {mech_fail}", style={'marginRight': '20px'}),
            html.Span(f"💥 Damage: {race_info.get('damage_mult', '0')}x", style={'marginRight': '20px'}),
            html.Span(f"⛽ Fuel: {race_info.get('fuel_mult', '0')}x", style={'marginRight': '20px'}),
            html.Span(f"🏎️ Tire: {race_info.get('tire_mult', '0')}x", style={'marginRight': '20px'}),
            html.Span(f"🔥 Warmers: {tire_warmers}", style={'marginRight': '20px'}),
            html.Span(f"🎮 Game Version: {race_info.get('game_version', 'Unknown')}")
        ], style={'marginTop': '5px'})
    ])

@app.callback(
    Output('events-content', 'children'),
    [Input('events-tabs', 'value'),
     Input('stored-incidents', 'data')]
)
def render_events_content(active_events_tab, incidents):
    table_style = {
        'width': '100%', 
        'borderCollapse': 'collapse', 
        'fontSize': '14px',
        'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'
    }
    th_style = {
        'textAlign': 'left',
        'padding': '12px',
        'backgroundColor': '#f8f9fa',
        'borderBottom': '2px solid #dee2e6',
        'fontWeight': '600'
    }
    td_style = {
        'padding': '10px 12px',
        'borderBottom': '1px solid #e9ecef'
    }
    
    if active_events_tab == 'events-chat':
        messages = incidents.get('chat', [])
        if not messages:
            return html.P('No chat messages')
        return html.Table([
            html.Thead(html.Tr([html.Th('Time', style=th_style), html.Th('Message', style=th_style)])),
            html.Tbody([html.Tr([html.Td(f"{msg['et']}s", style=td_style), html.Td(msg['message'], style=td_style)]) for msg in messages])
        ], style=table_style)
    elif active_events_tab == 'events-incidents':
        messages = incidents.get('incident', [])
        if not messages:
            return html.P('No incidents')
        return html.Table([
            html.Thead(html.Tr([html.Th('Time', style=th_style), html.Th('Message', style=th_style)])),
            html.Tbody([html.Tr([html.Td(f"{msg['et']}s", style=td_style), html.Td(msg['message'], style=td_style)]) for msg in messages])
        ], style=table_style)
    elif active_events_tab == 'events-penalties':
        messages = incidents.get('penalty', [])
        if not messages:
            return html.P('No penalties')
        return html.Table([
            html.Thead(html.Tr([html.Th('Time', style=th_style), html.Th('Message', style=th_style)])),
            html.Tbody([html.Tr([html.Td(f"{msg['et']}s", style=td_style), html.Td(msg['message'], style=td_style)]) for msg in messages])
        ], style=table_style)

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    app.run_server(debug=debug_mode, host='0.0.0.0', port=7860, dev_tools_props_check=False)
