import dash
from dash import html, dcc, Input, Output, State
import pandas as pd
import base64
import time
import os
import pickle
from data.parsers_secure import parse_xml_scores
from security.security import validate_upload, log_suspicious_activity, MAX_FILE_SIZE
from presentation.styles import (
    CONTENT_PADDING, EVENTS_PADDING, ERROR_MESSAGE, SUCCESS_MESSAGE,
    ICON_LARGE, ICON_MARGIN, ICON_MARGIN_20, ERROR_TEXT, SUCCESS_TEXT,
    FLAG_ICON, TABLE_HEADER, TABLE_CELL_LEFT, NOTIFICATION_BASE
)
from business.analytics import (
    update_position_chart, update_gap_chart, update_class_gap_chart,
    update_laptime_chart, update_laptime_no_pit_chart,
    update_fuel_chart, update_ve_chart, update_tire_wear_chart,
    update_fuel_level_chart, update_ve_level_chart, update_tire_consumption_chart,
    update_consistency_chart, update_tire_degradation_chart, update_pace_decay_chart,
    update_strategy_gantt_chart
)
from data.track_flags import get_country_flag
from presentation.components import create_standings_table

def validate_file_size(decoded_content):
    """Valida se o tamanho do arquivo está dentro do limite permitido"""
    file_size_mb = len(decoded_content) / (1024 * 1024)
    max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
    if file_size_mb > max_size_mb:
        error_msg = f'File is too large ({file_size_mb:.1f}MB). Maximum allowed size is {max_size_mb:.0f}MB.'
        return False, file_size_mb, error_msg
    return True, file_size_mb, None

# Server-side storage for file contents in desktop mode
CACHE_FILE = '.desktop_file_cache.pkl'

def load_cache():
    """Load cache from disk"""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    """Save cache to disk"""
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(cache, f)
    except:
        pass

server_file_cache = load_cache()
server_metadata_cache = {}  # Store parsed metadata

def extract_file_metadata(content):
    """Extract metadata from XML file"""
    try:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        content_str = decoded.decode('utf-8')
        df, race_info, _ = parse_xml_scores(content_str)
        
        # Extract metadata
        event_type = race_info.get('session', 'Race')
        circuit = race_info.get('track', 'Unknown')
        classes = ', '.join(sorted(df['Class'].unique())) if not df.empty else '-'
        num_cars = len(df['Driver'].unique()) if not df.empty else 0
        
        time_val = int(race_info.get('time', '0'))
        laps_val = int(race_info.get('laps', '0'))
        if time_val > 1000:
            hours = time_val // 3600
            minutes = (time_val % 3600) // 60
            duration = f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
        elif time_val > 0:
            duration = f"{time_val}min"
        else:
            duration = f"{laps_val} laps"
        
        event_name = race_info.get('server', '-')
        
        return {
            'event_type': event_type,
            'circuit': circuit,
            'classes': classes,
            'num_cars': num_cars,
            'duration': duration,
            'event_name': event_name
        }
    except:
        return None

