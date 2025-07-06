# Canal Panama Dashboard

This project contains a Dash application for visualising maritime statistics along with utility scripts.

## Running Tests

Install the required dependencies and run `pytest` from the project root:

```bash
pip install -r requirements.txt
pytest
```

The tests cover critical functions from `app/data_utils/map_processing.py` and do not require any AWS credentials.

## Load Testing with Locust

This repository includes a basic `locustfile.py` for exercising the dashboard hosted at `https://canalpanama.online/`. After installing the dependencies you can launch Locust with:

```bash
locust -f locustfile.py
```

Then open `http://localhost:8089` in your browser to start a test with multiple user types.
