import base64
import time
import dash
from dash import html, Input, Output, State, no_update
from data.parsers_secure import parse_xml_scores
from security.security import validate_upload, log_suspicious_activity
from presentation.styles import ERROR_MESSAGE, SUCCESS_MESSAGE, ERROR_TEXT, SUCCESS_TEXT, ICON_LARGE, NOTIFICATION_BASE
from presentation.callbacks_cache import validate_file_size


def register_upload_callbacks(app, initial_df, initial_race_info, initial_incidents):

    @app.callback(
        [Output('stored-data', 'data'),
         Output('stored-race-info', 'data'),
         Output('stored-incidents', 'data'),
         Output('upload-status', 'children'),
         Output('standings-lap-store', 'data', allow_duplicate=True)],
        [Input('upload-data', 'contents'), Input('app-mode', 'data')],
        [State('upload-data', 'filename')],
        prevent_initial_call=True
    )
    def update_data(contents, app_mode, filename):
        if app_mode == 'desktop':
            raise dash.exceptions.PreventUpdate
        if contents is None:
            return no_update, no_update, no_update, no_update, no_update
        try:
            content_type, content_string = contents.split(',')
            decoded = base64.b64decode(content_string)
            is_valid, file_size_mb, error_msg = validate_file_size(decoded)
            if not is_valid:
                log_suspicious_activity('unknown', 'large_file_upload', f'{filename}: {file_size_mb:.1f}MB')
                return no_update, no_update, no_update, html.Div(
                    html.Div([html.Span('❌ ', style=ICON_LARGE),
                              html.Span(f'{filename}: {error_msg}', style=ERROR_TEXT)],
                             style={**ERROR_MESSAGE, **NOTIFICATION_BASE}),
                    key=f'error-{time.time()}'), no_update
            safe_filename, content_str = validate_upload(decoded, filename)
            df, race_info, incidents = parse_xml_scores(content_str)
            return df.to_dict('records'), race_info, incidents, html.Div(
                html.Div([html.Span('✅ ', style=ICON_LARGE),
                          html.Span(f'{filename} loaded successfully!', style=SUCCESS_TEXT)],
                         style={**SUCCESS_MESSAGE, **NOTIFICATION_BASE}),
                key=f'success-{time.time()}'), None
        except ValueError as e:
            log_suspicious_activity('unknown', 'invalid_file', f'{filename}: {str(e)}')
            return no_update, no_update, no_update, html.Div(
                html.Div([html.Span('❌ ', style=ICON_LARGE),
                          html.Span(f'Error: {str(e)}', style=ERROR_TEXT)],
                         style={**ERROR_MESSAGE, **NOTIFICATION_BASE}),
                key=f'error-{time.time()}'), no_update
        except Exception as e:
            log_suspicious_activity('unknown', 'parse_error', f'{filename}: {str(e)}')
            return no_update, no_update, no_update, html.Div(
                html.Div([html.Span('❌ ', style=ICON_LARGE),
                          html.Span(f'Error loading {filename}: {str(e)}', style=ERROR_TEXT)],
                         style={**ERROR_MESSAGE, **NOTIFICATION_BASE}),
                key=f'error-{time.time()}'), no_update
