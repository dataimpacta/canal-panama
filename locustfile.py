from locust import HttpUser, task, between
import json

class PublicUser(HttpUser):
    """Simple user that just visits the main webpages."""
    host = "http://127.0.0.1:8050/e"
    wait_time = between(3, 6)

    def on_start(self):
        """Initialize session by loading the homepage"""
        self.client.get("/", name="/")

    @task(3)
    def visit_homepage(self):
        """Visit the homepage"""
        self.client.get("/", name="/")

    @task(2)
    def visit_emissions(self):
        """Visit the emissions page"""
        self.client.get("/emissions", name="/emissions")

    @task(1)
    def visit_waiting(self):
        """Visit the waiting time page"""
        self.client.get("/waiting", name="/waiting")

    @task(1)
    def visit_energy(self):
        """Visit the energy page"""
        self.client.get("/energy", name="/energy")

    @task(1)
    def visit_explorer(self):
        """Visit the explorer page"""
        self.client.get("/explorer", name="/explorer")

    @task(1)
    def visit_about(self):
        """Visit the about page"""
        self.client.get("/about", name="/about")


class DashboardUser(HttpUser):
    """User that visits pages and loads Dash dependencies."""
    host = "https://www.canalpanama.online"
    wait_time = between(8, 15)  # More realistic: 8-15 seconds between actions

    def on_start(self):
        """Initialize session"""
        self.client.get("/", name="/")

    @task(4)
    def emissions_analysis(self):
        """Visit emissions page and load dependencies"""
        self.client.get("/emissions", name="/emissions")
        # Load Dash dependencies that are typically requested
        self.client.get("/_dash-layout", name="/_dash-layout")
        self.client.get("/_dash-deps", name="/_dash-deps")

    @task(3)
    def waiting_analysis(self):
        """Visit waiting page and load dependencies"""
        self.client.get("/waiting", name="/waiting")
        self.client.get("/_dash-layout", name="/_dash-layout")
        self.client.get("/_dash-deps", name="/_dash-deps")

    @task(2)
    def energy_analysis(self):
        """Visit energy page and load dependencies"""
        self.client.get("/energy", name="/energy")
        self.client.get("/_dash-layout", name="/_dash-layout")
        self.client.get("/_dash-deps", name="/_dash-deps")

    @task(2)
    def explorer_analysis(self):
        """Visit explorer page and load dependencies"""
        self.client.get("/explorer", name="/explorer")
        self.client.get("/_dash-layout", name="/_dash-layout")
        self.client.get("/_dash-deps", name="/_dash-deps")


