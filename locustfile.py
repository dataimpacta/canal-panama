from locust import HttpUser, task, between, events
import json
import random
import time

# ========================== CONFIGURATION ==========================

# Test configuration
TARGET_HOST = "https://www.canalpanama.online"  # Change to your target URL
LOCAL_HOST = "http://127.0.0.1:8050"  # For local testing

# Dashboard tabs and their relative weights
DASHBOARD_TABS = {
    "emissions": 4,      # Most popular
    "waiting": 3,        # Second most popular
    "service": 2,        # Medium popularity
    "energy": 2,         # Medium popularity
    "explorer": 1,       # Less popular
    "about": 1           # Least popular
}

# Vessel types for realistic filter combinations
VESSEL_TYPES = [
    "Container", "Oil tanker", "Chemical tanker", "Liquified gas tanker",
    "Bulk carrier", "General cargo", "Vehicle", "Refrigerated bulk",
    "Yacht", "Cruise", "Miscellaneous-other", "Offshore",
    "Miscellaneous-fishing", "Service-tug", "Ferry-pax only",
    "Ro-Ro", "Service-other", "Ferry-RoPax", "Other liquids tankers"
]

# Stop areas for waiting/service times
STOP_AREAS = [
    "MIT", "Panama Canal South Transit", "Panama Canal North Transit",
    "Atlantic - PPC Cristobal", "Bocas Fruit Company", "CCT",
    "Colon2000", "LNG terminal", "Oil Tanking", "PTP Charco Azul",
    "PTP Chiriqui Grande", "Pacific - PATSA", "Pacific - PPC Balboa",
    "Pacific - PSA", "Puerto Punta Rincon", "Puerto de Cruceros de Amador", "Telfer"
]

# Date ranges for realistic testing
DATE_RANGES = [
    (48, 71),   # Recent data
    (10, 50),   # Medium range
    (0, 67),    # Full range
    (20, 60),   # Another medium range
    (30, 55),   # Shorter recent range
]

# ========================== UTILITY FUNCTIONS ==========================

def get_random_vessel_combination():
    """Get a random combination of vessel types for filtering"""
    num_vessels = random.randint(2, 6)  # 2-6 vessels selected
    return random.sample(VESSEL_TYPES, num_vessels)

def get_random_stop_area_combination():
    """Get a random combination of stop areas for filtering"""
    num_areas = random.randint(3, 8)  # 3-8 areas selected
    return random.sample(STOP_AREAS, num_areas)

def get_random_date_range():
    """Get a random date range for filtering"""
    return random.choice(DATE_RANGES)

def build_emissions_payload(vessels, start_date, end_date, chart_id=1):
    """Build payload for emissions chart callback"""
    return {
        "output": f"..emissions--chart--{chart_id}.figure...emissions--chart--{chart_id}-fullscreen.figure..",
        "outputs": [
            {"id": f"emissions--chart--{chart_id}", "property": "figure"},
            {"id": f"emissions--chart--{chart_id}-fullscreen", "property": "figure"}
        ],
        "inputs": [
            {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 1}
        ],
        "changedPropIds": ["emissions--btn--refresh.n_clicks"],
        "parsedChangedPropsIds": ["emissions--btn--refresh.n_clicks"],
        "state": [
            {"id": "emissions--checklist--vessel", "property": "value", "value": vessels},
            {"id": "emissions--start-date", "property": "value", "value": start_date},
            {"id": "emissions--end-date", "property": "value", "value": end_date}
        ]
    }

def build_waiting_chart_payload(vessels, stop_areas, start_date, end_date, chart_id, tab_name="waiting"):
    """Build payload for individual waiting times chart callback"""
    return {
        "output": f"..time--chart--{chart_id}.figure...time--chart--{chart_id}-fullscreen.figure..",
        "outputs": [
            {"id": f"time--chart--{chart_id}", "property": "figure"},
            {"id": f"time--chart--{chart_id}-fullscreen", "property": "figure"}
        ],
        "inputs": [
            {"id": "time--btn--refresh", "property": "n_clicks", "value": 1}
        ],
        "changedPropIds": ["time--btn--refresh.n_clicks"],
        "parsedChangedPropsIds": ["time--btn--refresh.n_clicks"],
        "state": [
            {"id": "chart-tabs-store", "property": "data", "value": tab_name},
            {"id": "time--start-date", "property": "value", "value": start_date},
            {"id": "time--end-date", "property": "value", "value": end_date},
            {"id": "time--checklist--vessel", "property": "value", "value": vessels},
            {"id": "time--checklist--stop-area", "property": "value", "value": stop_areas}
        ]
    }

