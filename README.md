# lrg-network

## 🌐 Overview

lrg-network is a Django web application for managing and displaying data about Live Reality Games (LRGs). It includes functionality for event listings, player profiles, and media uploads.

---

## 🚀 Quickstart (Docker)

If you're a developer, the easiest way to get started is with Docker:

```bash
git clone git@github.com:liverealitygames/lrg-network.git
cd lrg-network
cp .env.example .env

# ⚠️ IMPORTANT:
# Open the newly created `.env` file and fill in the required environment variables.
# At a minimum, Docker needs the following for local development:
#
# POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
# AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME
# DJANGO_SECRET_KEY
#
# If you're missing these values, contact a project maintainer.

# Build and start the app
docker compose up --build
```

Then open [http://localhost:8001](http://localhost:8001) in your browser.

For more detailed setup, environment configuration, and developer instructions, see CONTRIBUTING.md.

---

## 🛠 Tech Stack

* Python 3.12 / Django
* PostgreSQL
* AWS S3 (media storage)
* Cloudflare (CDN)
* Docker

---

## 📄 License

This project is licensed under the MIT License.
