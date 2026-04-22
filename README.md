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

### ⚠️ IMPORTANT: Fix Deployment "Status 127"
If your deploy fails with `guvicorn: command not found`, it is because of a typo in the Render Dashboard.
1. Go to your **Render Dashboard**.
2. Select your **Web Service** (osint-tool).
3. Go to **Settings**.
4. Find the **Start Command** field.
5. Change `guvicorn` to `uvicorn`. It should be:
   `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. Save and Redeploy.

### Alternative Deployment (Docker)
This repo includes a `render.yaml` and `Dockerfile`. For the best experience:
1. Use the **Blueprints** feature in Render to connect this repository.
2. It will automatically use Docker, which handles all dependencies and start commands correctly.