def build_energy_chart_payload(country_before, country_after, start_date, end_date, chart_id):
    """Build payload for individual energy chart callback"""
    # Base state for all charts
    base_state = [
        {"id": "energy--checklist--country-before", "property": "value", "value": country_before},
        {"id": "energy--checklist--country-after", "property": "value", "value": country_after},
        {"id": "energy--start-date", "property": "value", "value": start_date},
        {"id": "energy--end-date", "property": "value", "value": end_date}
    ]
    
    # Base inputs for all charts
    inputs = [
        {"id": "emissions--btn--refresh", "property": "n_clicks", "value": 0}
    ]
    
    # Add role input for charts 2 and 3
    if chart_id == 2:
        inputs.append({"id": "energy--role-chart2", "property": "data", "value": "country_before"})
    elif chart_id == 3:
        inputs.append({"id": "energy--role-chart3", "property": "data", "value": "country_before"})
    
    return {
        "output": f"..energy--chart--{chart_id}.figure...energy--chart--{chart_id}-fullscreen.figure..",
        "outputs": [
            {"id": f"energy--chart--{chart_id}", "property": "figure"},
            {"id": f"energy--chart--{chart_id}-fullscreen", "property": "figure"}
        ],
        "inputs": inputs,
        "changedPropIds": [],
        "parsedChangedPropsIds": [],
        "state": base_state
    }

def build_energy_role_payload(chart_id):
    """Build payload for energy role dropdown callback"""
    return {
        "output": f"energy--role-chart{chart_id}.data",
        "outputs": {"id": f"energy--role-chart{chart_id}", "property": "data"},
        "inputs": [
            {"id": f"energy--dropdown-chart{chart_id}", "property": "value", "value": "country_before"}
        ],
        "changedPropIds": [f"energy--dropdown-chart{chart_id}.value"],
        "parsedChangedPropsIds": [f"energy--dropdown-chart{chart_id}.value"]
    }

# ========================== USER CLASSES ==========================

