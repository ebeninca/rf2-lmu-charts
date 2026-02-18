import json
import base64
import dash
from dash import html, Input, Output, State, no_update
from presentation.styles import ERROR_MESSAGE, ERROR_TEXT, SUCCESS_MESSAGE, SUCCESS_TEXT, ICON_LARGE, NOTIFICATION_BASE
from presentation.callbacks_cache import (
    server_file_cache, server_metadata_cache,
    save_cache, extract_file_metadata, validate_file_size, CACHE_FILE
)
import time
import os
from security.security import validate_upload
from data.parsers_secure import parse_xml_scores

TH = {'padding': '8px', 'textAlign': 'left', 'borderBottom': '2px solid #ddd'}
TH_CENTER = {'padding': '8px', 'textAlign': 'center', 'borderBottom': '2px solid #ddd'}

def _build_file_list(xml_files):
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
                html.Td(html.Button(filename, id={'type': 'file-button', 'index': i}, n_clicks=0,
                    style={'cursor': 'pointer', 'border': 'none', 'background': 'none',
                           'color': '#0066cc', 'textDecoration': 'underline', 'padding': '0'}), style=td()),
                html.Td(meta['event_type'], style=td()),
                html.Td(meta['circuit'], style=td()),
                html.Td(meta['classes'], style=td({'fontSize': '12px'})),
                html.Td(str(meta['num_cars']), style=td({'textAlign': 'center'})),
                html.Td(meta['duration'], style=td()),
                html.Td(meta['event_name'], style=td({'fontSize': '12px'}))
            ]))

    return html.Div([
        html.Div([
            html.H3('Select a file:', style={'fontSize': '15px', 'margin': '0'}),
            html.A('🗑️ Clear Cache', href='/clear-cache', style={'fontSize': '12px', 'padding': '3px 8px'})
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'marginBottom': '10px'}),
        html.Table([
            html.Thead(html.Tr([
                html.Th('File', style=TH), html.Th('Type', style=TH),
                html.Th('Circuit', style=TH), html.Th('Classes', style=TH),
                html.Th('Cars', style=TH_CENTER), html.Th('Duration', style=TH),
                html.Th('Event', style=TH)
            ])),
            html.Tbody(rows)
        ], id='file-list-table', style={'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '13px'})
    ], style={'padding': '10px', 'border': '1px solid #ddd', 'borderRadius': '5px',
              'marginTop': '10px', 'maxHeight': '200px', 'overflowY': 'auto'})


def _initialize_cache(app_mode, current_store):
    if app_mode == 'desktop' and not current_store and server_file_cache:
        return sorted(server_file_cache.keys(), reverse=True)
    return current_store if current_store else None


def _restore_last_folder(last_folder_data, app_mode):
    if app_mode != 'desktop':
        return None, None, {'display': 'none'}, no_update
    xml_files = sorted([f for f in (last_folder_data or []) if f in server_file_cache] or server_file_cache.keys(), reverse=True)
    if not xml_files:
        return None, None, {'display': 'none'}, None
    return xml_files, _build_file_list(xml_files), {'display': 'block'}, xml_files


def _handle_folder_upload(contents_list, app_mode, filenames_list):
    if app_mode != 'desktop' or not contents_list:
        return None, None, {'display': 'none'}, '', None
    for content, filename in zip(contents_list, filenames_list):
        if filename.lower().endswith(('.xml', '.xmlx')):
            server_file_cache[filename] = content
            server_metadata_cache[filename] = extract_file_metadata(content)
    xml_filenames = sorted(server_file_cache.keys(), reverse=True)
    save_cache(server_file_cache)
    if not xml_filenames:
        return None, None, {'display': 'none'}, html.Div(
            html.Div([html.Span('❌ ', style=ICON_LARGE),
                      html.Span('No XML files found in folder', style=ERROR_TEXT)],
                     style={**ERROR_MESSAGE, **NOTIFICATION_BASE})), None
    return xml_filenames, _build_file_list(xml_filenames), {'display': 'block'}, '', xml_filenames


def _load_selected_file(n_clicks_list, xml_filenames, app_mode, initial_df, initial_race_info, initial_incidents):
    if app_mode != 'desktop' or not xml_filenames:
        raise dash.exceptions.PreventUpdate
    ctx = dash.callback_context
    if not ctx.triggered or not ctx.triggered[0]['value']:
        raise dash.exceptions.PreventUpdate
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    clicked_idx = json.loads(trigger_id)['index']
    if clicked_idx is None or clicked_idx >= len(xml_filenames):
        raise dash.exceptions.PreventUpdate
    filename = xml_filenames[clicked_idx]
    content = server_file_cache.get(filename)
    if not content:
        return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
            html.Div([html.Span('❌ ', style=ICON_LARGE),
                      html.Span(f'{filename}: File not found in cache', style=ERROR_TEXT)],
                     style={**ERROR_MESSAGE, **NOTIFICATION_BASE})), None
    try:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        is_valid, file_size_mb, error_msg = validate_file_size(decoded)
        if not is_valid:
            return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
                html.Div([html.Span('❌ ', style=ICON_LARGE),
                          html.Span(f'{filename}: {error_msg}', style=ERROR_TEXT)],
                         style={**ERROR_MESSAGE, **NOTIFICATION_BASE}),
                key=f'error-{time.time()}'), None
        safe_filename, content_str = validate_upload(decoded, filename)
        df, race_info, incidents = parse_xml_scores(content_str)
        return df.to_dict('records'), race_info, incidents, html.Div(
            html.Div([html.Span('✅ ', style=ICON_LARGE),
                      html.Span(f'{filename} loaded successfully!', style=SUCCESS_TEXT)],
                     style={**SUCCESS_MESSAGE, **NOTIFICATION_BASE}),
            key=f'success-{time.time()}'), None
    except Exception as e:
        return initial_df.to_dict('records'), initial_race_info, initial_incidents, html.Div(
            html.Div([html.Span('❌ ', style=ICON_LARGE),
                      html.Span(f'Error loading {filename}: {str(e)}', style=ERROR_TEXT)],
                     style={**ERROR_MESSAGE, **NOTIFICATION_BASE})), None


