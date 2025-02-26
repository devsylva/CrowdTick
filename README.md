# CrowdTick
# Real-Time Social Polling Platform

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.x-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A scalable web application built with Python and Django that allows users to create polls, cast votes, and view live results—designed to handle high traffic efficiently.

## Aim
To create a robust polling platform that maintains performance and reliability under heavy user load, showcasing scalable backend engineering principles.

## Objectives
- **Functional Polling System**: Enable poll creation, voting, and real-time result updates with a intuitive interface.
- **Scalability**: Implement horizontal scaling, caching, and async processing to handle traffic spikes.
- **High-Traffic Resilience**: Validate performance under simulated loads (e.g., 1,000 users) with metrics like response time and error rate.
- **Efficient Architecture**: Build a modular, cost-effective system using best practices.

## What We Hope to Achieve
1. **Robust Backend**: Handles thousands of users with minimal performance drop.
2. **Proof of Scalability**: Load testing data showing flat response times and low errors as load increases.
3. **Real-World Ready**: A prototype applicable to high-traffic use cases (e.g., social media, live events).
4. **Skill Mastery**: Deep understanding of scalable web development and testing.

## Project Components

### Tech Stack
- **Backend**: Python, Django, Django REST Framework
- **Database**: PostgreSQL (indexed, replicable)
- **Caching & Messaging**: Redis (results cache, WebSocket layer)
- **Async Processing**: Celery (vote handling)
- **Real-Time**: Django Channels (WebSocket updates)
- **Server**: Gunicorn (WSGI), Nginx (load balancer/proxy)
- **Deployment**: Docker (local), AWS ECS (cloud, optional)
- **Testing**: Locust (load testing)

### Features
- **Poll Creation**: Users create polls with multiple options (`POST /polls/`).
- **Voting**: Async vote processing via API (`POST /votes/`).
- **Live Results**: Real-time updates with WebSockets, cached in Redis (`GET /polls/{id}/results/`).
- **Scalability**: Load-balanced instances, caching, optimized queries.

### Success Metrics
- **Performance**: <200ms response time under 1,000 concurrent users.
- **Throughput**: High requests/sec with no downtime.
- **Stability**: <1% error rate during sustained load.

## Getting Started

### Prerequisites
- Python 3.9+
- Docker (optional for containerized setup)
- PostgreSQL, Redis

### Installation
Clone the repo:
```bash
git clone https://github.com/devsylva/CrowdTick.git
cd CrowdTick
```


### Set up a virtual environment
```bash
python -m venv venv
source venv/bin/acitvate # On Windows: venv\Scripts\activate
```
    
### Install dependecies
```bash
pip install -r requirements.txt
```

### Configure environment variables (e.g., database URL, Redis host) in `.env`.


### Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```


## Testing Scalability
Use Locust to simulate high traffic:
    ```bash
    locust -f locustfile.py --host=http://localhost:8000
    ```