class ChartUser(HttpUser):
    """User that triggers actual chart updates and map generation."""
    host = "https://www.canalpanama.online"
    wait_time = between(2, 5)  # More realistic: 8-15 seconds between chart updates

    def on_start(self):
        """Initialize session"""
        self.client.get("/", name="/")

    @task(4)
    def emissions_chart_update(self):
        """Trigger emissions chart updates - multiple requests for separate callbacks"""
        # Load emissions page first
        self.client.get("/emissions", name="/emissions")
        
        # Common state for all emissions callbacks
        common_state = [
            {"id": "emissions--checklist--vessel", "property": "value", "value": [
                "Container", "Oil tanker", "Chemical tanker", "Liquified gas tanker", 
                "Bulk carrier", "General cargo", "Vehicle", "Refrigerated bulk", 
                "Yacht", "Cruise", "Miscellaneous-other", "Offshore", 
                "Miscellaneous-fishing", "Service-tug", "Ferry-pax only", 
                "Ro-Ro", "Service-other", "Ferry-RoPax", "Other liquids tankers"
            ]},
            {"id": "emissions--start-date", "property": "value", "value": 48},
            {"id": "emissions--end-date", "property": "value", "value": 71}
        ]

        headers = {"Content-Type": "application/json"}

        # Trigger chart 1 callback
        payload_chart1 = {
            "output": "..emissions--chart--1.figure...emissions--chart--1-fullscreen.figure..",
            "outputs": [
                {"id": "emissions--chart--1", "property": "figure"},
                {"id": "emissions--chart--1-fullscreen", "property": "figure"}
            ],
            "inputs": [
                {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
            ],
            "changedPropIds": ["emissions--btn--refresh.n_clicks"],
            "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
            "state": common_state
        }

        with self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload_chart1),
            headers=headers,
            name="/_dash-update-component (emissions chart 1)",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()

        # Trigger chart 2 callback
        payload_chart2 = {
            "output": "..emissions--chart--2.figure...emissions--chart--2-fullscreen.figure..",
            "outputs": [
                {"id": "emissions--chart--2", "property": "figure"},
                {"id": "emissions--chart--2-fullscreen", "property": "figure"}
            ],
            "inputs": [
                {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
            ],
            "changedPropIds": ["emissions--btn--refresh.n_clicks"],
            "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
            "state": common_state
        }

        with self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload_chart2),
            headers=headers,
            name="/_dash-update-component (emissions chart 2)",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()

        # Trigger chart 3 callback (map)
        payload_chart3 = {
            "output": "..emissions--chart--3.figure...emissions--chart--3-fullscreen.figure..",
            "outputs": [
                {"id": "emissions--chart--3", "property": "figure"},
                {"id": "emissions--chart--3-fullscreen", "property": "figure"}
            ],
            "inputs": [
                {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
            ],
            "changedPropIds": ["emissions--btn--refresh.n_clicks"],
            "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
            "state": common_state
        }

        with self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload_chart3),
            headers=headers,
            name="/_dash-update-component (emissions chart 3)",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()

        # Trigger chart 4 callback
        payload_chart4 = {
            "output": "..emissions--chart--4.figure...emissions--chart--4-fullscreen.figure..",
            "outputs": [
                {"id": "emissions--chart--4", "property": "figure"},
                {"id": "emissions--chart--4-fullscreen", "property": "figure"}
            ],
            "inputs": [
                {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
            ],
            "changedPropIds": ["emissions--btn--refresh.n_clicks"],
            "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
            "state": common_state
        }

        with self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload_chart4),
            headers=headers,
            name="/_dash-update-component (emissions chart 4)",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()


        # Trigger UI elements callback
        payload_ui = {
            "output": "..modal-no-data.is_open...emissions--range-label.children..",
            "outputs": [
                {"id": "modal-no-data", "property": "is_open"},
                {"id": "emissions--range-label", "property": "children"}
            ],
            "inputs": [
                {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
            ],
            "changedPropIds": ["emissions--btn--refresh.n_clicks"],
            "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
            "state": common_state
        }

        with self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload_ui),
            headers=headers,
            name="/_dash-update-component (emissions ui)",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()

    @task(3)
    def waiting_chart_update(self):
        """Trigger waiting time chart update"""
        # Load waiting page first
        self.client.get("/waiting", name="/waiting")
        
        # Trigger chart update with exact payload structure from browser
        payload = {
            "output": "..time--chart--1.figure...time--chart--1-fullscreen.figure...time--chart--2.figure...time--chart--2-fullscreen.figure...time--chart--3.figure...time--chart--3-fullscreen.figure...time--chart--4.figure...time--chart--4-fullscreen.figure...time--modal--no-data.is_open...time--range-label.children..",
            "outputs": [
                {"id": "time--chart--1", "property": "figure"},
                {"id": "time--chart--1-fullscreen", "property": "figure"},
                {"id": "time--chart--2", "property": "figure"},
                {"id": "time--chart--2-fullscreen", "property": "figure"},
                {"id": "time--chart--3", "property": "figure"},
                {"id": "time--chart--3-fullscreen", "property": "figure"},
                {"id": "time--chart--4", "property": "figure"},
                {"id": "time--chart--4-fullscreen", "property": "figure"},
                {"id": "time--modal--no-data", "property": "is_open"},
                {"id": "time--range-label", "property": "children"}
            ],
            "inputs": [
                {"id": "time--btn--refresh", "property": "n_clicks", "value": 1}
            ],
            "changedPropIds": ["time--btn--refresh.n_clicks"],
            "parsedChangedPropsIds": ["time--btn--refresh.n_clicks"],
            "state": [
                {"id": "chart-tabs-store", "property": "data", "value": "waiting"},
                {"id": "time--start-date", "property": "value", "value": 48},
                {"id": "time--end-date", "property": "value", "value": 71},
                {"id": "time--checklist--vessel", "property": "value", "value": [
                    "Container", "Oil tanker", "Chemical tanker", "Liquified gas tanker",
                    "Bulk carrier", "Cruise", "General cargo", "Miscellaneous-other",
                    "Offshore", "Refrigerated bulk", "Ro-Ro", "Service-tug", "Vehicle",
                    "Yacht", "Service-other", "Miscellaneous-fishing", "Ferry-RoPax",
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

        headers = {"Content-Type": "application/json"}
        with self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload),
            headers=headers,
            name="/_dash-update-component (waiting chart)",
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(f"Status {response.status_code}: {response.text}")
            else:
                response.success()

    @task(2)
    def multiple_chart_updates(self):
        """Trigger multiple chart updates to create heavy load"""
        # Test different filter combinations
        filter_combinations = [
            {
                "vessels": ["Container", "Bulk carrier", "Oil tanker"],
                "start_date": 10,
                "end_date": 50
            },
            {
                "vessels": ["Chemical tanker", "Liquified gas tanker", "General cargo"],
                "start_date": 20,
                "end_date": 60
            },
            {
                "vessels": ["Container", "Vehicle", "Yacht"],
                "start_date": 0,
                "end_date": 67
            }
        ]
        
        for combo in filter_combinations:
            # Trigger chart 2 update (bar chart by vessel type)
            payload = {
                "output": "..emissions--chart--2.figure...emissions--chart--2-fullscreen.figure..",
                "outputs": [
                    {"id": "emissions--chart--2", "property": "figure"},
                    {"id": "emissions--chart--2-fullscreen", "property": "figure"}
                ],
                "inputs": [
                    {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
                ],
                "changedPropIds": ["emissions--btn--refresh.n_clicks"],
                "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
                "state": [
                    {"id": "emissions--checklist--vessel", "property": "value", "value": combo["vessels"]},
                    {"id": "emissions--start-date", "property": "value", "value": combo["start_date"]},
                    {"id": "emissions--end-date", "property": "value", "value": combo["end_date"]}
                ]
            }

            headers = {"Content-Type": "application/json"}
            with self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name="/_dash-update-component (emissions chart 2)",
                catch_response=True
            ) as response:
                if response.status_code != 200:
                    response.failure(f"Status {response.status_code}: {response.text}")
                else:
                    response.success()


class AssetLoader(HttpUser):
    """User that loads various assets and static files."""
    host = "https://www.canalpanama.online"
    wait_time = between(5, 10)  # More realistic asset loading timing

    def on_start(self):
        """Initialize session"""
        self.client.get("/", name="/")

    @task(3)
    def load_assets(self):
        """Load various assets that might be requested"""
        # Load CSS
        self.client.get("/assets/styles.css", name="/assets/styles.css")
        
        # Load images
        self.client.get("/assets/Financing_Logo.webp", name="/assets/Financing_Logo.webp")
        self.client.get("/assets/logo_senacyt.jpg", name="/assets/logo_senacyt.jpg")
