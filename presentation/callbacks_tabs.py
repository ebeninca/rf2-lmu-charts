import pandas as pd
import dash
from dash import html, dcc, Input, Output, State
from business.analytics import (
    update_position_chart, update_gap_chart, update_class_gap_chart,
    update_laptime_chart, update_laptime_no_pit_chart,
    update_fuel_chart, update_ve_chart, update_tire_wear_chart,
    update_fuel_level_chart, update_ve_level_chart, update_tire_consumption_chart,
    update_consistency_chart, update_tire_degradation_chart, update_pace_decay_chart,
    update_strategy_gantt_chart
)
from presentation.styles import CONTENT_PADDING, EVENTS_PADDING, TABLE_HEADER, TABLE_CELL_LEFT
from presentation.components import create_standings_table


def register_tab_callbacks(app):

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
        if active_tab == 'tab-standings' and ctx.triggered:
            trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if trigger_id in ['driver-filter', 'car-filter', 'veh-filter', 'cartype-filter']:
                raise dash.exceptions.PreventUpdate
        df = pd.DataFrame(data)
        if active_tab == 'tab-standings':
            if selected_classes:
                df = df[df['Class'].isin(selected_classes)]
            data = df.to_dict('records')
        elif not df.empty:
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
        Output('events-content', 'children'),
        [Input('events-tabs', 'value'), Input('stored-incidents', 'data')]
    )
    def render_events_content(active_events_tab, incidents):
        table_style = {'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '14px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}
        th_style = {**TABLE_HEADER, 'textAlign': 'left'}
        td_style = {**TABLE_CELL_LEFT, 'padding': '10px 12px'}
        key = {'events-chat': 'chat', 'events-incidents': 'incident', 'events-penalties': 'penalty'}.get(active_events_tab, 'chat')
        label = {'events-chat': 'chat messages', 'events-incidents': 'incidents', 'events-penalties': 'penalties'}.get(active_events_tab, '')
        messages = incidents.get(key, [])
        if not messages:
            return html.P(f'No {label}')
        return html.Table([
            html.Thead(html.Tr([html.Th('Time', style=th_style), html.Th('Message', style=th_style)])),
            html.Tbody([html.Tr([html.Td(f"{msg['et']}s", style=td_style), html.Td(msg['message'], style=td_style)]) for msg in messages])
        ], style=table_style)

    @app.callback(Output('standings-lap-store', 'data'), Input('standings-lap-selector', 'value'))
    def store_selected_lap(selected_lap):
        return selected_lap

    @app.callback(
        Output('standings-table', 'children'),
        [Input('standings-lap-selector', 'value'), Input('standings-filtered-data', 'data')]
    )
    def update_standings_table(selected_lap, data):
        return create_standings_table(selected_lap, data)

    @app.callback(Output('laptimes-tab-store', 'data'), Input('laptimes-tabs', 'value'))
    def store_laptimes_tab(selected_tab):
        return selected_tab

    @app.callback(
        Output('laptimes-tabs', 'value'),
        [Input('stored-data', 'data'), Input('driver-filter', 'value'), Input('class-filter', 'value'),
         Input('car-filter', 'value'), Input('veh-filter', 'value'), Input('cartype-filter', 'value')],
        [State('laptimes-tab-store', 'data')]
    )
    def restore_laptimes_tab(data, selected_drivers, selected_classes, selected_cars, selected_veh, selected_cartype, stored_tab):
        return stored_tab

    @app.callback(Output('events-tab-store', 'data'), Input('events-tabs', 'value'))
    def store_events_tab(selected_tab):
        return selected_tab

    @app.callback(
        Output('events-tabs', 'value'),
        [Input('stored-data', 'data'), Input('class-filter', 'value')],
        [State('events-tab-store', 'data')]
    )
    def restore_events_tab(data, selected_classes, stored_tab):
        return stored_tab


def _render_standings_tab(data, stored_lap):
    all_df = pd.DataFrame(data)
    if all_df.empty:
        return html.P('No data available')
    max_lap = int(all_df['Lap'].max())
    lap_options = [{'label': f'Lap {i}', 'value': i} for i in range(0, max_lap + 1)]
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


