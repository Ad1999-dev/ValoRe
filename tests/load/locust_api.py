# locustfile.py
import random
import uuid
from datetime import date

from locust import HttpUser, between, task

LOCATION_PRESETS = [
    (47.61, -122.33),  # Seattle
    (47.61, -122.20),  # Bellevue
    (47.67, -122.12),  # Redmond
    (47.68, -122.21),  # Kirkland
    (47.53, -122.04),  # Issaquah
    (47.49, -122.21),  # Renton
    (47.32, -122.31),  # Federal Way
]


class ValoreApiUser(HttpUser):
    wait_time = between(1, 3)

    @task(1)
    def health(self):
        with self.client.get(
            "/health", name="GET /health", catch_response=True, timeout=10
        ) as r:
            if r.status_code != 200:
                r.failure(f"{r.status_code}: {r.text[:300]}")
            else:
                r.success()

    @task(5)
    def predict(self):
        # date format exactly like dashboard: YYYYMMDDT000000
        sale_date = date.today().strftime("%Y%m%d") + "T000000"

        bedrooms = random.randint(1, 6)
        bathrooms = random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
        floors = random.choice([1.0, 1.5, 2.0, 2.5, 3.0, 3.5])

        sqft_living = random.randrange(600, 4200, 50)
        sqft_basement = (
            random.randrange(0, min(1500, sqft_living - 100), 50)
            if sqft_living > 200
            else 0
        )
        sqft_lot = random.randrange(1000, 20000, 500)

        waterfront = random.choice([0, 1])
        view = random.randint(0, 4)
        condition = random.randint(1, 5)
        grade = random.randint(3, 12)

        yr_built = random.randint(1900, 2015)
        yr_renovated = random.choice([0, random.randint(1990, 2015)])

        lat, lon = random.choice(LOCATION_PRESETS)

        payload = {
            "id": uuid.uuid4().hex[:8],  # string, like dashboard
            "zipcode": "98103",  # string, like dashboard
            "date": sale_date,  # YYYYMMDDT000000
            "sqft_above": sqft_living - sqft_basement,
            "sqft_living15": sqft_living,
            "sqft_lot15": sqft_lot,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "sqft_living": sqft_living,
            "sqft_lot": sqft_lot,
            "sqft_basement": sqft_basement,
            "floors": floors,
            "waterfront": waterfront,
            "view": view,
            "condition": condition,
            "grade": grade,
            "yr_built": yr_built,
            "yr_renovated": yr_renovated,
            "lat": lat,
            "long": lon,
        }

        # IMPORTANT: same wrapper as utils.api.predict -> {"data": payload}
        body = {"data": payload}

        with self.client.post(
            "/predict",
            json=body,
            name="POST /predict",
            catch_response=True,
            timeout=30,
        ) as r:
            if r.status_code != 200:
                # for debugging schema errors
                r.failure(f"{r.status_code}: {r.text[:500]}")
                return

            try:
                j = r.json()
                if "prediction" not in j:
                    r.failure(f"Missing 'prediction' in response: {j}")
                else:
                    r.success()
            except Exception as e:
                r.failure(f"Invalid JSON response: {e}; body={r.text[:500]}")
