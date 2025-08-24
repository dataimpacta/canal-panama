# Panama Canal Analytics Dashboard

A Dash-based web application for monitoring emissions, waiting times, service times, and energy demand across the Panama Canal. The app is designed for deployment with Gunicorn behind a reverse proxy such as Nginx.

## Features
- Interactive dashboards for multiple datasets
- AWS S3 integration for data storage
- Modular callbacks, layouts, and charts for maintainability
- Basic load testing with Locust

## Installation
1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd canal-panama
   ```
2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Running the App
For development:
```bash
python -m app.app
```

For production with Gunicorn:
```bash
gunicorn app.app:server --workers 4 --bind 0.0.0.0:8050
```
Behind Nginx, ensure `ProxyFix` settings match the proxy configuration.

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

sample_data/             # Example data files
tests/                   # Pytest suite
locustfile.py            # Load testing script
```

## Updating Data
Data is loaded from S3. To refresh the datasets, update the source files in the configured bucket. Schedule a cron job or an AWS Lambda function to run your ETL pipeline and upload new parquet files; the app will read the latest versions on startup.

## Testing
Run the test suite after making changes:
```bash
PYTHONPATH=. pytest
```

## License
MIT License. See `LICENSE` for details.

## Author
Gabriel Fuentes and contributors.
