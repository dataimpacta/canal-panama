import dash
from dash import html
from app.layout import create_layout  # Import layout from layout.py

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Define layout
app.layout = create_layout()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)