def _create_laptimes_table(df):
    if df.empty:
        return html.P('No data available')
    lap_df = df[(df['Lap'] > 0) & (df['LapTime'] > 0)].copy()
    if lap_df.empty:
        return html.P('No lap time data available')
    performance_warning = None
    if len(lap_df) > 2000:
        lap_df = lap_df.head(2000)
        performance_warning = html.P([html.Span('⚠️', className='emoji-icon'), ' Showing first 2000 laps for performance. Use filters to see specific data.'],
                                     style={'color': '#ff6b35', 'fontSize': '12px', 'fontStyle': 'italic', 'marginBottom': '10px'})
    last_lap_df = lap_df.groupby('Driver')['Lap'].max().reset_index().merge(lap_df, on=['Driver', 'Lap'])
    finishing_order = last_lap_df.sort_values('Position')['Driver'].tolist()
    final_positions = {driver: pos + 1 for pos, driver in enumerate(finishing_order)}
    starting_positions = df[df['Lap'] == 0].set_index('Driver')['Position'].to_dict()
    lap_df['FinishOrder'] = lap_df['Driver'].map({driver: i for i, driver in enumerate(finishing_order)})
    lap_df = lap_df.sort_values(['FinishOrder', 'Lap'])
    table_style = {'width': '100%', 'borderCollapse': 'collapse', 'fontSize': '13px'}
    th_style = {'textAlign': 'left', 'padding': '8px', 'backgroundColor': '#f8f9fa', 'borderBottom': '2px solid #dee2e6', 'fontWeight': '600'}
    td_style = {'padding': '6px 8px', 'borderBottom': '1px solid #e9ecef'}
    rows = []
    current_driver = None
    lap_row_counter = 0
    for _, row in lap_df.iterrows():
        if current_driver != row['Driver']:
            current_driver = row['Driver']
            lap_row_counter = 0
            finish_pos = final_positions.get(row['Driver'], 'DNF')
            start_pos = starting_positions.get(row['Driver'], 'N/A')
            start_text = f" (Started P{int(start_pos)})" if start_pos != 'N/A' and start_pos > 0 else ""
            rows.append(html.Tr([html.Td(f"P{finish_pos} - {row['Driver']} - {row['Car']}{start_text}", colSpan=10,
                                         style={**td_style, 'backgroundColor': '#e9ecef', 'fontWeight': 'bold'})]))
        row_bg = '#ffffff' if lap_row_counter % 2 == 0 else '#e0e0e0'
        lap_row_counter += 1
        td_row = {**td_style, 'backgroundColor': row_bg}
        lap_time = row['LapTime']
        minutes = int(lap_time // 60)
        seconds = lap_time % 60
        lap_time_str = f"{minutes}:{seconds:06.3f}"
        s1, s2, s3 = row.get('S1', 0), row.get('S2', 0), row.get('S3', 0)
        ve_str = f"{row.get('VE', 0):.1%}" if row.get('VE', 0) > 0 else ''
        fuel_str = f"{row['FuelLevel']:.1%}" if row['FuelLevel'] > 0 else '-'
        twfl, twfr, twrl, twrr = row.get('TWFL', 0), row.get('TWFR', 0), row.get('TWRL', 0), row.get('TWRR', 0)
        tire_wear_str = f"FL:{twfl:.0%} FR:{twfr:.0%} RL:{twrl:.0%} RR:{twrr:.0%}" if any([twfl, twfr, twrl, twrr]) else '-'
        fcompound = row.get('FCompound', '').split(',')[-1] if row.get('FCompound') else '-'
        rcompound = row.get('RCompound', '').split(',')[-1] if row.get('RCompound') else '-'
        rows.append(html.Tr([
            html.Td(str(int(row['Lap'])), style=td_row),
            html.Td(lap_time_str, style=td_row),
            html.Td(f"{s1:.3f}" if s1 > 0 else '-', style=td_row),
            html.Td(f"{s2:.3f}" if s2 > 0 else '-', style=td_row),
            html.Td(f"{s3:.3f}" if s3 > 0 else '-', style=td_row),
            html.Td(ve_str, style=td_row),
            html.Td(fuel_str, style=td_row),
            html.Td(tire_wear_str, style=td_row),
            html.Td(f"{fcompound}/{rcompound}", style=td_row),
            html.Td('PIT' if row.get('IsPit', False) else '', style={**td_row, 'fontWeight': 'bold', 'color': 'red'})
        ]))
    table_content = [html.Table([
        html.Thead(html.Tr([
            html.Th('Lap', style=th_style), html.Th('Lap Time', style=th_style),
            html.Th('S1', style=th_style), html.Th('S2', style=th_style), html.Th('S3', style=th_style),
            html.Th('VE', style=th_style), html.Th('Fuel', style=th_style),
            html.Th('Tire Wear', style=th_style), html.Th('Tires Compound', style=th_style), html.Th('Pit', style=th_style)
        ])),
        html.Tbody(rows)
    ], style=table_style)]
    if performance_warning:
        table_content.insert(0, performance_warning)
    return html.Div(table_content, style={'padding': '20px 40px'})
