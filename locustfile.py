from locust import HttpUser, task, between
import json

class CrowdTickUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:8000"

    def on_start(self):
        """Login with CSRF token using hardcoded credentials."""
        username = ""
        password = ""

        # Step 1: Get CSRF token from login page
        response = self.client.get("/admin/login/", allow_redirects=False)
        print(f"GET Status: {response.status_code}, Cookies: {self.client.cookies}")

        self.csrftoken = self.client.cookies.get('csrftoken')
        if not self.csrftoken:
            print("No CSRF token found")
            return

        # Step 2: Post login with CSRF token
        response = self.client.post(
            "/admin/login/?next=/admin/",
            {
                "username": username,
                "password": password,
                "csrfmiddlewaretoken": self.csrftoken
            },
            headers={"Referer": "http://localhost:8000/admin/login/"},
            allow_redirects=True
        )
        if response.status_code == 200:
            print("Logged in successfully")
        else:
            print(f"Login failed: {response.status_code} - {response.text[:200]}")

    @task(1)
    def create_poll(self):
        """Create a poll with csrf token."""
        if not hasattr(self, 'csrftoken') or not hasattr(self, 'sessionid'):
            print("Skipping create_poll: Not authenticated")
            return

        poll_data = {"title": "Test Poll", "options": {"Option A": 0, "Option B": 0}}
        response = self.client.post(
            "/api/polls/",
            json=poll_data,
            headers={
                "Content-Type": "application/json",
                "X-CSRFToken": self.csrftoken,
                "Cookie": f"csrftoken={self.csrftoken}; sessionid={self.sessionid}"
            }
        )
        if response.status_code == 201:
            self.poll_id = response.json().get("id")
        else:
            print(f"Create poll failed: {response.status_code}")

    @task(3)
    def cast_vote(self):
        """Cast a vote on the poll with csrf token"""
        if not hasattr(self, 'poll_id') or not hasattr(self, 'csrftoken') or not hasattr(self, 'sessionid'):
            print("Skipping cast_vote: Not authenticated or no poll_id")
            return

        vote_data = {"poll": self.poll_id, "choice": "Option A"}
        response = self.client.post(
            "/api/votes/",
            json=vote_data,
            headers={
                "Content-Type": "application/json",
                "X-CSRFToken": self.csrftoken,
                "Cookie": f"csrftoken={self.csrftoken}; sessionid={self.sessionid}"
            }
        )
        if response.status_code != 202:
            print(f"Vote failed: {response.status_code}")

    @task(5)
    def get_results(self):
        """Get poll results (GET doesn’t need CSRF, but needs session)."""
        if not hasattr(self, 'poll_id') or not hasattr(self, 'sessionid'):
            print("Skipping get_results: Not authenticated or no poll_id")
            return

        response = self.client.get(
            f"/api/polls/{self.poll_id}/results/",
            headers={"Cookie": f"sessionid={self.sessionid}"}
        )
        if response.status_code != 200:
            print(f"Get results failed: {response.status_code}")