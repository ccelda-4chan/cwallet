# ONSINTaru
A high-performance OSINT (Open Source Intelligence) tool platform.

## Features
- **Email Lookup**: Check where an email is registered using `Holehe`.
- **Username Search**: Find accounts across 300+ sites with `Sherlock`.
- **IP Intelligence**: Infrastructure and vulnerability mapping via `Shodan`.
- **Settings Management**: Enable or disable tools based on API availability or preference.
- **Async Execution**: Real-time scan progress using FastAPI background tasks.
- **Persistent Storage**: Scan history stored in MongoDB via Motor.
- **Modern UI**: Clean, responsive dashboard built with Tailwind CSS.

## Setup
1. Clone the repository to `C:\Users\Sam\Documents\GitHub\ONSINTaru`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set environment variables:
   - `SHODAN_API_KEY`: Your Shodan API key.
   - `CENSYS_API_ID`: Your Censys API ID.
   - `CENSYS_API_SECRET`: Your Censys API secret.
   - `MONGO_URI`: MongoDB connection string (default: `mongodb://localhost:27017`).
4. Run locally: `python main.py`.

## Deployment
This app is ready for deployment on **Render.com**.

**Start Command for Render:**
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

- It uses the provided `render.yaml` for automatic infrastructure provisioning.
- The `Dockerfile` ensures a consistent Python 3.10 environment.
- Environment variables must be set in the Render Dashboard for full functionality.
