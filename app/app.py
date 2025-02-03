import dash
from dash import html
from layout import create_layout

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Define layout
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.layout = create_layout()

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
