import xml.etree.ElementTree as ET
import pandas as pd


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
        grid_pos = driver.find('GridPos')
        
        if driver_name is not None:
            name = driver_name.text
            car_cls = car_class.text if car_class is not None else 'GT3'
            grid_position = int(grid_pos.text) if grid_pos is not None and grid_pos.text else 0
            
            # Add lap 0 with GridPos
            if grid_position > 0:
                data.append({
                    'Driver': name,
                    'Lap': 0,
                    'Position': grid_position,
                    'ET': 0,
                    'LapTime': 0,
                    'IsPit': False,
                    'FuelUsed': 0,
                    'FuelLevel': 0,
                    'VE': 0,
                    'VELevel': 0,
                    'TireWear': 0,
                    'Class': car_cls
                })
            
            for lap in driver.findall('.//Lap'):
                lap_num = int(lap.get('num', 0))
                position = int(lap.get('p', 0))
                et_text = lap.get('et', '0')
                is_pit = lap.get('pit', '0') == '1'
                fuel_used = lap.get('fuelUsed', '0')
                fuel_level = lap.get('fuel', '0')
                ve = lap.get('veUsed', '0')
                ve_level = lap.get('ve', '0')
                twfl = lap.get('twfl', '0')
                twfr = lap.get('twfr', '0')
                twrl = lap.get('twrl', '0')
                twrr = lap.get('twrr', '0')
                
                try:
                    et = float(et_text) if et_text else 0
                except:
                    et = 0
                lap_time_text = lap.text
                
                if lap_num > 0 and position > 0 and position <= 99:
                    lap_time = 0
                    if lap_time_text and lap_time_text.strip() not in ['--.----', '']:
                        try:
                            lap_time = float(lap_time_text)
                        except:
                            lap_time = 0
                    
                    try:
                        fuel = float(fuel_used) if fuel_used else 0
                    except:
                        fuel = 0
                    
                    try:
                        fuel_lvl = float(fuel_level) if fuel_level else 0
                    except:
                        fuel_lvl = 0
                    
                    try:
                        virtual_energy = float(ve) if ve else 0
                    except:
                        virtual_energy = 0
                    
                    try:
                        ve_lvl = float(ve_level) if ve_level else 0
                    except:
                        ve_lvl = 0
                    
                    # Calculate average tire wear
                    tire_values = []
                    for tw in [twfl, twfr, twrl, twrr]:
                        try:
                            val = float(tw) if tw else 0
                            if val > 0:
                                tire_values.append(val)
                        except:
                            pass
                    tire_wear = sum(tire_values) / len(tire_values) if tire_values else 0
                    
                    data.append({
                        'Driver': name,
                        'Lap': lap_num,
                        'Position': position,
                        'ET': et,
                        'LapTime': lap_time,
                        'IsPit': is_pit,
                        'FuelUsed': fuel,
                        'FuelLevel': fuel_lvl,
                        'VE': virtual_energy,
                        'VELevel': ve_lvl,
                        'TireWear': tire_wear,
                        'Class': car_cls
                    })
    
    df = pd.DataFrame(data)
    if not df.empty:
        leader_times = df.groupby('Lap')['ET'].min().reset_index()
        leader_times.columns = ['Lap', 'LeaderET']
        df = df.merge(leader_times, on='Lap')
        df['GapToLeader'] = df['ET'] - df['LeaderET']
        
        class_leader_times = df.groupby(['Lap', 'Class'])['ET'].min().reset_index()
        class_leader_times.columns = ['Lap', 'Class', 'ClassLeaderET']
        df = df.merge(class_leader_times, on=['Lap', 'Class'])
        df['GapToClassLeader'] = df['ET'] - df['ClassLeaderET']
    
    return df, race_info