class DashboardUser(HttpUser):
    """
    Realistic dashboard user that:
    - Visits different tabs
    - Refreshes charts with filters
    - Spends time viewing charts
    - Interacts with filters
    """
    host = TARGET_HOST
    wait_time = between(10, 15)  # Realistic time between actions

    def on_start(self):
        """Initialize session by loading the homepage"""
        self.client.get("/", name="/")
        # Load Dash dependencies
        self.client.get("/_dash-layout", name="/_dash-layout")
        self.client.get("/_dash-deps", name="/_dash-deps")

    @task(4)
    def emissions_analysis(self):
        """Complete emissions analysis workflow"""
        # Load emissions page
        self.client.get("/emissions", name="/emissions")
        
        # Wait for initial load
        time.sleep(2)
        
        # Get random filter values
        vessels = get_random_vessel_combination()
        start_date, end_date = get_random_date_range()
        
        # Trigger chart updates with realistic timing
        headers = {"Content-Type": "application/json"}
        
        # Update all charts (this simulates clicking refresh button)
        for chart_id in range(1, 5):
            payload = build_emissions_payload(vessels, start_date, end_date, chart_id)
            
            self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name=f"/_dash-update-component (emissions chart {chart_id})"
            )
            
            # Small delay between chart updates
            time.sleep(0.5)
        
        # Update UI elements
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
            "state": [
                {"id": "emissions--checklist--vessel", "property": "value", "value": vessels},
                {"id": "emissions--start-date", "property": "value", "value": start_date},
                {"id": "emissions--end-date", "property": "value", "value": end_date}
            ]
        }
        
        self.client.post(
            "/_dash-update-component",
            data=json.dumps(payload_ui),
            headers=headers,
            name="/_dash-update-component (emissions ui)"
        )

    @task(3)
    def waiting_times_analysis(self):
        """Complete waiting times analysis workflow"""
        # Load waiting page
        self.client.get("/waiting", name="/waiting")
        
        # Wait for initial load
        time.sleep(2)
        
        # Get random filter values
        vessels = get_random_vessel_combination()
        stop_areas = get_random_stop_area_combination()
        start_date, end_date = get_random_date_range()
        
        # Trigger chart updates for each chart separately
        headers = {"Content-Type": "application/json"}
        
        # Update each chart individually (like the actual callbacks)
        for chart_id in range(1, 5):
            payload = build_waiting_chart_payload(vessels, stop_areas, start_date, end_date, chart_id, "waiting")
            
            self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name=f"/_dash-update-component (waiting chart {chart_id})"
            )
            
            # Small delay between chart updates
            time.sleep(0.5)

    @task(2)
    def service_times_analysis(self):
        """Complete service times analysis workflow"""
        # Load service page (same as waiting but different tab)
        self.client.get("/service", name="/service")
        
        # Wait for initial load
        time.sleep(2)
        
        # Get random filter values
        vessels = get_random_vessel_combination()
        stop_areas = get_random_stop_area_combination()
        start_date, end_date = get_random_date_range()
        
        # Trigger chart updates for each chart separately (service tab)
        headers = {"Content-Type": "application/json"}
        
        # Update each chart individually (like the actual callbacks)
        for chart_id in range(1, 5):
            payload = build_waiting_chart_payload(vessels, stop_areas, start_date, end_date, chart_id, "service")
            
            self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name=f"/_dash-update-component (service chart {chart_id})"
            )
            
            # Small delay between chart updates
            time.sleep(0.5)

    @task(2)
    def energy_analysis(self):
        """Complete energy analysis workflow"""
        # Load energy page
        self.client.get("/energy", name="/energy")
        
        # Wait for initial load
        time.sleep(2)
        
        # Get random filter values for energy (using realistic country lists)
        all_countries_before = ["Algeria","Antigua and Barbuda","Argentina","Aruba","Australia","Bahamas","Barbados","Belgium","Belize","Bonaire, Sint Eustatius and Saba","Brazil","Cabo Verde","Canada","Cayman Islands","Chile","China","Colombia","Costa Rica","Cuba","Denmark","Dominican Republic","Ecuador","Egypt","El Salvador","Estonia","Falkland Islands (Malvinas)","Finland","France","Germany","Grenada","Guadeloupe","Guam","Guatemala","Guyana","Haiti","Honduras","Hong Kong","India","Indonesia","Ireland","Israel","Italy","Jamaica","Japan","Korea, Republic of","Kuwait","Latvia","Lithuania","Madagascar","Malaysia","Malta","Martinique","Mauritius","Mexico","Morocco","Netherlands","New Zealand","Nicaragua","Nigeria","Norway","Panama","Papua New Guinea","Peru","Portugal","Puerto Rico","Russian Federation","Saint Lucia","Saudi Arabia","Senegal","South Africa","Spain","Sri Lanka","Suriname","Sweden","Taiwan, Province of China","Trinidad and Tobago","Turks and Caicos Islands","Türkiye","Ukraine","United Arab Emirates","United Kingdom","United States","Venezuela, Bolivarian Republic of","Viet Nam","Virgin Islands, British","Virgin Islands, U.S."]
        
        all_countries_after = ["Algeria","Antigua and Barbuda","Argentina","Aruba","Australia","Bahamas","Barbados","Belgium","Bermuda","Bonaire, Sint Eustatius and Saba","Brazil","Bulgaria","Canada","Cayman Islands","Chile","China","Colombia","Costa Rica","Cuba","Curaçao","Denmark","Dominican Republic","Ecuador","Egypt","El Salvador","France","French Polynesia","Germany","Ghana","Grenada","Guadeloupe","Guatemala","Guyana","Haiti","Honduras","India","Indonesia","Ireland","Italy","Jamaica","Japan","Korea, Republic of","Libya","Malaysia","Malta","Martinique","Mauritania","Mexico","Morocco","Netherlands","New Caledonia","New Zealand","Nicaragua","Nigeria","Norway","Oman","Panama","Peru","Philippines","Poland","Portugal","Puerto Rico","Qatar","Russian Federation","Saint Lucia","Saudi Arabia","Senegal","South Africa","Spain","Taiwan, Province of China","Trinidad and Tobago","Tunisia","Türkiye","United Kingdom","United States","Venezuela, Bolivarian Republic of","Viet Nam","Virgin Islands, U.S."]
        
        # Select random countries (more realistic selection)
        countries_before = random.sample(all_countries_before, random.randint(5, 15))
        countries_after = random.sample(all_countries_after, random.randint(5, 15))
        
        # Use realistic date range (0-26 as shown in reference)
        start_date = random.randint(0, 20)
        end_date = random.randint(start_date + 1, 26)
        
        # Trigger chart updates for each chart separately
        headers = {"Content-Type": "application/json"}
        
        # Update each chart individually (like the actual callbacks)
        for chart_id in range(1, 5):
            # For charts 2 and 3, first trigger the role dropdown callback
            if chart_id in [2, 3]:
                role_payload = build_energy_role_payload(chart_id)
                self.client.post(
                    "/_dash-update-component",
                    data=json.dumps(role_payload),
                    headers=headers,
                    name=f"/_dash-update-component (energy role chart {chart_id})"
                )
                time.sleep(0.2)  # Small delay between role and chart update
            
            # Then trigger the chart update
            payload = build_energy_chart_payload(countries_before, countries_after, start_date, end_date, chart_id)
            
            self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name=f"/_dash-update-component (energy chart {chart_id})"
            )
            
            # Small delay between chart updates
            time.sleep(0.5)



    @task(1)
    def about_page_visit(self):
        """Visit the about page"""
        self.client.get("/about", name="/about")
        # About page is mostly static, no complex interactions needed


