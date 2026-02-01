import plotly.graph_objs as go
import pandas as pd


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
        
        # Format gap times as mm:ss.sss
        formatted_gaps = []
        for gap in driver_data['GapToLeader']:
            minutes = int(gap // 60)
            seconds = gap % 60
            formatted_gaps.append(f"{minutes}:{seconds:06.3f}")
        
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['GapToLeader'],
            mode='lines+markers',
            name=driver,
            text=formatted_gaps,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Gap: %{text}<extra></extra>'
        ))
    
    # Format y-axis ticks as mm:ss
    min_gap = df['GapToLeader'].min()
    max_gap = df['GapToLeader'].max()
    tick_interval = 30  # 30 seconds
    tick_vals = list(range(int(min_gap), int(max_gap) + tick_interval, tick_interval))
    tick_texts = [f"{int(t//60):01d}:{int(t%60):02d}" for t in tick_vals]
    
    fig.update_layout(
        title='Gap to Leader by Lap',
        xaxis_title='Lap',
        yaxis_title='Gap to Leader',
        hovermode='closest',
        height=600,
        yaxis=dict(
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_texts
        )
    )
    
    return fig


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
        
        # Format gap times as mm:ss.sss
        formatted_gaps = []
        for gap in driver_data['GapToClassLeader']:
            minutes = int(gap // 60)
            seconds = gap % 60
            formatted_gaps.append(f"{minutes}:{seconds:06.3f}")
        
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['GapToClassLeader'],
            mode='lines+markers',
            name=driver,
            text=formatted_gaps,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Gap: %{text}<extra></extra>'
        ))
    
    # Format y-axis ticks as mm:ss
    min_gap = df['GapToClassLeader'].min()
    max_gap = df['GapToClassLeader'].max()
    tick_interval = 30  # 30 seconds
    tick_vals = list(range(int(min_gap), int(max_gap) + tick_interval, tick_interval))
    tick_texts = [f"{int(t//60):01d}:{int(t%60):02d}" for t in tick_vals]
    
    fig.update_layout(
        title='Gap to Class Leader by Lap',
        xaxis_title='Lap',
        yaxis_title='Gap to Class Leader',
        hovermode='closest',
        height=600,
        yaxis=dict(
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_texts
        )
    )
    
    return fig


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


def update_laptime_no_pit_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    all_data = pd.DataFrame(data)
    exclude_set = set()
    for driver in all_data['Driver'].unique():
        driver_data = all_data[all_data['Driver'] == driver]
        pit_laps = driver_data[driver_data['IsPit'] == True]['Lap'].values
        for pit_lap in pit_laps:
            exclude_set.add((driver, pit_lap))
            exclude_set.add((driver, pit_lap + 1))
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['LapTime'] > 0].copy()
    df = df.sort_values(['Driver', 'Lap'])
    df = df[~df.apply(lambda row: (row['Driver'], row['Lap']) in exclude_set, axis=1)]
    
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
        title='Lap Times (Excluding Pit Laps)',
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


def update_fuel_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    all_data = pd.DataFrame(data)
    exclude_set = set()
    for driver in all_data['Driver'].unique():
        driver_data = all_data[all_data['Driver'] == driver]
        pit_laps = driver_data[driver_data['IsPit'] == True]['Lap'].values
        for pit_lap in pit_laps:
            exclude_set.add((driver, pit_lap + 1))
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['FuelUsed'] > 0]
    df = df[~df.apply(lambda row: (row['Driver'], row['Lap']) in exclude_set, axis=1)]
    
    if df.empty:
        return go.Figure().add_annotation(text="No fuel data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['FuelUsed'] * 100,
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Fuel: %{y:.2f}L<extra></extra>'
        ))
    
    fig.update_layout(
        title='Fuel Used per Lap',
        xaxis_title='Lap',
        yaxis_title='Fuel Used (Liters)',
        hovermode='closest',
        height=600
    )
    
    return fig


