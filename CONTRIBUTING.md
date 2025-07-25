# CONTRIBUTING.md

## 🧑‍💻 Local Development

These instructions are for developers who want to run the project outside of Docker or contribute to the codebase in more depth.

### 1. Prerequisites

* Python 3.12.3
* [virtualenv](https://virtualenv.pypa.io/en/latest/)

### 2. Clone the Repository

```bash
git clone git@github.com:liverealitygames/lrg-network.git
cd lrg-network
```

If you're not set up for SSH:

* [Generate an SSH key](https://help.github.com/articles/generating-ssh-keys)
* Add it to your GitHub account

### 3. Set Up the Environment

```bash
cp .env.example .env
```

* Generate a Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

* Contact Austin for AWS credentials or other secrets.

### 4. Set Up a Virtual Environment

```bash
python3 -m venv lrgvenv
source lrgvenv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```

### 5. Database Setup

```bash
python manage.py migrate
python manage.py cities_light
```

(Optional) To speed up local setup, restrict the locations imported in `settings.py`:

```python
CITIES_LIGHT_INCLUDE_COUNTRIES = ['US', 'CA']
```

### 6. Run the Development Server

```bash
python manage.py runserver 0:8001
```

Visit [http://localhost:8001](http://localhost:8001) to confirm it's working.

---

## 🐳 Docker Usage (Local Dev)

To build and run the app with Docker:

```bash
cp .env.example .env
# Fill out required values in .env

docker compose up --build
```

This runs both the web app and a PostgreSQL database. The DB is persisted using a Docker volume.

To run Django commands inside the web container:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py cities_light
```

---

## Using the Makefile

To simplify your development workflow, you can use the provided `Makefile` with common commands for building, running, migrating, and managing the project:

```bash
make help

---

## 🧪 Testing

*TODO: Add test setup steps if/when tests are implemented.*

---

## 📦 Production Deployment

Production deployment is handled via [Fly.io](https://fly.io) with environment variables and secrets configured via the dashboard or `flyctl` CLI.

Media is stored in AWS S3, optionally served via CloudFront CDN.

---

## 🤝 Contributing Guidelines

* Use feature branches for new development.
* Keep pull requests focused and well-documented.
* Ask questions or check in with Austin before making major changes to architecture or deployment logic.