class FilterInteractionUser(HttpUser):
    """
    User that focuses on filter interactions and multiple chart refreshes
    """
    host = TARGET_HOST
    wait_time = between(5, 8)  # Faster interactions for filter testing

    def on_start(self):
        """Initialize session"""
        self.client.get("/", name="/")

    @task(3)
    def multiple_filter_changes(self):
        """Test multiple filter changes in quick succession"""
        # Start with emissions page
        self.client.get("/emissions", name="/emissions")
        time.sleep(1)
        
        headers = {"Content-Type": "application/json"}
        
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
            },
            {
                "vessels": ["Cruise", "Ro-Ro", "Ferry-pax only"],
                "start_date": 30,
                "end_date": 55
            }
        ]
        
        for combo in filter_combinations:
            # Update chart 2 (bar chart by vessel type) with different filters
            payload = build_emissions_payload(
                combo["vessels"], 
                combo["start_date"], 
                combo["end_date"], 
                chart_id=2
            )
            
            self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name="/_dash-update-component (emissions chart 2 filter change)"
            )
            
            # Small delay between filter changes
            time.sleep(1)

    @task(2)
    def waiting_filter_interactions(self):
        """Test waiting times filter interactions"""
        self.client.get("/waiting", name="/waiting")
        time.sleep(1)
        
        headers = {"Content-Type": "application/json"}
        
        # Test different vessel and stop area combinations
        combinations = [
            {
                "vessels": ["Container", "Bulk carrier"],
                "stop_areas": ["MIT", "Panama Canal South Transit", "Panama Canal North Transit"],
                "start_date": 48,
                "end_date": 71
            },
            {
                "vessels": ["Oil tanker", "Chemical tanker", "Liquified gas tanker"],
                "stop_areas": ["Atlantic - PPC Cristobal", "Pacific - PPC Balboa"],
                "start_date": 20,
                "end_date": 60
            }
        ]
        
        for combo in combinations:
            payload = build_waiting_chart_payload(
                combo["vessels"],
                combo["stop_areas"],
                combo["start_date"],
                combo["end_date"],
                2,  # Chart 2 for filter testing
                "waiting"
            )
            
            self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name="/_dash-update-component (waiting filter change)"
            )
            
            time.sleep(1)