def update_ve_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    all_data = pd.DataFrame(data)
    exclude_set = set()
    for driver in all_data['Driver'].unique():
        driver_data = all_data[all_data['Driver'] == driver]
        pit_laps = driver_data[driver_data['IsPit'] == True]['Lap'].values
        for pit_lap in pit_laps:
            exclude_set.add((driver, pit_lap + 1))
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['VE'] > 0]
    df = df[~df.apply(lambda row: (row['Driver'], row['Lap']) in exclude_set, axis=1)]
    
    if df.empty:
        return go.Figure().add_annotation(text="No virtual energy data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['VE'] * 100,
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>VE: %{y:.2f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title='Virtual Energy per Lap',
        xaxis_title='Lap',
        yaxis_title='Virtual Energy (%)',
        hovermode='closest',
        height=600
    )
    
    return fig



def update_tire_wear_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    all_data = pd.DataFrame(data)
    exclude_set = set()
    for driver in all_data['Driver'].unique():
        driver_data = all_data[all_data['Driver'] == driver]
        pit_laps = driver_data[driver_data['IsPit'] == True]['Lap'].values
        for pit_lap in pit_laps:
            exclude_set.add((driver, pit_lap + 1))
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['TireWear'] > 0]
    df = df[~df.apply(lambda row: (row['Driver'], row['Lap']) in exclude_set, axis=1)]
    
    if df.empty:
        return go.Figure().add_annotation(text="No tire wear data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['TireWear'] * 100,
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Tire Wear: %{y:.2f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title='Tire Condition',
        xaxis_title='Lap',
        yaxis_title='Tire Wear (%)',
        hovermode='closest',
        height=600
    )
    
    return fig



def update_fuel_level_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['FuelLevel'] > 0]
    
    if df.empty:
        return go.Figure().add_annotation(text="No fuel level data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['FuelLevel'] * 100,
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Fuel: %{y:.2f}L<extra></extra>'
        ))
    
    fig.update_layout(
        title='Fuel Level',
        xaxis_title='Lap',
        yaxis_title='Fuel Level (Liters)',
        hovermode='closest',
        height=600
    )
    
    return fig


