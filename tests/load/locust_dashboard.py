# locust_dashboard.py
from locust import HttpUser, between, task


class DashboardUser(HttpUser):
    wait_time = between(1, 3)

    @task(2)
    def home(self):
        self.client.get("/", name="GET / (Home)")

    @task(2)
    def estimate_price(self):
        self.client.get("/1_Estimate_Price", name="GET /1_Estimate_Price")

    @task(1)
    def explore_market(self):
        self.client.get("/2_Explore_Market", name="GET /2_Explore_Market")

    @task(1)
    def model_insights(self):
        self.client.get("/3_Model_Insights", name="GET /3_Model_Insights")
