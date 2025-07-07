from locust import HttpUser, task, between
import json

class PublicUser(HttpUser):
    host = "https://canalpanama.online"
    wait_time = between(1, 5)

    @task
    def load_homepage(self):
        """Load the landing page"""
        self.client.get("/")


class DashboardUser(HttpUser):
    host = "https://canalpanama.online"
    wait_time = between(1, 5)

    @task
    def refresh_waiting_time_tab(self):
        # Step 1: Load the homepage to initialize session cookies
        home_response = self.client.get("/", name="/")
        if home_response.status_code != 200:
            return  # Skip if the homepage failed

        # Step 2: Simulate Refresh Charts on the "Waiting Time" tab
        payload = {
            "output": "..time--chart--1.figure...time--chart--1-fullscreen.figure...time--chart--2.figure...time--chart--2-fullscreen.figure...time--chart--3.figure...time--chart--3-fullscreen.figure...time--chart--4.figure...time--chart--4-fullscreen.figure...time--modal--no-data.is_open..",
            "outputs": [
                {"id": "time--chart--1", "property": "figure"},
                {"id": "time--chart--1-fullscreen", "property": "figure"},
                {"id": "time--chart--2", "property": "figure"},
                {"id": "time--chart--2-fullscreen", "property": "figure"},
                {"id": "time--chart--3", "property": "figure"},
                {"id": "time--chart--3-fullscreen", "property": "figure"},
                {"id": "time--chart--4", "property": "figure"},
                {"id": "time--chart--4-fullscreen", "property": "figure"},
                {"id": "time--modal--no-data", "property": "is_open"}
            ],
            "inputs": [
                {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
            ],
            "changedPropIds": ["emissions--btn--refresh.n_clicks"],
            "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
            "state": [
                {"id": "chart-tabs-store", "property": "value"},
                {"id": "time--start-date", "property": "value", "value": 0},
                {"id": "time--end-date", "property": "value", "value": 67},
                {"id": "time--checklist--vessel", "property": "value", "value": [
                    "Chemical tanker", "Liquified gas tanker", "Bulk carrier",
                    "Cruise", "General cargo", "Miscellaneous-other", "Offshore",
                    "Refrigerated bulk", "Ro-Ro", "Service-tug", "Vehicle", "Yacht",
                    "Service-other", "Miscellaneous-fishing", "Ferry-RoPax",
                    "Other liquids tankers", "Ferry-pax only"
                ]},
                {"id": "time--checklist--stop-area", "property": "value", "value": [
                    "MIT", "Panama Canal South Transit", "Panama Canal North Transit",
                    "Atlantic - PPC Cristobal", "Bocas Fruit Company", "CCT",
                    "Colon2000", "LNG terminal", "Oil Tanking", "PTP Charco Azul",
                    "PTP Chiriqui Grande", "Pacific - PATSA", "Pacific - PPC Balboa",
                    "Pacific - PSA", "Puerto Punta Rincon", "Puerto de Cruceros de Amador", "Telfer"
                ]}
            ]
        }

        headers = {
            "Content-Type": "application/json"
        }

        with self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload),
            headers=headers,
            name="/_dash-update-component",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()
