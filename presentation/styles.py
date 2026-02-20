"""CSS styles for Dash components"""

# Layout styles
CONTENT_PADDING = {'padding': '10px 20px 0 20px'}
EVENTS_PADDING = {'padding': '20px 40px'}

# Message styles
ERROR_MESSAGE = {
    'backgroundColor': '#f8d7da',
    'color': '#721c24',
    'padding': '15px',
    'borderRadius': '5px',
    'border': '1px solid #f5c6cb',
    'marginTop': '20px'
}

SUCCESS_MESSAGE = {
    'backgroundColor': '#d4edda',
    'color': '#155724',
    'padding': '15px',
    'borderRadius': '5px',
    'border': '1px solid #c3e6cb',
    'marginTop': '20px'
}

# Icon styles
ICON_LARGE = {'fontSize': '20px', 'marginRight': '10px'}
ICON_MARGIN = {'marginRight': '5px'}
ICON_MARGIN_20 = {'marginRight': '20px'}

# Text colors
ERROR_TEXT = {'color': '#721c24'}
SUCCESS_TEXT = {'color': '#155724'}

# Flag styles
FLAG_ICON = {'height': '16px', 'marginRight': '5px', 'verticalAlign': 'middle'}

# Table styles
TABLE_HEADER = {
    'backgroundColor': '#f8f9fa',
    'fontWeight': 'bold',
    'textAlign': 'center',
    'padding': '12px',
    'borderBottom': '2px solid #dee2e6'
}

TABLE_CELL = {
    'textAlign': 'center',
    'padding': '10px',
    'borderBottom': '1px solid #dee2e6'
}

TABLE_CELL_LEFT = {
    'textAlign': 'left',
    'padding': '10px',
    'borderBottom': '1px solid #dee2e6'
}

# Card styles
CARD_STYLE = {
    'marginBottom': '20px',
    'boxShadow': '0 2px 4px rgba(0,0,0,0.1)',
    'borderRadius': '8px'
}

# Event styles
EVENT_CHAT = {
    'padding': '8px 12px',
    'marginBottom': '8px',
    'backgroundColor': '#e3f2fd',
    'borderLeft': '3px solid #2196F3',
    'borderRadius': '4px'
}

EVENT_INCIDENT = {
    'padding': '8px 12px',
    'marginBottom': '8px',
    'backgroundColor': '#fff3cd',
    'borderLeft': '3px solid #ffc107',
    'borderRadius': '4px'
}

EVENT_PENALTY = {
    'padding': '8px 12px',
    'marginBottom': '8px',
    'backgroundColor': '#f8d7da',
    'borderLeft': '3px solid #dc3545',
    'borderRadius': '4px'
}

EVENT_TIME = {
    'fontWeight': 'bold',
    'marginRight': '10px',
    'color': '#666'
}

EVENT_DRIVER = {
    'fontWeight': 'bold',
    'color': '#333'
}

# Chart container
CHART_CONTAINER = {
    'height': '600px',
    'overflowY': 'auto'
}

# Notification styles (toast messages)
NOTIFICATION_BASE = {
    'position': 'fixed',
    'top': '20px',
    'left': '50%',
    'transform': 'translateX(-50%)',
    'zIndex': '9999',
    'boxShadow': '0 4px 8px rgba(0,0,0,0.2)',
    'minWidth': '300px',
    'maxWidth': '600px',
    'animation': 'fadeOut 1s ease-in 4s forwards'
}
