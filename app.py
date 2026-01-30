import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import xml.etree.ElementTree as ET
import pandas as pd
import base64
import io

app = dash.Dash(__name__)

def parse_xml(file_content):
    root = ET.fromstring(file_content)
    data = []
    
    for driver in root.findall('.//Driver'):
        driver_name = driver.get('Name')
        vehicle = driver.get('CarType', 'Unknown')
        car_class = driver.get('CarClass', 'GT3')
        
        for lap in driver.findall('.//Lap'):
            lap_num = int(lap.get('num', 0))
            position = int(lap.get('p', 0))
            lap_time = float(lap.get('et', 0))
            
            data.append({
                'Driver': driver_name,
                'Lap': lap_num,
                'Position': position,
                'Time': lap_time,
                'Vehicle': vehicle,
                'Class': car_class
            })
    
    return pd.DataFrame(data)

def parse_xml_scores(content):
    root = ET.fromstring(content)
    data = []
    race_info = {}
    
    # Extract race information
    race_results = root.find('.//RaceResults')
    if race_results is not None:
        race_info['track'] = race_results.find('TrackVenue')
        race_info['course'] = race_results.find('TrackCourse')
        race_info['date'] = race_results.find('TimeString')
        race_info['laps'] = race_results.find('RaceLaps')
        race_info['time'] = race_results.find('RaceTime')
        
        race_info = {
            'track': race_info['track'].text if race_info['track'] is not None else 'Unknown',
            'course': race_info['course'].text if race_info['course'] is not None else 'Unknown',
            'date': race_info['date'].text if race_info['date'] is not None else 'Unknown',
            'laps': race_info['laps'].text if race_info['laps'] is not None else '0',
            'time': race_info['time'].text if race_info['time'] is not None else '0'
        }
    
    for driver in root.findall('.//Driver'):
        driver_name = driver.find('Name')
        car_class = driver.find('CarClass')
        
        if driver_name is not None:
            name = driver_name.text
            car_cls = car_class.text if car_class is not None else 'GT3'
            
            for lap in driver.findall('.//Lap'):
                lap_num = int(lap.get('num', 0))
                position = int(lap.get('p', 0))
                et_text = lap.get('et', '0')
                
                try:
                    et = float(et_text) if et_text else 0
                except:
                    et = 0
                lap_time_text = lap.text
                
                if lap_num > 0 and position > 0:
                    lap_time = 0
                    if lap_time_text and lap_time_text.strip() not in ['--.----', '']:
                        try:
                            lap_time = float(lap_time_text)
                        except:
                            lap_time = 0
                    
                    data.append({
                        'Driver': name,
                        'Lap': lap_num,
                        'Position': position,
                        'ET': et,
                        'LapTime': lap_time,
                        'Class': car_cls
                    })
    
    df = pd.DataFrame(data)
    if not df.empty:
        leader_times = df.groupby('Lap')['ET'].min().reset_index()
        leader_times.columns = ['Lap', 'LeaderET']
        df = df.merge(leader_times, on='Lap')
        df['GapToLeader'] = df['ET'] - df['LeaderET']
        
        # Calculate gap to class leader
        class_leader_times = df.groupby(['Lap', 'Class'])['ET'].min().reset_index()
        class_leader_times.columns = ['Lap', 'Class', 'ClassLeaderET']
        df = df.merge(class_leader_times, on=['Lap', 'Class'])
        df['GapToClassLeader'] = df['ET'] - df['ClassLeaderET']
    
    return df, race_info

try:
    with open('/home/ebeninca/repo/race-graphs/2025_10_26_01_40_42-54R1.xml', 'r', encoding='utf-8') as f:
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
    
    dcc.Graph(id='position-chart'),
    dcc.Graph(id='gap-chart'),
    dcc.Graph(id='class-gap-chart'),
    dcc.Graph(id='laptime-chart'),
    
    dcc.Store(id='stored-data', data=initial_df.to_dict('records')),
    dcc.Store(id='stored-race-info', data=initial_race_info)
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
    
    # Convert to int safely
    try:
        time_val = int(race_time)
        laps_val = int(race_laps)
    except:
        time_val = 0
        laps_val = 0
    
    # If race time is in seconds (> 1000), convert to hours
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

@app.callback(
    Output('position-chart', 'figure'),
    [Input('stored-data', 'data'),
     Input('driver-filter', 'value'),
     Input('class-filter', 'value')]
)
def update_position_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df_pos = df.copy()
    
    if df_pos.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df_pos['Driver'].unique():
        driver_data = df_pos[df_pos['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['Position'],
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Position: %{y}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Driver Position by Lap',
        xaxis_title='Lap',
        yaxis_title='Position',
        yaxis=dict(autorange='reversed'),
        hovermode='closest',
        height=600
    )
    
    return fig

@app.callback(
    Output('gap-chart', 'figure'),
    [Input('stored-data', 'data'),
     Input('driver-filter', 'value'),
     Input('class-filter', 'value')]
)
def update_gap_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['GapToLeader'],
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Gap: %{y:.2f}s<extra></extra>'
        ))
    
    fig.update_layout(
        title='Gap to Leader by Lap',
        xaxis_title='Lap',
        yaxis_title='Gap to Leader (seconds)',
        hovermode='closest',
        height=600
    )
    
    return fig

@app.callback(
    Output('class-gap-chart', 'figure'),
    [Input('stored-data', 'data'),
     Input('driver-filter', 'value'),
     Input('class-filter', 'value')]
)
def update_class_gap_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['GapToClassLeader'],
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Gap: %{y:.2f}s<extra></extra>'
        ))
    
    fig.update_layout(
        title='Gap to Class Leader by Lap',
        xaxis_title='Lap',
        yaxis_title='Gap to Class Leader (seconds)',
        hovermode='closest',
        height=600
    )
    
    return fig

@app.callback(
    Output('laptime-chart', 'figure'),
    [Input('stored-data', 'data'),
     Input('driver-filter', 'value'),
     Input('class-filter', 'value')]
)
def update_laptime_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['LapTime'] > 0]
    
    if df.empty:
        return go.Figure().add_annotation(text="No lap time data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        minutes = (driver_data['LapTime'] // 60).astype(int)
        seconds = driver_data['LapTime'] % 60
        formatted_times = [f"{int(m):02d}:{s:06.3f}" for m, s in zip(minutes, seconds)]
        
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['LapTime'],
            mode='lines+markers',
            name=driver,
            text=formatted_times,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Time: %{text}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Lap Times',
        xaxis_title='Lap',
        yaxis_title='Lap Time (seconds)',
        hovermode='closest',
        height=600,
        yaxis=dict(
            tickmode='array',
            tickvals=[i*10 for i in range(int(df['LapTime'].min()//10), int(df['LapTime'].max()//10)+2)],
            ticktext=[f"{int(t//60):02d}:{int(t%60):02d}" for t in [i*10 for i in range(int(df['LapTime'].min()//10), int(df['LapTime'].max()//10)+2)]]
        )
    )
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0', port=7860)
