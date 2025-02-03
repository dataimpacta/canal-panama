import dash
from dash import dcc, html
import pandas as pd
import plotly.express as px
import boto3
from io import StringIO

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# Set up AWS S3 client
s3_client = boto3.client('s3')

# Bucket and file name
bucket_name = 'buckect-canalpanama'
file_name = 'fruit_data.csv'

# Function to read CSV from S3
def read_csv_from_s3(bucket, file):
    obj = s3_client.get_object(Bucket=bucket, Key=file)
    data = obj['Body'].read().decode('utf-8')
    return pd.read_csv(StringIO(data))

# Read the data from S3
df = read_csv_from_s3(bucket_name, file_name)

# Create a simple bar chart using Plotly
fig = px.bar(df, x="Fruit", y="Amount", title="Fruit Amounts")

# Define the layout of the app
app.layout = html.Div([
    html.H1("Simple Dash App with S3 Data"),
    dcc.Graph(figure=fig),
])

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
