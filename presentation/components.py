from dash import html
import pandas as pd

def create_standings_table(selected_lap, data):
    """Cria a tabela de standings"""
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
            html.Th(['Tires ', html.Span('🛞', className='emoji-icon')], style=th_style, title='Tires used during the selected lap (Front/Rear)'),
            html.Th(['Aids ', html.Span('ℹ️', className='emoji-icon')], style=th_style, title='TC=Traction Control, ABS=Anti-lock Brakes, SC=Stability Control, AS=Auto Shift, AC=Auto Clutch, AB=Auto Blip, AL=Auto Lift, PC=Player Control')
        ])),
        html.Tbody(rows)
    ], style=table_style)