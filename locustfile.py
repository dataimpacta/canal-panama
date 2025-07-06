from locust import HttpUser, task, between

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
    def load_dashboard(self):
        """Request main dashboard assets"""
        self.client.get("/")
        # Dash apps fetch their layout and dependencies via these endpoints
        self.client.get("/_dash-layout", name="/_dash-layout")
        self.client.get("/_dash-deps", name="/_dash-deps")
