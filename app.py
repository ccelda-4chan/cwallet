from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for
import asyncio
import threading
from Trapdev import SMSBomber, normalize_phone_number
import os
import re
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SolidBomberWeb")

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key-change-me")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "admin")

# Concurrency control
MAX_CONCURRENT_ATTACKS = 10
attack_semaphore = threading.Semaphore(MAX_CONCURRENT_ATTACKS)
active_attacks_count = 0
active_attacks_lock = threading.Lock()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SOLID BOMBER PRO - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #121212; color: #e0e0e0; max-width: 400px; margin: 100px auto; padding: 20px; }
        .card { background: #1e1e1e; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        h1 { color: #bb86fc; text-align: center; font-size: 24px; margin-bottom: 30px; }
        label { display: block; margin-top: 10px; color: #03dac6; }
        input { width: 100%; padding: 12px; margin-top: 5px; border-radius: 4px; border: 1px solid #333; background: #2c2c2c; color: white; box-sizing: border-box; }
        button { width: 100%; background: #6200ee; border: none; font-weight: bold; cursor: pointer; margin-top: 30px; padding: 12px; border-radius: 4px; color: white; }
        button:hover { background: #3700b3; }
        .error { color: #f44336; margin-top: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="card">
        <h1>SOLID BOMBER PRO</h1>
        <form method="POST">
            <label>Password</label>
            <input type="password" name="password" placeholder="Enter password" required>
            <button type="submit">LOGIN</button>
        </form>
        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>SOLID BOMBER PRO - Web</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; background: #121212; color: #e0e0e0; max-width: 600px; margin: 0 auto; padding: 20px; }
        .card { background: #1e1e1e; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .logout { color: #f44336; text-decoration: none; font-size: 14px; }
        h1 { color: #bb86fc; text-align: center; margin: 0; }
        label { display: block; margin-top: 10px; color: #03dac6; }
        input, select, button { width: 100%; padding: 10px; margin-top: 5px; border-radius: 4px; border: 1px solid #333; background: #2c2c2c; color: white; box-sizing: border-box; }
        button { background: #6200ee; border: none; font-weight: bold; cursor: pointer; margin-top: 20px; }
        button:hover { background: #3700b3; }
        #status { margin-top: 20px; padding: 15px; border-radius: 4px; display: none; background: #333; }
        .success { color: #4caf50; }
        .fail { color: #f44336; }
    </style>
</head>
<body>
    <div class="nav">
        <span></span>
        <h1>SOLID BOMBER PRO</h1>
        <a href="/logout" class="logout">Logout</a>
    </div>
    <div class="card">
        <form id="bombForm">
            <label>Phone Number (PH format)</label>
            <input type="text" id="phone" placeholder="09123456789" required>
            
            <label>Amount (Max 50 for Web)</label>
            <input type="number" id="amount" value="5" min="1" max="50">
            
            <label>Services</label>
            <select id="services" multiple style="height: 100px;">
                <option value="all" selected>All Services</option>
                <option value="CUSTOM_SMS">Custom SMS</option>
                <option value="EZLOAN">EzLoan</option>
                <option value="XPRESS">Xpress PH</option>
                <option value="ABENSON">Abenson</option>
                <option value="EXCELLENT_LENDING">Excellent Lending</option>
                <option value="FORTUNE_PAY">Fortune Pay</option>
                <option value="WEMOVE">WeMove</option>
                <option value="LBC">LBC Connect</option>
                <option value="PICKUP_COFFEE">Pickup Coffee</option>
                <option value="HONEY_LOAN">Honey Loan</option>
                <option value="KOMO_PH">Komo PH</option>
                <option value="S5_OTP">S5.com</option>
                <option value="CALL_BOMB">Call Bomb</option>
            </select>
            
            <button type="submit">LAUNCH ATTACK</button>
        </form>
        
        <div id="status">
            <div id="progressText">Starting...</div>
            <div id="stats"></div>
        </div>
    </div>

    <script>
        document.getElementById('bombForm').onsubmit = async (e) => {
            e.preventDefault();
            const btn = e.target.querySelector('button');
            const statusDiv = document.getElementById('status');
            const progressText = document.getElementById('progressText');
            const statsDiv = document.getElementById('stats');
            
            btn.disabled = true;
            btn.innerText = 'ATTACKING...';
            statusDiv.style.display = 'block';
            progressText.innerText = 'Initiating request...';
            statsDiv.innerText = '';

            const phone = document.getElementById('phone').value;
            const amount = document.getElementById('amount').value;
            const selectedOptions = Array.from(document.getElementById('services').selectedOptions).map(o => o.value);
            
            const services = selectedOptions.includes('all') ? null : selectedOptions;

            try {
                const response = await fetch('/attack', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({phone, amount, services})
                });
                const data = await response.json();
                
                if (data.success) {
                    progressText.innerText = 'Attack triggered successfully!';
                    statsDiv.innerHTML = `<p class="success">Attack on ${phone} is running in background.</p>
                                          <p>Check logs for progress.</p>`;
                } else {
                    progressText.innerText = 'Error occurred';
                    statsDiv.innerHTML = `<p class="fail">${data.error}</p>`;
                }
            } catch (err) {
                progressText.innerText = 'Connection error';
                statsDiv.innerHTML = `<p class="fail">${err.message}</p>`;
            } finally {
                btn.disabled = false;
                btn.innerText = 'LAUNCH ATTACK';
            }
        };
    </script>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == APP_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid Password!")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template_string(HTML_TEMPLATE)

def run_async_attack(phone, amount, services):
    global active_attacks_count
    
    if not attack_semaphore.acquire(blocking=False):
        logger.warning(f"Attack rejected: MAX_CONCURRENT_ATTACKS reached ({MAX_CONCURRENT_ATTACKS})")
        return

    with active_attacks_lock:
        active_attacks_count += 1

    try:
        logger.info(f"Starting attack on {phone} (Amount: {amount})")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def attack():
            async with SMSBomber() as bomber:
                await bomber.execute_attack(phone, amount, services)
                logger.info(f"Attack finished for {phone}. Stats: {bomber.get_stats()}")
        
        loop.run_until_complete(attack())
        loop.close()
    except Exception as e:
        logger.error(f"Error in attack thread for {phone}: {str(e)}")
    finally:
        with active_attacks_lock:
            active_attacks_count -= 1
        attack_semaphore.release()

@app.route('/status')
@login_required
def status():
    return jsonify({
        "active_attacks": active_attacks_count,
        "max_concurrent": MAX_CONCURRENT_ATTACKS
    })

@app.route('/attack', methods=['POST'])
@login_required
def attack():
    data = request.json
    phone = data.get('phone')
    amount = int(data.get('amount', 5))
    services = data.get('services')

    if not phone or not re.match(r'^(09\d{9}|9\d{9}|\+639\d{9})$', phone.replace(' ', '')):
        return jsonify({"success": False, "error": "Invalid phone number format"}), 400

    if active_attacks_count >= MAX_CONCURRENT_ATTACKS:
        return jsonify({"success": False, "error": "Server is busy. Please try again later."}), 429

    if amount > 50:
        amount = 50

    # Start attack in a separate thread
    thread = threading.Thread(target=run_async_attack, args=(phone, amount, services))
    thread.daemon = True
    thread.start()

    return jsonify({"success": True, "message": "Attack initiated"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
