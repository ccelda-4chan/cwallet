# Nexus Wallet
A high-fidelity mobile crypto wallet.

## Features
- **Mobile-First Design**: Optimized for iOS and Android with a dark theme and modern UI.
- **USDT Transactions**: Advanced USDT sending flow with network selection (ERC-20, TRC-20, BEP-20) and QR support.
- **Asset Management**: Realistic view of multi-chain assets and activity.
- **PWA Ready**: Can be installed on mobile devices for a native app experience.
- **Secure Access**: Protected by a 6-digit PIN authentication.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Set `APP_PASSWORD` environment variable (default: `090902`).
3. Run: `python app.py`

## Deployment
This app is configured for deployment on Render using a **Dockerfile** to ensure maximum compatibility. 
Ensure your Render service is connected to the `main` (or `master`) branch.

**Troubleshooting Build Failures:**
If Render still fails, verify on the Render Dashboard that the **Environment** for your service is set to **Docker** (or that it is reading your `render.yaml`).
