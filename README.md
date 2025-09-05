# Panama Canal Analytics Dashboard

A Dash-based web application for monitoring emissions, waiting times, service times, and energy demand across the Panama Canal. The app is designed for deployment with Gunicorn behind a reverse proxy such as Nginx.

## Features
- Interactive dashboards for multiple datasets
- AWS S3 integration for data storage
- Modular callbacks, layouts, and charts for maintainability

## Folder Structure
```
app/
├── app.py               # Main Dash application
├── callbacks/           # Callback definitions
├── charts/              # Plotly chart helpers
├── controls/            # UI control builders
├── data_utils/          # Data processing utilities
├── layout.py            # Layout and component assembly
└── theme.py             # Color palette and theme constants

locustfile.py            # Load testing script
```

## Updating Data
Data is loaded from S3. To refresh the datasets, update the source files in the configured bucket. Schedule a cron job or an AWS Lambda function to run your ETL pipeline and upload new parquet files; the app will read the latest versions on startup.