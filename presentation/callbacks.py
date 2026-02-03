import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import base64
from data.parsers import parse_xml_scores
from business.analytics import (
    update_position_chart, update_gap_chart, update_class_gap_chart,
    update_laptime_chart, update_laptime_no_pit_chart,
    update_fuel_chart, update_ve_chart, update_tire_wear_chart,
    update_fuel_level_chart, update_ve_level_chart, update_tire_consumption_chart,
    update_consistency_chart, update_tire_degradation_chart
)

def register_callbacks(app, initial_df, initial_race_info, initial_incidents):
    """Registra todos os callbacks da aplicação"""
    
    @app.callback(
        Output('tabs-content', 'children'),
        [Input('tabs', 'value'),
         Input('stored-data', 'data'),
         Input('class-filter', 'value'),
         Input('driver-filter', 'value'),
         Input('car-filter', 'value'),
         Input('veh-filter', 'value'),
         Input('cartype-filter', 'value'),
         Input('stored-incidents', 'data')],
        [State('standings-lap-store', 'data')],
        prevent_initial_call=False
    )
    def render_tab_content(active_tab, data, selected_classes, selected_drivers, selected_cars, selected_veh, selected_cartype, incidents, stored_lap):
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
            return _render_standings_tab(data, stored_lap)
        elif active_tab == 'tab-position':
            return dcc.Graph(id='position-chart', figure=update_position_chart(data, None, None))
        elif active_tab == 'tab-gap':
            return html.Div([
                dcc.Graph(id='class-gap-chart', figure=update_class_gap_chart(data, None, None)),
                dcc.Graph(id='gap-chart', figure=update_gap_chart(data, None, None))
            ])
        elif active_tab == 'tab-laptimes':
            return html.Div([
                dcc.Tabs(id='laptimes-tabs', value='laptimes-charts', children=[
                    dcc.Tab(label='Charts', value='laptimes-charts'),
                    dcc.Tab(label='Table', value='laptimes-table')
                ]),
                html.Div(id='laptimes-content')
            ], style={'padding': '10px 20px 0 20px'})
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
                html.Div(id='events-content', style={'padding': '20px 40px'})
            ], style={'padding': '10px 20px 0 20px'})

    @app.callback(
        Output('laptimes-content', 'children'),
        [Input('laptimes-tabs', 'value'),
         Input('stored-data', 'data'),
         Input('driver-filter', 'value'),
         Input('class-filter', 'value'),
         Input('car-filter', 'value'),
         Input('veh-filter', 'value'),
         Input('cartype-filter', 'value')]
    )
    def render_laptimes_content(active_laptimes_tab, data, selected_drivers, selected_classes, selected_cars, selected_veh, selected_cartype):
        df = pd.DataFrame(data)
        
        # Apply all filters
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
        
        filtered_data = df.to_dict('records')
        
        if active_laptimes_tab == 'laptimes-charts':
            return html.Div([
                dcc.Graph(id='laptime-no-pit-chart', figure=update_laptime_no_pit_chart(filtered_data, None, None)),
                dcc.Graph(id='laptime-chart', figure=update_laptime_chart(filtered_data, None, None)),
                dcc.Graph(id='consistency-chart', figure=update_consistency_chart(filtered_data, None, None))
            ])
        elif active_laptimes_tab == 'laptimes-table':
            return _create_laptimes_table(df)

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
        
        # Check file size (20MB limit)
        file_size_mb = len(decoded) / (1024 * 1024)
        if file_size_mb > 20:
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div([
                html.Span('❌ ', style={'fontSize': '16px'}),
                html.Span(f'File {filename} is too large ({file_size_mb:.1f}MB). Maximum allowed size is 20MB.', 
                         style={'color': '#dc3545', 'fontWeight': 'bold'})
            ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8d7da', 'border': '1px solid #f5c6cb', 'borderRadius': '5px', 'margin': '10px'})
        
        try:
            df, race_info, incidents = parse_xml_scores(decoded.decode('utf-8'))
            return df.to_dict('records'), race_info, incidents, html.Div([
                html.Span('✅ ', style={'fontSize': '16px'}),
                html.Span(f'{filename} loaded successfully!', style={'color': '#28a745', 'fontWeight': 'bold'})
            ], id='success-message', style={
                'position': 'fixed', 'top': '20px', 'right': '20px', 'zIndex': '9999',
                'textAlign': 'center', 'padding': '10px 15px', 'backgroundColor': '#d4edda', 
                'border': '1px solid #c3e6cb', 'borderRadius': '5px', 'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
                'animation': 'fadeOut 0.5s ease-in-out 3s forwards'
            })
        except Exception as e:
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div([
                html.Span('❌ ', style={'fontSize': '16px'}),
                html.Span(f'Error loading {filename}: {str(e)}', style={'color': '#dc3545', 'fontWeight': 'bold'})
            ], style={'textAlign': 'center', 'padding': '10px', 'backgroundColor': '#f8d7da', 'border': '1px solid #f5c6cb', 'borderRadius': '5px', 'margin': '10px'})

    @app.callback(
        [Output('class-filter', 'options'),
         Output('driver-filter', 'options'),
         Output('car-filter', 'options'),
         Output('veh-filter', 'options'),
         Output('cartype-filter', 'options'),
         Output('class-filter', 'value'),
         Output('driver-filter', 'value'),
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
        
        return classes, drivers, cars, vehs, cartypes, None, None, None, None, None

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
                html.Span(f"⚫ Tire: {race_info.get('tire_mult', '0')}x", style={'marginRight': '20px'}),
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
        from presentation.components import create_standings_table
        return create_standings_table(selected_lap, data)

    @app.callback(
        Output('laptimes-tab-store', 'data'),
        Input('laptimes-tabs', 'value')
    )
    def store_laptimes_tab(selected_tab):
        return selected_tab

    @app.callback(
        Output('laptimes-tabs', 'value'),
        [Input('stored-data', 'data'),
         Input('driver-filter', 'value'),
         Input('class-filter', 'value'),
         Input('car-filter', 'value'),
         Input('veh-filter', 'value'),
         Input('cartype-filter', 'value')],
        [State('laptimes-tab-store', 'data')]
    )
    def restore_laptimes_tab(data, selected_drivers, selected_classes, selected_cars, selected_veh, selected_cartype, stored_tab):
        return stored_tab

    @app.callback(
        Output('events-tab-store', 'data'),
        Input('events-tabs', 'value')
    )
    def store_events_tab(selected_tab):
        return selected_tab

    @app.callback(
        Output('events-tabs', 'value'),
        [Input('stored-data', 'data'),
         Input('class-filter', 'value')],
        [State('events-tab-store', 'data')]
    )
    def restore_events_tab(data, selected_classes, stored_tab):
        return stored_tab

def _create_laptimes_table(df):
    """Cria a tabela de tempos de volta"""
    if df.empty:
        return html.P('No data available')
    
    # Filter only laps with valid lap times
    lap_df = df[(df['Lap'] > 0) & (df['LapTime'] > 0)].copy()
    
    if lap_df.empty:
        return html.P('No lap time data available')
    
    # Limit to 2000 rows for performance
    if len(lap_df) > 2000:
        lap_df = lap_df.head(2000)
        performance_warning = html.P('⚠️ Showing first 2000 laps for performance. Use filters to see specific data.', 
                                   style={'color': '#ff6b35', 'fontSize': '12px', 'fontStyle': 'italic', 'marginBottom': '10px'})
    else:
        performance_warning = None
    
    # Get finishing order from the last lap data
    last_lap_df = lap_df.groupby('Driver')['Lap'].max().reset_index()
    last_lap_df = last_lap_df.merge(lap_df, on=['Driver', 'Lap'])
    finishing_order = last_lap_df.sort_values('Position')['Driver'].tolist()
    
    # Create a mapping of driver to final position
    final_positions = {driver: pos + 1 for pos, driver in enumerate(finishing_order)}
    
    # Get starting positions
    starting_positions = df[df['Lap'] == 0].set_index('Driver')['Position'].to_dict()
    
    # Sort by finishing order, then by lap
    lap_df['FinishOrder'] = lap_df['Driver'].map({driver: i for i, driver in enumerate(finishing_order)})
    lap_df = lap_df.sort_values(['FinishOrder', 'Lap'])
    
    table_style = {'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '13px'}
    th_style = {'textAlign': 'left', 'padding': '8px', 'backgroundColor': '#f8f9fa', 'borderBottom': '2px solid #dee2e6', 'fontWeight': '600'}
    td_style = {'padding': '6px 8px', 'borderBottom': '1px solid #e9ecef'}
    
    rows = []
    current_driver = None
    
    for _, row in lap_df.iterrows():
        # Add driver header row
        if current_driver != row['Driver']:
            current_driver = row['Driver']
            finish_pos = final_positions.get(row['Driver'], 'DNF')
            start_pos = starting_positions.get(row['Driver'], 'N/A')
            start_text = f" (Started P{int(start_pos)})" if start_pos != 'N/A' and start_pos > 0 else ""
            rows.append(html.Tr([
                html.Td(f"P{finish_pos} - {row['Driver']} - {row['Car']}{start_text}", colSpan=10, 
                       style={**td_style, 'backgroundColor': '#e9ecef', 'fontWeight': 'bold'})
            ]))
        
        # Format lap time
        lap_time = row['LapTime']
        minutes = int(lap_time // 60)
        seconds = lap_time % 60
        lap_time_str = f"{minutes}:{seconds:06.3f}"
        
        # Get sector times from XML if available
        s1 = row.get('S1', 0)
        s2 = row.get('S2', 0) 
        s3 = row.get('S3', 0)
        s1_str = f"{s1:.3f}" if s1 > 0 else '-'
        s2_str = f"{s2:.3f}" if s2 > 0 else '-'
        s3_str = f"{s3:.3f}" if s3 > 0 else '-'
        
        # Virtual Energy
        ve_str = f"{row.get('VE', 0):.1%}" if row.get('VE', 0) > 0 else ''
        
        # Fuel remaining
        fuel_str = f"{row['FuelLevel']:.1%}" if row['FuelLevel'] > 0 else '-'
        
        # Tire wear percentages
        twfl = row.get('TWFL', 0)
        twfr = row.get('TWFR', 0)
        twrl = row.get('TWRL', 0)
        twrr = row.get('TWRR', 0)
        tire_wear_str = f"FL:{twfl:.0%} FR:{twfr:.0%} RL:{twrl:.0%} RR:{twrr:.0%}" if any([twfl, twfr, twrl, twrr]) else '-'
        
        # Tire compounds
        fcompound = row.get('FCompound', '').split(',')[-1] if row.get('FCompound') else '-'
        rcompound = row.get('RCompound', '').split(',')[-1] if row.get('RCompound') else '-'
        compounds_str = f"{fcompound}/{rcompound}"
        
        # Pit stop indicator
        pit_str = 'PIT' if row.get('IsPit', False) else ''
        
        rows.append(html.Tr([
            html.Td(str(int(row['Lap'])), style=td_style),
            html.Td(lap_time_str, style=td_style),
            html.Td(s1_str, style=td_style),
            html.Td(s2_str, style=td_style),
            html.Td(s3_str, style=td_style),
            html.Td(ve_str, style=td_style),
            html.Td(fuel_str, style=td_style),
            html.Td(tire_wear_str, style=td_style),
            html.Td(compounds_str, style=td_style),
            html.Td(pit_str, style={**td_style, 'fontWeight': 'bold', 'color': 'red'})
        ]))
    
    table_content = [
        html.Table([
            html.Thead(html.Tr([
                html.Th('Lap', style=th_style),
                html.Th('Lap Time', style=th_style),
                html.Th('S1', style=th_style),
                html.Th('S2', style=th_style),
                html.Th('S3', style=th_style),
                html.Th('VE', style=th_style),
                html.Th('Fuel', style=th_style),
                html.Th('Tire Wear', style=th_style),
                html.Th('Tires Compound', style=th_style),
                html.Th('Pit', style=th_style)
            ])),
            html.Tbody(rows)
        ], style=table_style)
    ]
    
    if performance_warning:
        table_content.insert(0, performance_warning)
    
    return html.Div(table_content, style={'padding': '20px 40px'})

def _render_standings_tab(data, stored_lap):
    """Renderiza a aba de standings"""
    all_df = pd.DataFrame(data)
    if all_df.empty:
        return html.P('No data available')
    
    max_lap = int(all_df['Lap'].max())
    lap_options = [{'label': f'Lap {i}', 'value': i} for i in range(0, max_lap + 1)]
    
    # Use stored lap if available and valid, otherwise use max_lap
    selected_lap = stored_lap if stored_lap is not None and stored_lap <= max_lap else max_lap
    
    return html.Div([
        html.Div([
            html.Div([
                html.Label('Select Lap:', style={'fontSize': '14px', 'fontWeight': 'bold', 'marginBottom': '10px'}),
                dcc.Dropdown(id='standings-lap-selector', options=lap_options, value=selected_lap, style={'width': '200px'})
            ], style={'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                html.P('ℹ️ Only Class filter affects Standings', 
                       style={'fontSize': '12px', 'color': '#666', 'fontStyle': 'italic', 'margin': '0', 'paddingTop': '15px'})
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '20px'})
        ], style={'marginBottom': '20px'}),
        dcc.Store(id='standings-filtered-data', data=data),
        html.Div(id='standings-table')
    ], style={'padding': '20px'})