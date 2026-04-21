from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
import os
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NexusWalletWeb")

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key-change-me")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "admin")

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
    <title>Nexus Wallet - Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
</head>
<body class="bg-[#0F172A] text-white flex items-center justify-center min-h-screen p-6">
    <div class="w-full max-w-md bg-[#1E293B] p-8 rounded-3xl shadow-2xl border border-slate-700/50">
        <div class="text-center mb-10">
            <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20 mx-auto mb-4">
                <i class="fas fa-wallet text-3xl"></i>
            </div>
            <h1 class="text-3xl font-bold text-white tracking-tight">Nexus Wallet</h1>
            <p class="text-slate-400 mt-2">Secure access to your assets</p>
        </div>
        
        <form method="POST" class="space-y-6">
            <div>
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Access Password</label>
                <div class="relative">
                    <input type="password" name="password" placeholder="••••••••" required 
                           class="w-full bg-[#0F172A] border border-slate-700 rounded-2xl py-4 px-5 focus:outline-none focus:ring-2 focus:ring-sky-500 text-white transition-all">
                    <i class="fas fa-lock absolute right-5 top-1/2 -translate-y-1/2 text-slate-500"></i>
                </div>
            </div>
            
            <button type="submit" class="w-full bg-sky-500 hover:bg-sky-400 py-4 rounded-2xl font-bold shadow-lg shadow-sky-500/20 active:scale-[0.98] transition-all">
                Login
            </button>
        </form>
        
        {% if error %}
        <div class="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-sm text-center">
            <i class="fas fa-exclamation-circle mr-2"></i> {{ error }}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

