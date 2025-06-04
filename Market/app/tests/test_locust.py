from locust import HttpUser, task, between
import random
import string

def random_user():
    username = "user_" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    return {"login": username, "password": password}

def random_market():
    return {
        "name": "Market " + ''.join(random.choices(string.ascii_uppercase, k=5)),
        "address": "Street " + ''.join(random.choices(string.ascii_uppercase, k=3)),
        "postal_code": ''.join(random.choices(string.digits, k=6)),
        "inn": ''.join(random.choices(string.digits, k=10)),
        "kpp": ''.join(random.choices(string.digits, k=9)),
        "payment_account": ''.join(random.choices(string.digits, k=20)),
        "correspondent_account": ''.join(random.choices(string.digits, k=20)),
        "bank": "Bank " + ''.join(random.choices(string.ascii_uppercase, k=4)),
        "bik": ''.join(random.choices(string.digits, k=9)),
    }

def invalid_market():
    return {"name": "", "address": "", "postal_code": "bad", "inn": "", "kpp": "", "payment_account": "", "correspondent_account": "", "bank": "", "bik": ""}

class WebsiteUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.user = random_user()
        self.client.post("/api/v1/accounts/register", json=self.user)
        login_data = {**self.user, "user_agent": "locust-agent"}
        response = self.client.post("/api/v1/accounts/login", json=login_data)
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            self.token = None
        self.market = random_market()

    @task
    def get_profile(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/v1/users/profile", headers=headers)

    @task
    def unauthorized_profile(self):
        self.client.get("/api/v1/users/profile")

    @task
    def invalid_token_profile(self):
        headers = {"Authorization": "Bearer invalidtoken"}
        self.client.get("/api/v1/users/profile", headers=headers)

    @task
    def duplicate_registration(self):
        self.client.post("/api/v1/accounts/register", json=self.user)

    @task
    def wrong_password_login(self):
        login_data = {"login": self.user["login"], "password": "wrongpass", "user_agent": "locust-agent"}
        self.client.post("/api/v1/accounts/login", json=login_data)

    @task
    def create_market(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.post("/api/v1/markets/", json=self.market, headers=headers)

    @task
    def update_market(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.put("/api/v1/markets/", json=self.market, headers=headers)

    @task
    def create_market_invalid(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.post("/api/v1/markets/", json=invalid_market(), headers=headers)

    @task
    def update_market_invalid(self):
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.put("/api/v1/markets/", json=invalid_market(), headers=headers)

user_classes = [WebsiteUser] 