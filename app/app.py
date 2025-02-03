import dash
from dash import dcc, html
import plotly.express as px

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Sample data embedded directly in the code (example: a simple bar chart)
data = {
    "Fruits": ["Apples", "Bananas", "Oranges", "Berries", "Pears"],
    "Amount": [10, 15, 7, 20, 13]
}

# Create a simple bar chart using Plotly
fig = px.bar(data_frame=data, x="Fruits", y="Amount", title="Fruit Amounts")

# Define the layout of the app
app.layout = html.Div([
    html.H1("Bar Chart"),
    dcc.Graph(figure=fig),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