def register_callbacks(app, initial_df, initial_race_info, initial_incidents):
    """Registra todos os callbacks da aplicação"""
    
    # Initialize last-folder-store with cached files on app load
    @app.callback(
        Output('last-folder-store', 'data', allow_duplicate=True),
        Input('app-mode', 'data'),
        State('last-folder-store', 'data'),
        prevent_initial_call='initial_duplicate'
    )
    def initialize_cache(app_mode, current_store):
        if app_mode == 'desktop' and not current_store and server_file_cache:
            return list(server_file_cache.keys())
        return current_store if current_store else None
    
    @app.callback(
        [Output('folder-files-store', 'data', allow_duplicate=True),
         Output('file-list-container', 'children', allow_duplicate=True),
         Output('file-list-container', 'style', allow_duplicate=True)],
        [Input('last-folder-store', 'data'),
         Input('app-mode', 'data')],
        prevent_initial_call='initial_duplicate'
    )
    def restore_last_folder(last_folder_data, app_mode):
        if app_mode != 'desktop':
            return None, None, {'display': 'none'}
        
        # Try to restore from cache if no data in store
        xml_files = last_folder_data if last_folder_data else list(server_file_cache.keys())
        
        if not xml_files:
            return None, None, {'display': 'none'}
        
        # Extract metadata for each file
        rows = []
        for i, filename in enumerate(xml_files):
            if filename not in server_metadata_cache:
                content = server_file_cache.get(filename)
                if content:
                    server_metadata_cache[filename] = extract_file_metadata(content)
            
            meta = server_metadata_cache.get(filename)
            if meta:
                row_bg = '#ffffff' if i % 2 == 0 else '#e0e0e0'
                td = lambda extra={}: {'padding': '8px', 'backgroundColor': row_bg, **extra}
                rows.append(html.Tr([
                    html.Td(html.Button(
                        filename,
                        id={'type': 'file-button', 'index': i},
                        n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'background': 'none', 'color': '#0066cc', 'textDecoration': 'underline', 'padding': '0'}
                    ), style=td()),
                    html.Td(meta['event_type'], style=td()),
                    html.Td(meta['circuit'], style=td()),
                    html.Td(meta['classes'], style=td({'fontSize': '11px'})),
                    html.Td(str(meta['num_cars']), style=td({'textAlign': 'center'})),
                    html.Td(meta['duration'], style=td()),
                    html.Td(meta['event_name'], style=td({'fontSize': '11px'}))
                ]))
        
        file_list = html.Div([
            html.H3('Select a file:', style={'fontSize': '14px', 'marginBottom': '10px'}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('File', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Type', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Circuit', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Classes', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Cars', style={'padding': '8px', 'textAlign': 'center', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Duration', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Event', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'})
                ])),
                html.Tbody(rows)
            ], id='file-list-table', style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '12px'})
        ], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'marginTop': '10px', 'maxHeight': '200px', 'overflowY': 'auto'})
        
        return xml_files, file_list, {'display': 'block'}
    
    @app.callback(
        [Output('folder-files-store', 'data'),
         Output('file-list-container', 'children'),
         Output('file-list-container', 'style'),
         Output('upload-status', 'children', allow_duplicate=True),
         Output('last-folder-store', 'data')],
        [Input('upload-data', 'contents'),
         Input('app-mode', 'data')],
        [State('upload-data', 'filename')],
        prevent_initial_call=True
    )
    def handle_folder_upload(contents_list, app_mode, filenames_list):
        if app_mode != 'desktop' or not contents_list:
            return None, None, {'display': 'none'}, '', None
        
        # Clear cache and store new files
        server_file_cache.clear()
        server_metadata_cache.clear()
        xml_filenames = []
        for content, filename in zip(contents_list, filenames_list):
            if filename.lower().endswith(('.xml', '.xmlx')):
                server_file_cache[filename] = content
                xml_filenames.append(filename)
                # Extract metadata
                server_metadata_cache[filename] = extract_file_metadata(content)
        
        # Persist to disk
        save_cache(server_file_cache)
        
        if not xml_filenames:
            return None, None, {'display': 'none'}, html.Div(
                html.Div([
                    html.Span('❌ ', style=ICON_LARGE),
                    html.Span('No XML files found in folder', style=ERROR_TEXT)
                ], style={**ERROR_MESSAGE, **NOTIFICATION_BASE})
            ), None
        
        # Create table with metadata
        rows = []
        for i, filename in enumerate(xml_filenames):
            meta = server_metadata_cache.get(filename)
            if meta:
                row_bg = '#ffffff' if i % 2 == 0 else '#e0e0e0'
                td = lambda extra={}: {'padding': '8px', 'backgroundColor': row_bg, **extra}
                rows.append(html.Tr([
                    html.Td(html.Button(
                        filename,
                        id={'type': 'file-button', 'index': i},
                        n_clicks=0,
                        style={'cursor': 'pointer', 'border': 'none', 'background': 'none', 'color': '#0066cc', 'textDecoration': 'underline', 'padding': '0'}
                    ), style=td()),
                    html.Td(meta['event_type'], style=td()),
                    html.Td(meta['circuit'], style=td()),
                    html.Td(meta['classes'], style=td({'fontSize': '11px'})),
                    html.Td(str(meta['num_cars']), style=td({'textAlign': 'center'})),
                    html.Td(meta['duration'], style=td()),
                    html.Td(meta['event_name'], style=td({'fontSize': '11px'}))
                ]))
        
        file_list = html.Div([
            html.H3('Select a file:', style={'fontSize': '14px', 'marginBottom': '10px'}),
            html.Table([
                html.Thead(html.Tr([
                    html.Th('File', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Type', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Circuit', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Classes', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Cars', style={'padding': '8px', 'textAlign': 'center', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Duration', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}),
                    html.Th('Event', style={'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'})
                ])),
                html.Tbody(rows)
            ], id='file-list-table', style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '12px'})
        ], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'marginTop': '10px', 'maxHeight': '200px', 'overflowY': 'auto'})
        
        return xml_filenames, file_list, {'display': 'block'}, '', xml_filenames

    @app.callback(
        [Output('stored-data', 'data', allow_duplicate=True),
         Output('stored-race-info', 'data', allow_duplicate=True),
         Output('stored-incidents', 'data', allow_duplicate=True),
         Output('upload-status', 'children', allow_duplicate=True),
         Output('standings-lap-store', 'data', allow_duplicate=True)],
        [Input({'type': 'file-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
        [State('folder-files-store', 'data'),
         State('app-mode', 'data')],
        prevent_initial_call=True
    )
    def load_selected_file(n_clicks_list, xml_filenames, app_mode):
        if app_mode != 'desktop' or not xml_filenames:
            raise dash.exceptions.PreventUpdate
        
        ctx = dash.callback_context
        if not ctx.triggered or not ctx.triggered[0]['value']:
            raise dash.exceptions.PreventUpdate
        
        # Get which button was clicked from trigger
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        import json
        clicked_idx = json.loads(trigger_id)['index']
        
        if clicked_idx is None or clicked_idx >= len(xml_filenames):
            raise dash.exceptions.PreventUpdate
        
        filename = xml_filenames[clicked_idx]
        content = server_file_cache.get(filename)
        
        if not content:
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
                html.Div([
                    html.Span('❌ ', style=ICON_LARGE),
                    html.Span(f'{filename}: File not found in cache', style=ERROR_TEXT)
                ], style={**ERROR_MESSAGE, **NOTIFICATION_BASE})
            ), None
        
        try:
            content_type, content_string = content.split(',')
            decoded = base64.b64decode(content_string)
            
            is_valid, file_size_mb, error_msg = validate_file_size(decoded)
            if not is_valid:
                return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
                    html.Div([
                        html.Span('❌ ', style=ICON_LARGE),
                        html.Span(f'{filename}: {error_msg}', style=ERROR_TEXT)
                    ], style={**ERROR_MESSAGE, **NOTIFICATION_BASE})
                ), None
            
            safe_filename, content_str = validate_upload(decoded, filename)
            df, race_info, incidents = parse_xml_scores(content_str)
            
            return df.to_dict('records'), race_info, incidents, html.Div(
                html.Div([
                    html.Span('✅ ', style=ICON_LARGE),
                    html.Span(f'{filename} loaded successfully!', style=SUCCESS_TEXT)
                ], style={**SUCCESS_MESSAGE, **NOTIFICATION_BASE}),
                key=f'success-{time.time()}'
            ), None
        except Exception as e:
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
                html.Div([
                    html.Span('❌ ', style=ICON_LARGE),
                    html.Span(f'Error loading {filename}: {str(e)}', style=ERROR_TEXT)
                ], style={**ERROR_MESSAGE, **NOTIFICATION_BASE})
            ), None
    
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
            return html.Div([
                dcc.Graph(id='position-chart', figure=update_position_chart(data, None, None)),
                dcc.Graph(id='strategy-gantt-chart', figure=update_strategy_gantt_chart(data, None, None))
            ])
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
            ], style=CONTENT_PADDING)
        elif active_tab == 'tab-fuel':
            return html.Div([
                dcc.Graph(id='fuel-level-chart', figure=update_fuel_level_chart(data, None, None)),
                dcc.Graph(id='fuel-chart', figure=update_fuel_chart(data, None, None)),
                dcc.Graph(id='ve-level-chart', figure=update_ve_level_chart(data, None, None)),
                dcc.Graph(id='ve-chart', figure=update_ve_chart(data, None, None))
            ])
        elif active_tab == 'tab-tires':
            return html.Div([
                dcc.Graph(id='pace-decay-chart', figure=update_pace_decay_chart(data, None, None)),
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
                html.Div(id='events-content', style=EVENTS_PADDING)
            ], style=CONTENT_PADDING)

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
         Output('upload-status', 'children'),
         Output('standings-lap-store', 'data', allow_duplicate=True)],
        [Input('upload-data', 'contents'),
         Input('app-mode', 'data')],
        [State('upload-data', 'filename')],
        prevent_initial_call=True
    )
    def update_data(contents, app_mode, filename):
        if app_mode == 'desktop':
            raise dash.exceptions.PreventUpdate
        
        if contents is None:
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, '', None
        
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Validate file size
            is_valid, file_size_mb, error_msg = validate_file_size(decoded)
            if not is_valid:
                log_suspicious_activity('unknown', 'large_file_upload', f'{filename}: {file_size_mb:.1f}MB')
                return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
                    html.Div([
                        html.Span('❌ ', style=ICON_LARGE),
                        html.Span(f'{filename}: {error_msg}', style=ERROR_TEXT)
                    ], style={**ERROR_MESSAGE, **NOTIFICATION_BASE}),
                    key=f'error-{time.time()}'
                ), None
            
            # Validate upload (extension, MIME type, XML structure)
            safe_filename, content_str = validate_upload(decoded, filename)
            
            # Parse (Gunicorn timeout de 30s protege contra processamento lento)
            df, race_info, incidents = parse_xml_scores(content_str)
            
            return df.to_dict('records'), race_info, incidents, html.Div(
                html.Div([
                    html.Span('✅ ', style=ICON_LARGE),
                    html.Span(f'{filename} loaded successfully!', style=SUCCESS_TEXT)
                ], style={**SUCCESS_MESSAGE, **NOTIFICATION_BASE})
                #, key=f'success-{time.time()}'
            ), None
        except ValueError as e:
            log_suspicious_activity('unknown', 'invalid_file', f'{filename}: {str(e)}')
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
                html.Div([
                    html.Span('❌ ', style=ICON_LARGE),
                    html.Span(f'Error: {str(e)}', style=ERROR_TEXT)
                ], style={**ERROR_MESSAGE, **NOTIFICATION_BASE})
                #, key=f'error-{time.time()}'
            ), None
        except Exception as e:
            log_suspicious_activity('unknown', 'parse_error', f'{filename}: {str(e)}')
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
                html.Div([
                    html.Span('❌ ', style=ICON_LARGE),
                    html.Span(f'Error loading {filename}: {str(e)}', style=ERROR_TEXT)
                ], style={**ERROR_MESSAGE, **NOTIFICATION_BASE})
                #, key=f'error-{time.time()}'
            ), None

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
            duration_text = [html.Span('⏱️', className='emoji-icon'), f" {hours}h {minutes}min"] if minutes > 0 else [html.Span('⏱️', className='emoji-icon'), f" {hours} hours"]
        elif time_val > 0:
            duration_text = [html.Span('⏱️', className='emoji-icon'), f" {time_val} minutes"]
        else:
            duration_text = [html.Span('🏁', className='emoji-icon'), f" {laps_val} laps"]
        
        server_name = race_info.get('server', '')
        track_name = race_info.get('track', 'Unknown')
        course_name = race_info.get('course', 'Unknown')
        track_length = race_info.get('track_length', '0')
        mech_fail = 'Yes' if race_info.get('mech_fail', '0') == '1' else 'No'
        tire_warmers = 'Yes' if race_info.get('tire_warmers', '0') == '1' else 'No'
        
        # Get country flag for the track
        country_flag, country_name = get_country_flag(track_name)
        flag_element = html.Img(src=f'https://flagcdn.com/w20/{country_flag.lower()}.png', 
                               title=country_name, 
                               className='country-flag',
                               style=FLAG_ICON) if country_flag else None
        
        track_info_content = [html.Span([html.Span('📍', className='emoji-icon'), " "], style=ICON_MARGIN)]
        track_info_content.append(flag_element)
        track_info_content.append(html.Span(f"{track_name} - {course_name}"))
        
        first_line = []
        if server_name and server_name != 'Unknown':
            first_line.append(html.Span([html.Span('🖥️', className='emoji-icon'), f" {server_name}"], style=ICON_MARGIN_20))
        first_line.extend([
            html.Span(track_info_content, style=ICON_MARGIN_20),
            html.Span([html.Span('📏', className='emoji-icon'), f" Track Length: {track_length}m"], style=ICON_MARGIN_20),
            html.Span([html.Span('📅', className='emoji-icon'), f" {race_info.get('date', 'Unknown')}"], style=ICON_MARGIN_20),
            html.Span(duration_text)
        ])
        
        return html.Div([
            html.Div(first_line),
            html.Div([
                html.Span([html.Span('🔧', className='emoji-icon'), f" Mech Fail: {mech_fail}"], style=ICON_MARGIN_20),
                html.Span([html.Span('💥', className='emoji-icon'), f" Damage: {race_info.get('damage_mult', '0')}%"], style=ICON_MARGIN_20),
                html.Span([html.Span('⛽', className='emoji-icon'), f" Fuel: {race_info.get('fuel_mult', '0')}x"], style=ICON_MARGIN_20),
                html.Span([html.Span('🛞', className='emoji-icon'), f" Tire: {race_info.get('tire_mult', '0')}x"], style=ICON_MARGIN_20),
                html.Span([html.Span('🔥', className='emoji-icon'), f" Warmers: {tire_warmers}"], style=ICON_MARGIN_20),
                html.Span([html.Span('🎮', className='emoji-icon'), f" Game Version: {race_info.get('game_version', 'Unknown')}"])
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
        th_style = {**TABLE_HEADER, 'textAlign': 'left'}
        td_style = {**TABLE_CELL_LEFT, 'padding': '10px 12px'}
        
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

    app.clientside_callback(
        """
        function(n_clicks_list) {
            var ctx = dash_clientside.callback_context;
            if (!ctx.triggered || !ctx.triggered[0].value) return dash_clientside.no_update;
            var triggerId = ctx.triggered[0].prop_id.split('.')[0];
            var idx;
            try { idx = JSON.parse(triggerId).index; } catch(e) { return dash_clientside.no_update; }
            var table = document.getElementById('file-list-table');
            if (!table) return dash_clientside.no_update;
            var rows = table.querySelectorAll('tbody tr');
            rows.forEach(function(row, i) {
                var bg = i % 2 === 0 ? '#ffffff' : '#e0e0e0';
                row.style.backgroundColor = bg;
                row.querySelectorAll('td').forEach(function(td) { td.style.backgroundColor = bg; });
            });
            if (rows[idx]) {
                rows[idx].style.backgroundColor = '#e8f4fd';
                rows[idx].querySelectorAll('td').forEach(function(td) { td.style.backgroundColor = '#e8f4fd'; });
            }
            return dash_clientside.no_update;
        }
        """,
        Output('folder-files-store', 'data', allow_duplicate=True),
        Input({'type': 'file-button', 'index': dash.dependencies.ALL}, 'n_clicks'),
        prevent_initial_call=True
    )

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
        performance_warning = html.P([html.Span('⚠️', className='emoji-icon'), ' Showing first 2000 laps for performance. Use filters to see specific data.'], 
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
    lap_row_counter = 0
    
    for _, row in lap_df.iterrows():
        # Add driver header row
        if current_driver != row['Driver']:
            current_driver = row['Driver']
            lap_row_counter = 0
            finish_pos = final_positions.get(row['Driver'], 'DNF')
            start_pos = starting_positions.get(row['Driver'], 'N/A')
            start_text = f" (Started P{int(start_pos)})" if start_pos != 'N/A' and start_pos > 0 else ""
            rows.append(html.Tr([
                html.Td(f"P{finish_pos} - {row['Driver']} - {row['Car']}{start_text}", colSpan=10, 
                       style={**td_style, 'backgroundColor': '#e9ecef', 'fontWeight': 'bold'})
            ]))
        
        row_bg = '#ffffff' if lap_row_counter % 2 == 0 else '#e0e0e0'
        lap_row_counter += 1
        td_row = {**td_style, 'backgroundColor': row_bg}
        
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
            html.Td(str(int(row['Lap'])), style=td_row),
            html.Td(lap_time_str, style=td_row),
            html.Td(s1_str, style=td_row),
            html.Td(s2_str, style=td_row),
            html.Td(s3_str, style=td_row),
            html.Td(ve_str, style=td_row),
            html.Td(fuel_str, style=td_row),
            html.Td(tire_wear_str, style=td_row),
            html.Td(compounds_str, style=td_row),
            html.Td(pit_str, style={**td_row, 'fontWeight': 'bold', 'color': 'red'})
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
                html.P([html.Span('ℹ️', className='emoji-icon'), ' Standings are affected only by Select Lap and Class filter. Other filters (Drivers, Team, Vehicle, Car Type) do not apply here.'], 
                       style={'fontSize': '12px', 'color': '#666', 'fontStyle': 'italic', 'margin': '0', 'paddingTop': '15px'})
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginLeft': '20px'})
        ], style={'marginBottom': '20px'}),
        dcc.Store(id='standings-filtered-data', data=data),
        html.Div(id='standings-table')
    ], style={'padding': '20px'})