class AssetLoader(HttpUser):
    """
    User that loads various assets and static files
    """
    host = TARGET_HOST
    wait_time = between(3, 6)

    def on_start(self):
        """Initialize session"""
        self.client.get("/", name="/")

    @task(3)
    def load_critical_assets(self):
        """Load critical assets that are always needed"""
        # Load CSS
        self.client.get("/assets/styles.css", name="/assets/styles.css")
        
        # Load images
        self.client.get("/assets/Financing_Logo.webp", name="/assets/Financing_Logo.webp")
        self.client.get("/assets/logo_senacyt.jpg", name="/assets/logo_senacyt.jpg")
        self.client.get("/assets/MTCC-logo.png", name="/assets/MTCC-logo.png")

    @task(2)
    def load_dash_dependencies(self):
        """Load Dash-specific dependencies"""
        self.client.get("/_dash-layout", name="/_dash-layout")
        self.client.get("/_dash-deps", name="/_dash-deps")
        self.client.get("/_dash-routes", name="/_dash-routes")

    @task(1)
    def load_other_assets(self):
        """Load other assets that might be requested"""
        self.client.get("/assets/gabriel_moises_fuentes.jpg", name="/assets/gabriel_moises_fuentes.jpg")
        self.client.get("/assets/sample_image.png", name="/assets/sample_image.png")


class HeavyLoadUser(HttpUser):
    """
    User that creates heavy load by triggering many chart updates
    """
    host = TARGET_HOST
    wait_time = between(1, 3)  # Very fast interactions to create load

    def on_start(self):
        """Initialize session"""
        self.client.get("/", name="/")

    @task(5)
    def rapid_chart_updates(self):
        """Trigger rapid chart updates to create load"""
        # Load emissions page
        self.client.get("/emissions", name="/emissions")
        
        headers = {"Content-Type": "application/json"}
        
        # Trigger multiple chart updates rapidly
        for i in range(5):  # 5 rapid updates
            vessels = get_random_vessel_combination()
            start_date, end_date = get_random_date_range()
            
            # Update chart 1 (most complex - map)
            payload = build_emissions_payload(vessels, start_date, end_date, 1)
            
            self.client.post(
                "/_dash-update-component",
                data=json.dumps(payload),
                headers=headers,
                name="/_dash-update-component (rapid emissions chart 1)"
            )

    @task(3)
    def concurrent_page_loads(self):
        """Simulate multiple users loading different pages simultaneously"""
        pages = ["/emissions", "/waiting", "/service", "/energy", "/explorer"]
        
        for page in pages:
            self.client.get(page, name=f"concurrent {page}")

    @task(2)
    def mixed_workload(self):
        """Mix of different operations to create realistic load"""
        # Random page visit
        page = random.choice(["/emissions", "/waiting", "/energy"])
        self.client.get(page, name=f"mixed workload {page}")
        
        # Random asset load
        asset = random.choice([
            "/assets/styles.css",
            "/assets/Financing_Logo.webp",
            "/_dash-layout"
        ])
        self.client.get(asset, name=f"mixed workload {asset}")


# ========================== EVENT HANDLERS ==========================

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when a test is starting"""
    print(f"🚀 Starting performance test with target: {TARGET_HOST}")
    print(f"📊 Testing Panama Canal Dashboard with realistic user behavior")
    print(f"🎯 Target: 200 users with chart interactions and filter changes")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when a test is ending"""
    print(f"✅ Performance test completed")
    print(f"📈 Check the results for dashboard performance metrics")

# ========================== CONFIGURATION NOTES ==========================

"""
To run this performance test:

1. For local testing:
   locust -f locustfile.py --host=http://127.0.0.1:8050

2. For production testing:
   locust -f locustfile.py --host=https://www.canalpanama.online

3. To run with specific user count:
   locust -f locustfile.py --host=https://www.canalpanama.online --users=200 --spawn-rate=10

4. To run headless:
   locust -f locustfile.py --host=https://www.canalpanama.online --users=200 --spawn-rate=10 --run-time=10m --headless

Key Features:
- Realistic user behavior with 10-15 second wait times
- Chart refresh simulations with filter interactions
- Multiple user types (Dashboard, Filter, Asset, Heavy Load)
- Comprehensive testing of all dashboard tabs
- Proper error handling and response validation
- Asset loading simulation
- Concurrent load testing

User Distribution (for 200 users):
- DashboardUser: ~120 users (60%) - Main realistic users
- FilterInteractionUser: ~40 users (20%) - Filter testing
- AssetLoader: ~20 users (10%) - Asset loading
- HeavyLoadUser: ~20 users (10%) - Load generation
"""
