# Canal Panama Dashboard

This project contains a Dash application for visualising maritime statistics along with utility scripts.

## Running Tests

Install the required dependencies and run `pytest` from the project root:

```bash
pip install -r requirements.txt
pytest
```

The tests cover critical functions from `app/data_utils/map_processing.py` and do not require any AWS credentials.
