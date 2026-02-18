import pandas as pd
from dash import html, Input, Output
from data.track_flags import get_country_flag
from presentation.styles import ICON_MARGIN, ICON_MARGIN_20, FLAG_ICON


def register_filter_callbacks(app):

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
        country_flag, country_name = get_country_flag(track_name)
        flag_element = html.Img(src=f'https://flagcdn.com/w20/{country_flag.lower()}.png',
                                title=country_name, className='country-flag', style=FLAG_ICON) if country_flag else None
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
