from locust import HttpUser, task, between, events
from locust.exception import LocustError
import json
import random

# Sample poll options matching your Poll.options JSONField
POLL_OPTIONS = {"Option 1": 0, "Option 2": 0, "Option 3": 0}

class PollingUser(HttpUser):
    wait_time = between(1, 5)
    host = "http://localhost:8000"
    
    session_cookie = None
    username = None
    poll_ids = []
    voted_polls = set()
    
    def on_start(self):
        """Register a user and use the session for all tasks."""
        self.username = f"testuser_{random.randint(1, 10000)}"
        register_payload = {"username": self.username, "password": "testpass123", "email": f"{self.username}@example.com"}
        with self.client.post("/api/register/", json=register_payload, catch_response=True) as resp:
            print(f"Register response: {resp.status_code} - {resp.text}")
            print(f"Register cookies: {dict(self.client.cookies)}")
            if resp.status_code == 201:
                self.session_cookie = self.client.cookies.get("sessionid")
                if not self.session_cookie:
                    resp.failure("No session cookie after registration")
                    raise LocustError("Registration succeeded but no session cookie found")
                print(f"Session cookie after registration: {self.session_cookie}")
                resp.success()
            elif resp.status_code == 400 and "username" in resp.json():
                resp.failure(f"Username clash: {resp.text}")
                raise LocustError("Registration failed due to duplicate username")
            else:
                resp.failure(f"Registration failed: {resp.text}")
                raise LocustError("Could not register user")
    
    @task(1)
    def create_poll(self):
        """Create a new poll."""
        payload = {"title": f"Test Poll by {self.username}", "options": POLL_OPTIONS}
        print(f"Session cookie before poll creation: {self.session_cookie}")
        print(f"Request cookies: {dict(self.client.cookies)}")
        with self.client.post("/api/polls/", json=payload, catch_response=True) as resp:
            print(f"Create poll response: {resp.status_code} - {resp.text}")
            if resp.status_code == 201:
                poll_id = resp.json()["id"]
                self.poll_ids.append(poll_id)
                print(f"Added poll ID to poll_ids: {poll_id}")
                resp.success()
            elif resp.status_code == 403:
                resp.failure("Permission denied: session may be invalid")
            else:
                resp.failure(f"Poll creation failed: {resp.status_code} - {resp.text}")
    
    @task(5)
    def vote(self):
        """Vote on a poll if not already voted."""
        if not self.poll_ids:
            print("No polls available to vote on")
            return
        available_polls = [pid for pid in self.poll_ids if pid not in self.voted_polls]
        if not available_polls:
            print("All polls voted on")
            return
        poll_id = random.choice(available_polls)
        choice = random.choice(list(POLL_OPTIONS.keys()))
        payload = {"choice": choice}
        print(f"Attempting to vote on poll ID: {poll_id}")
        with self.client.post(f"/api/polls/{poll_id}/vote/", json=payload, catch_response=True) as resp:
            print(f"Vote response: {resp.status_code} - {resp.text}")
            if resp.status_code == 202:  # Updated to match HTTP_202_ACCEPTED
                self.voted_polls.add(poll_id)
                resp.success()
            elif resp.status_code == 400 and "already voted" in resp.text.lower():
                self.voted_polls.add(poll_id)
                resp.success()
            elif resp.status_code == 403:
                resp.failure("Permission denied: session may be invalid")
            elif resp.status_code == 404:
                resp.failure(f"Poll not found: {poll_id}")
            else:
                resp.failure(f"Vote failed: {resp.status_code} - {resp.text}")
    
    @task(3)
    def get_results(self):
        """Retrieve poll results."""
        if not self.poll_ids:
            print("No polls available for results")
            return
        poll_id = random.choice(self.poll_ids)
        print(f"Fetching results for poll ID: {poll_id}")
        with self.client.get(f"/api/polls/{poll_id}/results/", catch_response=True) as resp:
            print(f"Results response: {resp.status_code} - {resp.text}")
            if resp.status_code == 200:
                resp.success()
            elif resp.status_code == 403:
                resp.failure("Permission denied: session may be invalid")
            elif resp.status_code == 404:
                resp.failure(f"Poll not found: {poll_id}")
            else:
                resp.failure(f"Results failed: {resp.status_code} - {resp.text}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("Starting load test with Locust...")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    print("Load test completed.")