WALLET_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Nexus Wallet">
    <title>Nexus Wallet</title>
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background-color: #0F172A;
            color: white;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }
        .safe-area-inset-top {
            padding-top: env(safe-area-inset-top);
        }
        .glass {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .coin-card:active {
            transform: scale(0.98);
            background: rgba(51, 65, 85, 0.5);
        }
        .tab-active {
            color: #38BDF8;
        }
    </style>
</head>
<body class="safe-area-inset-top font-sans overflow-hidden h-screen flex flex-col">
    <!-- Header -->
    <div class="px-6 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <i class="fas fa-user text-sm"></i>
            </div>
            <div>
                <p class="text-xs text-slate-400">Welcome back,</p>
                <p class="font-bold">Sam IT</p>
            </div>
        </div>
        <div class="flex gap-4">
            <button class="w-10 h-10 rounded-full glass flex items-center justify-center">
                <i class="fas fa-bell text-slate-400"></i>
            </button>
            <a href="/logout" class="w-10 h-10 rounded-full glass flex items-center justify-center text-red-400">
                <i class="fas fa-sign-out-alt"></i>
            </a>
        </div>
    </div>

    <!-- Main Content Scroll Area -->
    <div class="flex-1 overflow-y-auto px-6 pb-24">
        <!-- Balance Card -->
        <div class="mt-4 p-6 rounded-3xl bg-gradient-to-br from-sky-500 to-blue-700 shadow-2xl shadow-blue-500/30 relative overflow-hidden">
            <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
            <p class="text-sky-100 text-sm opacity-80">Total Balance</p>
            <h2 class="text-4xl font-bold mt-1">$42,560.84</h2>
            <div class="flex items-center gap-2 mt-2 text-sky-100 text-sm">
                <span class="bg-white/20 px-2 py-0.5 rounded-full">+2.45%</span>
                <span>last 24h</span>
            </div>
            
            <div class="flex justify-between mt-8">
                <button onclick="showSend()" class="flex flex-col items-center gap-2 group">
                    <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                        <i class="fas fa-arrow-up rotate-45"></i>
                    </div>
                    <span class="text-xs font-medium">Send</span>
                </button>
                <button class="flex flex-col items-center gap-2 group">
                    <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                        <i class="fas fa-arrow-down -rotate-45"></i>
                    </div>
                    <span class="text-xs font-medium">Receive</span>
                </button>
                <button class="flex flex-col items-center gap-2 group">
                    <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                        <i class="fas fa-repeat"></i>
                    </div>
                    <span class="text-xs font-medium">Swap</span>
                </button>
                <button class="flex flex-col items-center gap-2 group">
                    <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                        <i class="fas fa-plus"></i>
                    </div>
                    <span class="text-xs font-medium">Buy</span>
                </button>
            </div>
        </div>

        <!-- Assets -->
        <div class="mt-8">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-lg font-bold">Your Assets</h3>
                <button class="text-sky-400 text-sm">See All</button>
            </div>
            
            <div class="space-y-3">
                <!-- Tether -->
                <div class="coin-card p-4 rounded-2xl glass flex justify-between items-center transition-all cursor-pointer">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-full bg-[#26A17B]/20 flex items-center justify-center">
                            <i class="fab fa-ethereum text-[#26A17B] text-xl"></i>
                        </div>
                        <div>
                            <p class="font-bold">Tether</p>
                            <p class="text-xs text-slate-400">USDT</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold">25,400.00</p>
                        <p class="text-xs text-slate-400">$25,400.00</p>
                    </div>
                </div>

                <!-- Bitcoin -->
                <div class="coin-card p-4 rounded-2xl glass flex justify-between items-center transition-all cursor-pointer">
                    <div class="flex items-center gap-4">
                        <div class="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center">
                            <i class="fab fa-bitcoin text-orange-500 text-xl"></i>
                        </div>
                        <div>
                            <p class="font-bold">Bitcoin</p>
                            <p class="text-xs text-slate-400">BTC</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold">0.42069</p>
                        <p class="text-xs text-slate-400">$17,160.84</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Transactions -->
        <div class="mt-8">
            <h3 class="text-lg font-bold mb-4">Activity</h3>
            <div class="space-y-4">
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full glass flex items-center justify-center">
                            <i class="fas fa-arrow-down text-green-500 text-xs"></i>
                        </div>
                        <div>
                            <p class="text-sm font-medium">Received USDT</p>
                            <p class="text-[10px] text-slate-500">Today, 10:45 AM</p>
                        </div>
                    </div>
                    <p class="text-sm font-bold text-green-500">+$1,200.00</p>
                </div>
                <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full glass flex items-center justify-center">
                            <i class="fas fa-arrow-up text-red-500 text-xs"></i>
                        </div>
                        <div>
                            <p class="text-sm font-medium">Sent USDT</p>
                            <p class="text-[10px] text-slate-500">Yesterday, 4:20 PM</p>
                        </div>
                    </div>
                    <p class="text-sm font-bold">-$450.00</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Bottom Nav -->
    <div class="fixed bottom-0 left-0 right-0 glass h-20 px-8 flex justify-between items-center rounded-t-[32px]">
        <button class="tab-active flex flex-col items-center gap-1">
            <i class="fas fa-wallet text-xl"></i>
            <span class="text-[10px]">Wallet</span>
        </button>
        <button class="text-slate-500 flex flex-col items-center gap-1">
            <i class="fas fa-chart-pie text-xl"></i>
            <span class="text-[10px]">Market</span>
        </button>
        <button class="text-slate-500 flex flex-col items-center gap-1">
            <i class="fas fa-compass text-xl"></i>
            <span class="text-[10px]">DApps</span>
        </button>
        <button class="text-slate-500 flex flex-col items-center gap-1">
            <i class="fas fa-gear text-xl"></i>
            <span class="text-[10px]">Settings</span>
        </button>
    </div>

    <!-- Send Modal -->
    <div id="sendModal" class="fixed inset-0 z-50 translate-y-full transition-transform duration-300 ease-out flex flex-col">
        <div class="flex-1 bg-black/60 backdrop-blur-sm" onclick="hideSend()"></div>
        <div class="glass rounded-t-[40px] px-6 pt-8 pb-12 flex flex-col gap-6">
            <div class="w-12 h-1 bg-slate-700 rounded-full mx-auto -mt-4"></div>
            
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold">Send USDT</h2>
                <button onclick="hideSend()" class="text-slate-400">Cancel</button>
            </div>

            <div>
                <label class="text-xs text-slate-400 mb-2 block uppercase tracking-wider">Network</label>
                <div class="grid grid-cols-3 gap-3">
                    <button class="py-3 glass rounded-2xl border-sky-500 bg-sky-500/10 text-xs">ERC-20</button>
                    <button class="py-3 glass rounded-2xl text-xs border-transparent">TRC-20</button>
                    <button class="py-3 glass rounded-2xl text-xs border-transparent">BEP-20</button>
                </div>
            </div>

            <div>
                <label class="text-xs text-slate-400 mb-2 block uppercase tracking-wider">Recipient Address</label>
                <div class="relative">
                    <input type="text" placeholder="Paste address or domain" class="w-full glass rounded-2xl py-4 px-5 pr-12 text-sm focus:outline-none focus:ring-1 focus:ring-sky-500">
                    <i class="fas fa-paste absolute right-4 top-1/2 -translate-y-1/2 text-slate-500"></i>
                </div>
            </div>

            <div>
                <label class="text-xs text-slate-400 mb-2 block uppercase tracking-wider">Amount</label>
                <div class="relative">
                    <input type="number" placeholder="0.00" class="w-full glass rounded-2xl py-4 px-5 pr-20 text-2xl font-bold focus:outline-none focus:ring-1 focus:ring-sky-500">
                    <span class="absolute right-4 top-1/2 -translate-y-1/2 text-sky-400 font-bold">MAX</span>
                </div>
                <div class="flex justify-between mt-2 px-1">
                    <p class="text-xs text-slate-400">Available: 25,400.00 USDT</p>
                    <p class="text-xs text-slate-400">≈ $0.00</p>
                </div>
            </div>

            <button id="sendBtn" onclick="processSend()" class="w-full bg-sky-500 py-4 rounded-2xl font-bold shadow-lg shadow-sky-500/20 active:scale-[0.98] transition-all mt-4">
                Send USDT
            </button>
        </div>
    </div>

    <!-- Success Screen Overlay -->
    <div id="successScreen" class="fixed inset-0 z-[60] bg-[#0F172A] hidden flex flex-col items-center justify-center p-8 text-center">
        <div class="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mb-8 shadow-2xl shadow-green-500/20 animate-bounce">
            <i class="fas fa-check text-4xl"></i>
        </div>
        <h2 class="text-3xl font-bold mb-2">Transfer Successful</h2>
        <p class="text-slate-400 mb-12">Your USDT is on its way to the recipient on the ERC-20 network.</p>
        
        <div class="w-full glass rounded-3xl p-6 mb-12 space-y-4">
            <div class="flex justify-between text-sm">
                <span class="text-slate-400">Transaction ID</span>
                <span class="text-sky-400 truncate ml-8">0x8a2c...4f9b</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-slate-400">Status</span>
                <span class="text-green-500">Confirmed</span>
            </div>
            <div class="flex justify-between text-sm">
                <span class="text-slate-400">Network Fee</span>
                <span class="font-medium">$4.52</span>
            </div>
        </div>

        <button onclick="resetUI()" class="w-full glass py-4 rounded-2xl font-bold">Done</button>
    </div>

    <script>
        function showSend() {
            document.getElementById('sendModal').classList.remove('translate-y-full');
        }

        function hideSend() {
            document.getElementById('sendModal').classList.add('translate-y-full');
        }

        function processSend() {
            const btn = document.getElementById('sendBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Processing...';
            
            setTimeout(() => {
                document.getElementById('successScreen').classList.remove('hidden');
                hideSend();
            }, 1500);
        }

        function resetUI() {
            document.getElementById('successScreen').classList.add('hidden');
            const btn = document.getElementById('sendBtn');
            btn.disabled = false;
            btn.innerHTML = 'Send USDT';
        }

        // Network selection logic
        const netBtns = document.querySelectorAll('#sendModal button.py-3');
        netBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                netBtns.forEach(b => {
                    b.classList.remove('border-sky-500', 'bg-sky-500/10');
                    b.classList.add('border-transparent');
                });
                btn.classList.add('border-sky-500', 'bg-sky-500/10');
                btn.classList.remove('border-transparent');
            });
        });
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
            return redirect(url_for('wallet'))
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
    return redirect(url_for('wallet'))

@app.route('/wallet')
@login_required
def wallet():
    return render_template_string(WALLET_TEMPLATE)

@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
