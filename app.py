import dash
import pandas as pd
import os
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
    xml_path = os.path.join(os.path.dirname(__file__), 'samples/2025_anonymized.xmlx')
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
    import os
    debug_mode = os.environ.get('DEBUG', 'False') == 'True'
    app.run(debug=debug_mode, host='0.0.0.0', port=7860)