def update_ve_level_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['VELevel'] > 0]
    
    if df.empty:
        return go.Figure().add_annotation(text="No virtual energy level data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap')
        fig.add_trace(go.Scatter(
            x=driver_data['Lap'],
            y=driver_data['VELevel'] * 100,
            mode='lines+markers',
            name=driver,
            hovertemplate='%{fullData.name}<br>Lap: %{x}<br>VE: %{y:.2f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title='Virtual Energy Level',
        xaxis_title='Lap',
        yaxis_title='Virtual Energy Level (%)',
        hovermode='closest',
        height=600
    )
    
    return fig


def update_tire_consumption_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    all_data = pd.DataFrame(data)
    exclude_set = set()
    for driver in all_data['Driver'].unique():
        driver_data = all_data[all_data['Driver'] == driver]
        pit_laps = driver_data[driver_data['IsPit'] == True]['Lap'].values
        for pit_lap in pit_laps:
            exclude_set.add((driver, pit_lap + 1))
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['TireWear'] > 0]
    df = df[~df.apply(lambda row: (row['Driver'], row['Lap']) in exclude_set, axis=1)]
    
    if df.empty:
        return go.Figure().add_annotation(text="No tire data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver].sort_values('Lap').reset_index(drop=True)
        
        if len(driver_data) < 2:
            continue
        
        consumption = []
        laps = []
        
        for i in range(len(driver_data) - 1):
            wear_n = driver_data.loc[i, 'TireWear']
            wear_n1 = driver_data.loc[i + 1, 'TireWear']
            cons = (wear_n - wear_n1) * 100
            if cons >= 0:
                consumption.append(cons)
                laps.append(driver_data.loc[i, 'Lap'])
        
        if consumption:
            fig.add_trace(go.Scatter(
                x=laps,
                y=consumption,
                mode='lines+markers',
                name=driver,
                hovertemplate='%{fullData.name}<br>Lap: %{x}<br>Consumption: %{y:.3f}%<extra></extra>'
            ))
    
    fig.update_layout(
        title='Average Tire Wear per Lap',
        xaxis_title='Lap',
        yaxis_title='Tire Consumption (%)',
        hovermode='closest',
        height=600
    )
    
    return fig


def update_tire_degradation_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    all_data = pd.DataFrame(data)
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[(df['TireWear'] > 0) & (df['LapTime'] > 0)].copy()
    
    if df.empty:
        return go.Figure().add_annotation(text="No tire or lap time data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = all_data[all_data['Driver'] == driver].sort_values('Lap')
        pit_laps = driver_data[driver_data['IsPit'] == True]['Lap'].values
        
        exclude_laps = set()
        for pit_lap in pit_laps:
            exclude_laps.add(pit_lap)
            exclude_laps.add(pit_lap + 1)
        
        stints = []
        current_stint = []
        
        for idx, row in driver_data.iterrows():
            if row['Lap'] in pit_laps:
                if current_stint:
                    stints.append(pd.DataFrame(current_stint))
                current_stint = []
            elif row['Lap'] not in exclude_laps and row['TireWear'] > 0 and row['LapTime'] > 0:
                current_stint.append(row)
        
        if current_stint:
            stints.append(pd.DataFrame(current_stint))
        
        for stint_idx, stint_df in enumerate(stints):
            if len(stint_df) < 2:
                continue
            
            if driver not in [d for d in (selected_drivers or [])] and selected_drivers:
                continue
            
            best_lap = stint_df['LapTime'].min()
            stint_df['Delta'] = stint_df['LapTime'] - best_lap
            stint_df['TireDeg'] = (1 - stint_df['TireWear']) * 100
            
            fig.add_trace(go.Scatter(
                x=stint_df['TireDeg'],
                y=stint_df['Delta'],
                mode='markers+lines',
                name=f"{driver} - Stint {stint_idx + 1}",
                hovertemplate='%{fullData.name}<br>Tire Deg: %{x:.1f}%<br>Delta: +%{y:.3f}s<extra></extra>'
            ))
    
    fig.update_layout(
        title='Lap Time Delta vs Tire Degradation',
        xaxis_title='Tire Degradation (%)',
        yaxis_title='Delta to Best Lap (seconds)',
        hovermode='closest',
        height=600
    )
    
    return fig


def update_consistency_chart(data, selected_drivers, selected_classes):
    df = pd.DataFrame(data)
    
    if df.empty:
        return go.Figure().add_annotation(text="No data available", showarrow=False)
    
    all_data = pd.DataFrame(data)
    exclude_set = set()
    for driver in all_data['Driver'].unique():
        driver_data = all_data[all_data['Driver'] == driver]
        pit_laps = driver_data[driver_data['IsPit'] == True]['Lap'].values
        for pit_lap in pit_laps:
            exclude_set.add((driver, pit_lap))
            exclude_set.add((driver, pit_lap + 1))
    
    if selected_drivers:
        df = df[df['Driver'].isin(selected_drivers)]
    if selected_classes:
        df = df[df['Class'].isin(selected_classes)]
    
    df = df[df['LapTime'] > 0].copy()
    df = df[~df.apply(lambda row: (row['Driver'], row['Lap']) in exclude_set, axis=1)]
    
    if df.empty:
        return go.Figure().add_annotation(text="No lap time data available", showarrow=False)
    
    fig = go.Figure()
    
    for driver in df['Driver'].unique():
        driver_data = df[df['Driver'] == driver]['LapTime']
        
        if len(driver_data) < 2:
            continue
        
        formatted_times = [f"{int(t//60):01d}:{int(t%60):02d}.{int((t%1)*1000):03d}" for t in driver_data]
        
        fig.add_trace(go.Box(
            y=driver_data,
            name=driver,
            boxmean='sd',
            text=formatted_times,
            hovertemplate='%{text}<extra></extra>'
        ))
    
    min_time = df['LapTime'].min()
    max_time = df['LapTime'].max()
    tick_interval = 5
    tick_vals = list(range(int(min_time), int(max_time) + tick_interval, tick_interval))
    tick_texts = [f"{int(t//60):01d}:{int(t%60):02d}.{int((t%1)*1000):03d}" for t in tick_vals]
    
    fig.update_layout(
        title='Lap Time Consistency by Driver',
        xaxis_title='Driver',
        yaxis_title='Lap Time',
        hovermode='closest',
        height=600,
        yaxis=dict(
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_texts
        )
    )
    
    return fig
