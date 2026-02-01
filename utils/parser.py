import xml.etree.ElementTree as ET
import pandas as pd


def parse_xml_scores(content):
    root = ET.fromstring(content)
    data = []
    race_info = {}
    incidents = {'chat': [], 'incident': [], 'penalty': []}
    
    # Extract chat messages
    for chat in root.findall('.//Chat'):
        incidents['chat'].append({
            'et': chat.get('et', '0'),
            'message': chat.text or ''
        })
    
    # Extract incidents
    for incident in root.findall('.//Incident'):
        incidents['incident'].append({
            'et': incident.get('et', '0'),
            'message': incident.text or ''
        })
    
    # Extract penalties
    for penalty in root.findall('.//Penalty'):
        incidents['penalty'].append({
            'et': penalty.get('et', '0'),
            'message': penalty.text or ''
        })
    
    # Extract race information
    race_results = root.find('.//RaceResults')
    if race_results is not None:
        race_info['track'] = race_results.find('TrackVenue')
        race_info['course'] = race_results.find('TrackCourse')
        race_info['date'] = race_results.find('TimeString')
        race_info['laps'] = race_results.find('RaceLaps')
        race_info['time'] = race_results.find('RaceTime')
        race_info['server'] = race_results.find('ServerName')
        race_info['track_length'] = race_results.find('TrackLength')
        race_info['mech_fail'] = race_results.find('MechFailRate')
        race_info['damage_mult'] = race_results.find('DamageMult')
        race_info['fuel_mult'] = race_results.find('FuelMult')
        race_info['tire_mult'] = race_results.find('TireMult')
        race_info['tire_warmers'] = race_results.find('TireWarmers')
        race_info['game_version'] = race_results.find('GameVersion')
        
        race_info = {
            'track': race_info['track'].text if race_info['track'] is not None else 'Unknown',
            'course': race_info['course'].text if race_info['course'] is not None else 'Unknown',
            'date': race_info['date'].text if race_info['date'] is not None else 'Unknown',
            'laps': race_info['laps'].text if race_info['laps'] is not None else '0',
            'time': race_info['time'].text if race_info['time'] is not None else '0',
            'server': race_info['server'].text if race_info['server'] is not None else 'Unknown',
            'track_length': race_info['track_length'].text if race_info['track_length'] is not None else '0',
            'mech_fail': race_info['mech_fail'].text if race_info['mech_fail'] is not None else '0',
            'damage_mult': race_info['damage_mult'].text if race_info['damage_mult'] is not None else '0',
            'fuel_mult': race_info['fuel_mult'].text if race_info['fuel_mult'] is not None else '0',
            'tire_mult': race_info['tire_mult'].text if race_info['tire_mult'] is not None else '0',
            'tire_warmers': race_info['tire_warmers'].text if race_info['tire_warmers'] is not None else '0',
            'game_version': race_info['game_version'].text if race_info['game_version'] is not None else 'Unknown'
        }
    
    for driver in root.findall('.//Driver'):
        driver_name = driver.find('Name')
        car_class = driver.find('CarClass')
        grid_pos = driver.find('GridPos')
        team_name = driver.find('TeamName')
        car_number = driver.find('CarNumber')
        veh_name = driver.find('VehName')
        car_type = driver.find('CarType')
        
        # Extract ControlAndAids
        control_aids = driver.find('ControlAndAids')
        aids_text = control_aids.text if control_aids is not None else ''
        
        if driver_name is not None:
            name = driver_name.text
            car_cls = car_class.text if car_class is not None else 'GT3'
            grid_position = int(grid_pos.text) if grid_pos is not None and grid_pos.text else 0
            team = team_name.text if team_name is not None else ''
            car_num = car_number.text if car_number is not None else ''
            car_id = f"{team} #{car_num}" if team and car_num else name
            vehicle_name = veh_name.text if veh_name is not None else ''
            vehicle_type = car_type.text if car_type is not None else ''
            
            # Parse aids
            aids_list = []
            if aids_text:
                for aid in aids_text.split(','):
                    aid = aid.strip()
                    if 'Clutch' in aid:
                        aids_list.append('C')
                    elif 'AutoBlip' in aid:
                        aids_list.append('B')
                    elif 'AutoLift' in aid:
                        aids_list.append('L')
            aids_display = '/'.join(aids_list) if aids_list else '-'
            
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
                    'Class': car_cls,
                    'Car': car_id,
                    'VehName': vehicle_name,
                    'CarType': vehicle_type,
                    'FCompound': '',
                    'RCompound': '',
                    'Aids': aids_display
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
                fcompound = lap.get('fcompound', '')
                rcompound = lap.get('rcompound', '')
                
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
                        'Class': car_cls,
                        'Car': car_id,
                        'VehName': vehicle_name,
                        'CarType': vehicle_type,
                        'FCompound': fcompound,
                        'RCompound': rcompound,
                        'Aids': aids_display
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
    
    return df, race_info, incidents