def register_desktop_callbacks(app, initial_df, initial_race_info, initial_incidents):

    @app.callback(
        Output('last-folder-store', 'data', allow_duplicate=True),
        Input('app-mode', 'data'),
        State('last-folder-store', 'data'),
        prevent_initial_call='initial_duplicate'
    )
    def initialize_cache(app_mode, current_store):
        return _initialize_cache(app_mode, current_store)

    @app.callback(
        [Output('folder-files-store', 'data', allow_duplicate=True),
         Output('file-list-container', 'children', allow_duplicate=True),
         Output('file-list-container', 'style', allow_duplicate=True),
         Output('last-folder-store', 'data', allow_duplicate=True)],
        [Input('last-folder-store', 'data'), Input('app-mode', 'data')],
        prevent_initial_call='initial_duplicate'
    )
    def restore_last_folder(last_folder_data, app_mode):
        return _restore_last_folder(last_folder_data, app_mode)

    @app.callback(
        [Output('folder-files-store', 'data'),
         Output('file-list-container', 'children'),
         Output('file-list-container', 'style'),
         Output('upload-status', 'children', allow_duplicate=True),
         Output('last-folder-store', 'data')],
        [Input('upload-data', 'contents'), Input('app-mode', 'data')],
        [State('upload-data', 'filename')],
        prevent_initial_call=True
    )
    def handle_folder_upload(contents_list, app_mode, filenames_list):
        return _handle_folder_upload(contents_list, app_mode, filenames_list)

    @app.callback(
        [Output('stored-data', 'data', allow_duplicate=True),
         Output('stored-race-info', 'data', allow_duplicate=True),
         Output('stored-incidents', 'data', allow_duplicate=True),
         Output('upload-status', 'children', allow_duplicate=True),
         Output('standings-lap-store', 'data', allow_duplicate=True)],
        [Input({'type': 'file-button', 'index': dash.dependencies.ALL}, 'n_clicks')],
        [State('folder-files-store', 'data'), State('app-mode', 'data')],
        prevent_initial_call=True
    )
    def load_selected_file(n_clicks_list, xml_filenames, app_mode):
        return _load_selected_file(n_clicks_list, xml_filenames, app_mode, initial_df, initial_race_info, initial_incidents)

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
