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
    with open('/home/ebeninca/repo/rFactor2-lmu-graphs/2026_01_31_17_55_01-49R1.xml', 'r', encoding='utf-8') as f:
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
    
    dcc.Tabs(id='tabs', value='tab-standings', children=[
        dcc.Tab(label='Standings', value='tab-standings'),
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
    dcc.Store(id='stored-incidents', data=initial_incidents),
    dcc.Store(id='standings-lap-store')
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
     Input('stored-incidents', 'data')],
    [State('standings-lap-store', 'data')],
    prevent_initial_call=False
)
def render_tab_content(active_tab, data, selected_drivers, selected_classes, selected_cars, selected_veh, selected_cartype, incidents, stored_lap):
    ctx = dash.callback_context
    
    # If we're on standings tab and only non-class filters changed, don't update
    if active_tab == 'tab-standings' and ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id in ['driver-filter', 'car-filter', 'veh-filter', 'cartype-filter']:
            raise dash.exceptions.PreventUpdate
    
    df = pd.DataFrame(data)
    
    if active_tab == 'tab-standings':
        # For standings, only apply class filter
        if selected_classes:
            df = df[df['Class'].isin(selected_classes)]
        data = df.to_dict('records')
    elif not df.empty:
        # For other tabs, apply all filters
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
    
    if active_tab == 'tab-standings':
        all_df = pd.DataFrame(data)
        if all_df.empty:
            return html.P('No data available')
        
        max_lap = int(all_df['Lap'].max())
        lap_options = [{'label': f'Lap {i}', 'value': i} for i in range(0, max_lap + 1)]
        
        # Use stored lap if available and valid, otherwise use max_lap
        selected_lap = stored_lap if stored_lap is not None and stored_lap <= max_lap else max_lap
        
        return html.Div([
            html.Div([
                html.P('ℹ️ Only Class filter affects Standings', 
                       style={'fontSize': '12px', 'color': '#666', 'fontStyle': 'italic', 'margin': '0 0 15px 0'})
            ]),
            html.Label('Select Lap:', style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
            dcc.Dropdown(id='standings-lap-selector', options=lap_options, value=selected_lap, style={'width': '200px', 'marginBottom': '20px'}),
            dcc.Store(id='standings-filtered-data', data=data),
            html.Div(id='standings-table')
        ], style={'padding': '20px'})
    elif active_tab == 'tab-position':
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

@app.callback(
    Output('standings-lap-store', 'data'),
    Input('standings-lap-selector', 'value')
)
def store_selected_lap(selected_lap):
    return selected_lap

@app.callback(
    Output('standings-table', 'children'),
    [Input('standings-lap-selector', 'value'),
     Input('standings-filtered-data', 'data')]
)
def update_standings_table(selected_lap, data):
    df = pd.DataFrame(data)
    if df.empty or selected_lap is None:
        return html.P('No data available')
    
    # Get all drivers' latest lap up to selected_lap
    all_drivers = df['Driver'].unique()
    lap_df_list = []
    
    for driver in all_drivers:
        driver_data = df[(df['Driver'] == driver) & (df['Lap'] <= selected_lap)]
        if not driver_data.empty:
            latest = driver_data.loc[driver_data['Lap'].idxmax()]
            lap_df_list.append(latest)
    
    lap_df = pd.DataFrame(lap_df_list)
    
    # Sort by laps completed (descending) then by ET (ascending)
    lap_df = lap_df.sort_values(['Lap', 'ET'], ascending=[False, True])
    
    # Assign positions based on correct order
    lap_df['OriginalPosition'] = range(1, len(lap_df) + 1)
    
    # Calculate positions gained/lost using the corrected position
    initial_pos = df[df['Lap'] == 0].set_index('Driver')['Position'].to_dict()
    lap_df['Up'] = lap_df.apply(lambda row: initial_pos.get(row['Driver'], row['OriginalPosition']) - row['OriginalPosition'], axis=1)
    
    # Calculate best lap per driver up to selected lap
    best_laps = df[(df['LapTime'] > 0) & (df['Lap'] <= selected_lap)].groupby('Driver')['LapTime'].min().to_dict()
    lap_df['BestLap'] = lap_df['Driver'].map(best_laps)
    
    # Count pit stops up to selected lap
    pit_counts = df[(df['IsPit'] == True) & (df['Lap'] <= selected_lap)].groupby('Driver').size().to_dict()
    lap_df['Pits'] = lap_df['Driver'].map(pit_counts).fillna(0).astype(int)
    
    # Count laps led up to selected lap
    laps_led = df[(df['Position'] == 1) & (df['Lap'] <= selected_lap) & (df['Lap'] > 0)].groupby('Driver').size().to_dict()
    lap_df['Led'] = lap_df['Driver'].map(laps_led).fillna(0).astype(int)
    
    # Calculate gap to leader
    leader_lap = lap_df.iloc[0]['Lap']
    leader_et = lap_df.iloc[0]['ET']
    
    def calculate_gap(row):
        if row.name == lap_df.index[0]:  # First row is leader
            return 'Leader'
        laps_behind = leader_lap - row['Lap']
        time_gap = row['ET'] - leader_et
        
        # Only use lap format on the last lap of the race
        if selected_lap == df['Lap'].max() and laps_behind >= 1:
            minutes = int(abs(time_gap) // 60)
            seconds = abs(time_gap) % 60
            return f"+{laps_behind}L {minutes}:{seconds:06.3f}"
        else:
            # Format as mm:ss.sss for all other laps
            minutes = int(abs(time_gap) // 60)
            seconds = abs(time_gap) % 60
            return f"+{minutes}:{seconds:06.3f}"
    
    lap_df['Gap'] = lap_df.apply(calculate_gap, axis=1)
    
    table_style = {'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '13px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}
    th_style = {'textAlign': 'left', 'padding': '10px', 'backgroundColor': '#f8f9fa', 'borderBottom': '2px solid #dee2e6', 'fontWeight': '600', 'fontSize': '12px'}
    td_style_table = {'padding': '8px 10px', 'borderBottom': '1px solid #e9ecef'}
    
    # Create color mapping based on sorted class order
    unique_classes = sorted(df['Class'].unique())
    color_palette = ['#D4E6F1', '#E8DAEF', '#FCF3CF', '#E8F8F5', '#FADBD8', '#D6EAF8', '#FEF5E7', '#D5F4E6']
    class_color_map = {cls: color_palette[i % len(color_palette)] for i, cls in enumerate(unique_classes)}
    
    rows = []
    for _, row in lap_df.iterrows():
        up_color = 'green' if row['Up'] > 0 else ('red' if row['Up'] < 0 else 'gray')
        up_text = f"+{row['Up']}" if row['Up'] > 0 else str(row['Up'])
        best_lap_text = f"{int(row['BestLap']//60):01d}:{int(row['BestLap']%60):02d}.{int((row['BestLap']%1)*1000):03d}" if pd.notna(row['BestLap']) else '-'
        class_abbr = row['Class'][:3].upper()
        pos_bg_color = class_color_map.get(row['Class'], '#CCCCCC')
        
        rows.append(html.Tr([
            html.Td(str(int(row['OriginalPosition'])), style={**td_style_table, 'fontWeight': 'bold'}),
            html.Td(up_text, style={**td_style_table, 'color': up_color, 'fontWeight': 'bold'}),
            html.Td(class_abbr, style={**td_style_table, 'backgroundColor': pos_bg_color, 'fontWeight': 'bold', 'color': 'black', 'textAlign': 'center'}),
            html.Td(row['Driver'], style=td_style_table),
            html.Td(row['Car'], style=td_style_table),
            html.Td(row.get('VehName', '-'), style=td_style_table),
            html.Td(str(int(row['Lap'])), style=td_style_table),
            html.Td(row['Gap'], style=td_style_table),
            html.Td(best_lap_text, style=td_style_table),
            html.Td(str(row['Led']), style=td_style_table),
            html.Td(str(row['Pits']), style=td_style_table),
            html.Td(f"{row.get('FCompound', '').split(',')[-1] if row.get('FCompound') else '-'}/{row.get('RCompound', '').split(',')[-1] if row.get('RCompound') else '-'}", style=td_style_table),
            html.Td(row.get('Aids', '-'), style=td_style_table)
        ]))
    
    return html.Table([
        html.Thead(html.Tr([
            html.Th('Pos', style=th_style),
            html.Th('Up', style=th_style),
            html.Th('Cat', style=th_style),
            html.Th('Driver', style=th_style),
            html.Th('Team', style=th_style),
            html.Th('Car', style=th_style),
            html.Th('Laps', style=th_style),
            html.Th('Time/Gap', style=th_style),
            html.Th('Best Lap', style=th_style),
            html.Th('Led', style=th_style),
            html.Th('Pits', style=th_style),
            html.Th('Tires', style=th_style),
            html.Th('Aids', style=th_style)
        ])),
        html.Tbody(rows)
    ], style=table_style)

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    app.run_server(debug=debug_mode, host='0.0.0.0', port=7860, dev_tools_props_check=False)
