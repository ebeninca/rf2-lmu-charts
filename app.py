import dash
import pandas as pd
from data.parsers import parse_xml_scores
from presentation.layouts import create_main_layout
from presentation.callbacks import register_callbacks

# Initialize Dash app
app = dash.Dash(__name__)
app.config.suppress_callback_exceptions = True

# Load custom HTML template
with open('assets/index.html', 'r') as f:
    app.index_string = f.read()

# Load initial data
try:
    with open('/home/ebeninca/repo/rFactor2-lmu-graphs/2026_01_31_17_55_01-49R1.xml', 'r', encoding='utf-8') as f:
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
    import os
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    app.run_server(debug=debug_mode, host='0.0.0.0', port=7860, dev_tools_props_check=False)