import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import base64
from utils.parser import parse_xml_scores
from utils.charts import (
    update_position_chart, update_gap_chart, update_class_gap_chart,
    update_laptime_chart, update_laptime_no_pit_chart,
    update_fuel_chart, update_ve_chart, update_tire_wear_chart,
    update_fuel_level_chart, update_ve_level_chart, update_tire_consumption_chart
)

app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

try:
    with open('/home/ebeninca/repo/rFactor2-lmu-graphs/2025_10_26_01_40_42-54R1.xml', 'r', encoding='utf-8') as f:
        initial_df, initial_race_info = parse_xml_scores(f.read())
except:
    initial_df = pd.DataFrame()
    initial_race_info = {}

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
        html.Label('Select Drivers:'),
        dcc.Dropdown(id='driver-filter', multi=True, placeholder='All Drivers'),
        
        html.Label('Select Class:'),
        dcc.Dropdown(id='class-filter', multi=True, placeholder='All Classes'),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
    
    dcc.Tabs(id='tabs', value='tab-position', children=[
        dcc.Tab(label='Position', value='tab-position'),
        dcc.Tab(label='Gap', value='tab-gap'),
        dcc.Tab(label='Lap Times', value='tab-laptimes'),
        dcc.Tab(label='Fuel', value='tab-fuel'),
        dcc.Tab(label='Tires', value='tab-tires')
    ]),
    
    dcc.Loading(
        id='loading-tabs',
        type='circle',
        parent_style={'position': 'relative', 'minHeight': '80px'},
        children=html.Div(id='tabs-content')
    ),
    
    dcc.Store(id='stored-data', data=initial_df.to_dict('records')),
    dcc.Store(id='stored-race-info', data=initial_race_info)
])

@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('stored-data', 'data'),
     Input('driver-filter', 'value'),
     Input('class-filter', 'value')]
)
def render_tab_content(active_tab, data, selected_drivers, selected_classes):
    if active_tab == 'tab-position':
        return dcc.Graph(id='position-chart', figure=update_position_chart(data, selected_drivers, selected_classes))
    elif active_tab == 'tab-gap':
        return html.Div([
            dcc.Graph(id='class-gap-chart', figure=update_class_gap_chart(data, selected_drivers, selected_classes)),
            dcc.Graph(id='gap-chart', figure=update_gap_chart(data, selected_drivers, selected_classes))
        ])
    elif active_tab == 'tab-laptimes':
        return html.Div([
            dcc.Graph(id='laptime-no-pit-chart', figure=update_laptime_no_pit_chart(data, selected_drivers, selected_classes)),
            dcc.Graph(id='laptime-chart', figure=update_laptime_chart(data, selected_drivers, selected_classes))
        ])
    elif active_tab == 'tab-fuel':
        return html.Div([
            dcc.Graph(id='fuel-level-chart', figure=update_fuel_level_chart(data, selected_drivers, selected_classes)),
            dcc.Graph(id='fuel-chart', figure=update_fuel_chart(data, selected_drivers, selected_classes)),
            dcc.Graph(id='ve-level-chart', figure=update_ve_level_chart(data, selected_drivers, selected_classes)),
            dcc.Graph(id='ve-chart', figure=update_ve_chart(data, selected_drivers, selected_classes))
        ])
    elif active_tab == 'tab-tires':
        return html.Div([
            dcc.Graph(id='tire-wear-chart', figure=update_tire_wear_chart(data, selected_drivers, selected_classes)),
            dcc.Graph(id='tire-consumption-chart', figure=update_tire_consumption_chart(data, selected_drivers, selected_classes))
        ])

@app.callback(
    [Output('stored-data', 'data'),
     Output('stored-race-info', 'data'),
     Output('upload-status', 'children')],
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def update_data(contents, filename):
    if contents is None:
        return initial_df.to_dict('records'), initial_race_info, ''
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    
    try:
        df, race_info = parse_xml_scores(decoded.decode('utf-8'))
        return df.to_dict('records'), race_info, html.Div(f'✓ {filename} loaded', style={'color': 'green'})
    except Exception as e:
        return initial_df.to_dict('records'), initial_race_info, html.Div(f'✗ Error: {str(e)}', style={'color': 'red'})

@app.callback(
    [Output('driver-filter', 'options'),
     Output('class-filter', 'options'),
     Output('driver-filter', 'value'),
     Output('class-filter', 'value')],
    Input('stored-data', 'data')
)
def update_filters(data):
    df = pd.DataFrame(data)
    if df.empty:
        return [], [], None, None
    
    drivers = [{'label': d, 'value': d} for d in sorted(df['Driver'].unique())]
    classes = [{'label': c, 'value': c} for c in sorted(df['Class'].unique())]
    
    return drivers, classes, None, None

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
    
    return html.Div([
        html.H3('Race Information', style={'marginBottom': '10px'}),
        html.Div([
            html.Span(f"📍 {race_info.get('track', 'Unknown')} - {race_info.get('course', 'Unknown')}", style={'marginRight': '20px'}),
            html.Span(f"📅 {race_info.get('date', 'Unknown')}", style={'marginRight': '20px'}),
            html.Span(duration_text)
        ])
    ])

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    app.run_server(debug=debug_mode, host='0.0.0.0', port=7860, dev_tools_props_check=False)
