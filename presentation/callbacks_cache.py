import os
import pickle
import base64
from data.parsers_secure import parse_xml_scores
from security.security import MAX_FILE_SIZE

CACHE_FILE = '.desktop_file_cache.pkl'

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(cache, f)
    except:
        pass

server_file_cache = load_cache()
server_metadata_cache = {}

def validate_file_size(decoded_content):
    file_size_mb = len(decoded_content) / (1024 * 1024)
    max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
    if file_size_mb > max_size_mb:
        return False, file_size_mb, f'File is too large ({file_size_mb:.1f}MB). Maximum allowed size is {max_size_mb:.0f}MB.'
    return True, file_size_mb, None

def extract_file_metadata(content):
    try:
        content_type, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        content_str = decoded.decode('utf-8')
        df, race_info, _ = parse_xml_scores(content_str)

        event_type = race_info.get('session', 'Race')
        circuit = race_info.get('track', 'Unknown')
        classes = ', '.join(sorted(df['Class'].unique())) if not df.empty else '-'
        num_cars = len(df['Driver'].unique()) if not df.empty else 0

        time_val = int(race_info.get('time', '0'))
        laps_val = int(race_info.get('laps', '0'))
        if time_val > 1000:
            hours = time_val // 3600
            minutes = (time_val % 3600) // 60
            duration = f"{hours}h {minutes}min" if minutes > 0 else f"{hours}h"
        elif time_val > 0:
            duration = f"{time_val}min"
        else:
            duration = f"{laps_val} laps"

        return {
            'event_type': event_type,
            'circuit': circuit,
            'classes': classes,
            'num_cars': num_cars,
            'duration': duration,
            'event_name': race_info.get('server', '-')
        }
    except:
        return None
