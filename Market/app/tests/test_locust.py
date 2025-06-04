from locust import HttpUser, task, between
import random
import string
import json

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

def new_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def random_name():
    return {
        "first_name": ''.join(random.choices(string.ascii_uppercase, k=1)).upper() + ''.join(random.choices(string.ascii_lowercase, k=5)),
        "last_name": ''.join(random.choices(string.ascii_uppercase, k=1)).upper() + ''.join(random.choices(string.ascii_lowercase, k=5)),
        "fathers_name": ''.join(random.choices(string.ascii_uppercase, k=1)).upper() + ''.join(random.choices(string.ascii_lowercase, k=5)),
    }

def new_phone():
    return '+7' + ''.join(random.choices(string.digits, k=10))

class WebsiteUser(HttpUser):
    wait_time = between(3, 7)

    def on_start(self):
        self.user = random_user()
        register_response = self.client.post("/api/v1/accounts/register", json=self.user)
        
        if register_response.status_code not in [200, 201]:
            self.token = None
            self.market_id = None
            return

        login_data = {**self.user, "user_agent": "locust-agent"}
        login_response = self.client.post("/api/v1/accounts/login", json=login_data)
        
        if login_response.status_code == 200:
            self.token = login_response.json().get("access_token")
        else:
            self.token = None
            self.market_id = None
            return

        self.market = random_market()
        self.market_id = None
        
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            profile_response = self.client.get("/api/v1/markets/profile", headers=headers)
            
            if profile_response.status_code == 200:
                self.market_id = profile_response.json().get("id")
            elif profile_response.status_code == 404:
                create_response = self.client.post("/api/v1/markets/", json=self.market, headers=headers)
                if create_response.status_code == 201:
                    self.market_id = create_response.json().get("id")

    @task(5)
    def get_profile(self):
        if getattr(self, 'token', None):
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/v1/users/profile", headers=headers)

    @task(3)
    def get_profile_history(self):
        if getattr(self, 'token', None):
            headers = {"Authorization": f"Bearer {self.token}"}
            skip = random.randint(0, 5)
            limit = random.randint(5, 15)
            self.client.get(f"/api/v1/users/profile/history?skip={skip}&limit={limit}", headers=headers)

    @task(2)
    def update_profile_name(self):
        if getattr(self, 'token', None):
            names = random_name()
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.put("/api/v1/users/profile/name", json=names, headers=headers)

    @task(2)
    def update_profile_phone(self):
        if self.token:
            new_phone_num = new_phone()
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.client.put(
                "/api/v1/users/profile/phone", 
                data=json.dumps(new_phone_num),
                headers=headers,
                name="/users/profile/phone"
            )
            
    @task(2)
    def update_profile_login(self):
        if self.token:
            new_login = "new_" + self.user["login"][4:] 
            headers = {"Authorization": f"Bearer {self.token}"}
            
            self.client.put(
                "/api/v1/users/profile/login", 
                data=json.dumps(new_login),
                headers=headers,
                name="/users/profile/login"
            )

    @task(2)
    def update_profile_password(self):
        if getattr(self, 'token', None):
            old_pass = self.user.get("password", "")
            new_pass = new_password()
            headers = {"Authorization": f"Bearer {self.token}"}
            response = self.client.put("/api/v1/users/profile/password", 
                                      json={"old_password": old_pass, "new_password": new_pass}, 
                                      headers=headers)
            if response.status_code == 200:
                self.user["password"] = new_pass

    @task(3)
    def get_verified_markets(self):
        if getattr(self, 'token', None):
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.get("/api/v1/markets/", headers=headers)

    # @task(2)
    # def get_own_market(self):
    #     if getattr(self, 'token', None) and getattr(self, 'market_id', None):
    #         headers = {"Authorization": f"Bearer {self.token}"}
    #         self.client.get("/api/v1/markets/profile", headers=headers)

    @task(1)
    def update_market(self):
        if getattr(self, 'token', None) and getattr(self, 'market_id', None):
            updated_market = random_market()
            headers = {"Authorization": f"Bearer {self.token}"}
            self.client.put("/api/v1/markets/", json=updated_market, headers=headers)