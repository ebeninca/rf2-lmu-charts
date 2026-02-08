import dash
import pandas as pd
import os
import sys
from data.parsers import parse_xml_scores
from presentation.layouts import create_main_layout
from presentation.callbacks import register_callbacks

# Get base path for PyInstaller
if getattr(sys, 'frozen', False):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

# Initialize Dash app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Load custom HTML template
with open(os.path.join(base_path, 'assets/index.html'), 'r') as f:
    app.index_string = f.read()

# Load initial data
try:
    xml_path = os.path.join(base_path, 'samples/2025_anonymized.xmlx')
    with open(xml_path, 'r', encoding='utf-8') as f:
        initial_df, initial_race_info, initial_incidents = parse_xml_scores(f.read())
except:
    initial_df = pd.DataFrame()
    initial_race_info = {}
    initial_incidents = {'chat': [], 'incident': [], 'penalty': []}

# Create layout
app.layout = create_main_layout(initial_df, initial_race_info, initial_incidents)

# Register callbacks
register_callbacks(app, initial_df, initial_race_info, initial_incidents)

if __name__ == '__main__':
    
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    
    if debug_mode:
        app.run(debug=True, host='0.0.0.0', port=7860, dev_tools_hot_reload=True)
    else:
        from waitress import serve
        print('Dash is running on http://0.0.0.0:7860/ (Waitress)')
        serve(app.server, host='0.0.0.0', port=7860, threads=4, channel_timeout=120)