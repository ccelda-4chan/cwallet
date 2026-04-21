from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
import os
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NexusWalletWeb")

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key-change-me")
APP_PASSWORD = os.environ.get("APP_PASSWORD", "090902")

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
    <title>Nexus Wallet - Access</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body {
            background-color: #0F172A;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            overflow: hidden;
            user-select: none;
            -webkit-tap-highlight-color: transparent;
        }
        .pin-dot {
            width: 14px;
            height: 14px;
            border-radius: 50%;
            border: 2px solid #334155;
            transition: all 0.2s;
        }
        .pin-dot.filled {
            background-color: #38BDF8;
            border-color: #38BDF8;
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
        }
        .key {
            aspect-ratio: 1/1;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: 600;
            border-radius: 50%;
            background: rgba(30, 41, 59, 0.5);
            transition: all 0.1s;
            cursor: pointer;
        }
        .key:active {
            background: rgba(56, 189, 248, 0.2);
            transform: scale(0.9);
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        .shake { animation: shake 0.2s ease-in-out 0s 2; }
    </style>
</head>
<body class="text-white flex flex-col items-center justify-center min-h-screen p-6 safe-area-inset-top safe-area-inset-bottom">
    <div class="w-full max-w-sm flex flex-col items-center">
        <!-- Logo & Header -->
        <div class="text-center mb-12 animate-fade-in">
            <div class="w-20 h-20 rounded-3xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20 mx-auto mb-6">
                <i class="fas fa-shield-halved text-3xl"></i>
            </div>
            <h1 class="text-2xl font-bold tracking-tight text-white">Enter Passcode</h1>
            <p class="text-slate-400 mt-2 text-sm">Please enter your security PIN</p>
        </div>

        <!-- PIN Display -->
        <div id="pin-display" class="flex gap-6 mb-16">
            <div class="pin-dot"></div>
            <div class="pin-dot"></div>
            <div class="pin-dot"></div>
            <div class="pin-dot"></div>
            <div class="pin-dot"></div>
            <div class="pin-dot"></div>
        </div>

        <!-- Numeric Keypad -->
        <div class="grid grid-cols-3 gap-8 w-full px-8">
            <button class="key" onclick="appendPin('1')">1</button>
            <button class="key" onclick="appendPin('2')">2</button>
            <button class="key" onclick="appendPin('3')">3</button>
            <button class="key" onclick="appendPin('4')">4</button>
            <button class="key" onclick="appendPin('5')">5</button>
            <button class="key" onclick="appendPin('6')">6</button>
            <button class="key" onclick="appendPin('7')">7</button>
            <button class="key" onclick="appendPin('8')">8</button>
            <button class="key" onclick="appendPin('9')">9</button>
            <div class="flex items-center justify-center">
                <i class="fas fa-fingerprint text-slate-700 text-2xl"></i>
            </div>
            <button class="key" onclick="appendPin('0')">0</button>
            <button class="key" onclick="deletePin()">
                <i class="fas fa-backspace text-xl"></i>
            </button>
        </div>

        <!-- Hidden Form -->
        <form id="loginForm" method="POST" class="hidden">
            <input type="hidden" name="password" id="hiddenPin">
        </form>

        {% if error %}
        <div id="errorMsg" class="mt-12 p-4 bg-red-500/10 border border-red-500/20 rounded-2xl text-red-400 text-sm text-center flex items-center gap-2">
            <i class="fas fa-exclamation-circle"></i> {{ error }}
        </div>
        {% endif %}
    </div>

    <script>
        let currentPin = "";
        const maxPinLength = 6;
        const dots = document.querySelectorAll('.pin-dot');
        const display = document.getElementById('pin-display');
        const form = document.getElementById('loginForm');
        const hiddenInput = document.getElementById('hiddenPin');

        function appendPin(digit) {
            if (currentPin.length < maxPinLength) {
                currentPin += digit;
                updateDots();
                
                if (currentPin.length === maxPinLength) {
                    submitPin();
                }
            }
        }

        function deletePin() {
            if (currentPin.length > 0) {
                currentPin = currentPin.slice(0, -1);
                updateDots();
            }
        }

        function updateDots() {
            dots.forEach((dot, index) => {
                if (index < currentPin.length) {
                    dot.classList.add('filled');
                } else {
                    dot.classList.remove('filled');
                }
            });
        }

        function submitPin() {
            hiddenInput.value = currentPin;
            // Short delay for visual feedback
            setTimeout(() => {
                form.submit();
            }, 200);
        }

        // Add shake effect on error
        {% if error %}
        display.classList.add('shake');
        setTimeout(() => display.classList.remove('shake'), 500);
        {% endif %}

        // Support physical keyboard
        document.addEventListener('keydown', (e) => {
            if (e.key >= '0' && e.key <= '9') {
                appendPin(e.key);
            } else if (e.key === 'Backspace') {
                deletePin();
            }
        });
    </script>
</body>
</html>
"""

WALLET_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Nexus Wallet">
    <title>Nexus Wallet</title>
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        :root {
            --bg-dark: #0F172A;
            --accent: #38BDF8;
        }
        body {
            background-color: var(--bg-dark);
            color: white;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .safe-area-top { padding-top: env(safe-area-inset-top); }
        .safe-area-bottom { padding-bottom: env(safe-area-inset-bottom); }
        .glass {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        .tab-active { color: var(--accent); }
        .screen { display: none; }
        .screen.active { display: flex; }
        .coin-card:active { transform: scale(0.98); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .animate-fade { animation: fadeIn 0.3s ease-out forwards; }
    </style>
</head>
<body class="safe-area-top overflow-hidden h-screen flex flex-col">
    <!-- Header (Shared) -->
    <div id="mainHeader" class="px-6 py-4 flex justify-between items-center z-40">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <i class="fas fa-shield-halved text-sm"></i>
            </div>
            <div>
                <p id="headerAddress" class="font-mono text-xs text-sky-400">0x71C7...976F</p>
                <p class="text-[10px] text-slate-500 uppercase tracking-widest">Verified Wallet</p>
            </div>
        </div>
        <div class="flex gap-4">
            <button class="w-10 h-10 rounded-full glass flex items-center justify-center relative">
                <i class="fas fa-bell text-slate-400"></i>
                <span class="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border-2 border-[#0F172A]"></span>
            </button>
        </div>
    </div>

    <!-- Main Screens Container -->
    <div class="flex-1 relative overflow-hidden">
        
        <!-- WALLET SCREEN -->
        <div id="screen-wallet" class="screen active flex-col h-full overflow-y-auto px-6 pb-24 animate-fade">
            <!-- Balance Card -->
            <div class="mt-4 p-6 rounded-3xl bg-gradient-to-br from-sky-500 to-blue-700 shadow-2xl shadow-blue-500/30 relative overflow-hidden">
                <div class="absolute -right-10 -top-10 w-40 h-40 bg-white/10 rounded-full blur-3xl"></div>
                <p class="text-sky-100 text-sm opacity-80">Total Balance</p>
                <h2 id="displayTotalBalance" class="text-4xl font-bold mt-1 tracking-tight">$11,420.69</h2>
                <div class="flex items-center gap-2 mt-2 text-sky-100 text-sm">
                    <span class="bg-white/20 px-2 py-0.5 rounded-full font-medium">+5.24%</span>
                    <span class="opacity-80">last 24h</span>
                </div>
                
                <div class="flex justify-between mt-8">
                    <button onclick="showSend()" class="flex flex-col items-center gap-2 group">
                        <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                            <i class="fas fa-arrow-up rotate-45"></i>
                        </div>
                        <span class="text-[11px] font-medium">Send</span>
                    </button>
                    <button onclick="showReceive()" class="flex flex-col items-center gap-2 group">
                        <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                            <i class="fas fa-arrow-down -rotate-45"></i>
                        </div>
                        <span class="text-[11px] font-medium">Receive</span>
                    </button>
                    <button class="flex flex-col items-center gap-2 group">
                        <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                            <i class="fas fa-repeat"></i>
                        </div>
                        <span class="text-[11px] font-medium">Swap</span>
                    </button>
                    <button class="flex flex-col items-center gap-2 group">
                        <div class="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center group-active:scale-90 transition-transform">
                            <i class="fas fa-plus"></i>
                        </div>
                        <span class="text-[11px] font-medium">Buy</span>
                    </button>
                </div>
            </div>

            <!-- Assets -->
            <div class="mt-8">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-lg font-bold">Assets</h3>
                    <button class="text-sky-400 text-xs font-semibold uppercase tracking-wider">Manage</button>
                </div>
                
                <div id="assetList" class="space-y-3">
                    <!-- Assets will be populated here -->
                </div>
            </div>

            <!-- Recent Transactions -->
            <div class="mt-8">
                <h3 class="text-lg font-bold mb-4">Activity</h3>
                <div id="activityList" class="space-y-5">
                    <!-- Dynamic history here -->
                </div>
            </div>
        </div>

        <!-- MARKET SCREEN -->
        <div id="screen-market" class="screen flex-col h-full overflow-y-auto px-6 pb-24 animate-fade">
            <h2 class="text-2xl font-bold mt-4 mb-6">Market</h2>
            <div class="flex gap-3 mb-6 overflow-x-auto pb-2 no-scrollbar">
                <button class="px-4 py-2 rounded-full bg-sky-500 text-xs font-bold">All</button>
                <button class="px-4 py-2 rounded-full glass text-xs font-bold text-slate-400">Gainer</button>
                <button class="px-4 py-2 rounded-full glass text-xs font-bold text-slate-400">Loser</button>
                <button class="px-4 py-2 rounded-full glass text-xs font-bold text-slate-400">New</button>
            </div>
            <div id="marketList" class="space-y-4">
                <!-- Market data from API -->
                <div class="flex items-center justify-center py-10">
                    <i class="fas fa-circle-notch fa-spin text-sky-500 text-2xl"></i>
                </div>
            </div>
        </div>

        <!-- DAPPS SCREEN -->
        <div id="screen-dapps" class="screen flex-col h-full overflow-y-auto px-6 pb-24 animate-fade">
            <h2 class="text-2xl font-bold mt-4 mb-6">DApps Browser</h2>
            <div class="glass rounded-2xl p-4 flex items-center gap-3 mb-8">
                <i class="fas fa-search text-slate-500"></i>
                <input type="text" placeholder="Search or enter URL" class="bg-transparent border-none outline-none text-sm w-full">
            </div>
            
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Recommended</h3>
            <div class="grid grid-cols-4 gap-6">
                <div class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl bg-pink-500/20 flex items-center justify-center">
                        <img src="https://uniswap.org/favicon.ico" class="w-8 h-8 rounded-lg" onerror="this.innerHTML='<i class=\'fas fa-exchange-alt text-pink-500\'></i>'">
                    </div>
                    <span class="text-[10px] font-medium text-slate-400">Uniswap</span>
                </div>
                <div class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl bg-yellow-500/20 flex items-center justify-center">
                        <img src="https://pancakeswap.finance/favicon.ico" class="w-8 h-8 rounded-lg">
                    </div>
                    <span class="text-[10px] font-medium text-slate-400">Pancake</span>
                </div>
                <div class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl bg-blue-500/20 flex items-center justify-center">
                        <img src="https://aave.com/favicon.ico" class="w-8 h-8 rounded-lg">
                    </div>
                    <span class="text-[10px] font-medium text-slate-400">Aave</span>
                </div>
                <div class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl bg-white/10 flex items-center justify-center">
                        <i class="fas fa-plus text-slate-500"></i>
                    </div>
                    <span class="text-[10px] font-medium text-slate-400">More</span>
                </div>
            </div>
        </div>

        <!-- SETTINGS SCREEN -->
        <div id="screen-settings" class="screen flex-col h-full overflow-y-auto px-6 pb-24 animate-fade">
            <h2 class="text-2xl font-bold mt-4 mb-6">Settings</h2>
            
            <div class="space-y-2">
                <div class="glass rounded-2xl overflow-hidden">
                    <div class="p-4 flex items-center justify-between border-b border-white/5">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full bg-sky-500/20 flex items-center justify-center">
                                <i class="fas fa-shield-halved text-sky-500"></i>
                            </div>
                            <div>
                                <p class="text-sm font-bold">Security</p>
                                <p class="text-[10px] text-slate-500">PIN & Biometrics</p>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right text-slate-600"></i>
                    </div>
                    <div class="p-4 flex items-center justify-between border-b border-white/5">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center">
                                <i class="fas fa-globe text-purple-500"></i>
                            </div>
                            <div>
                                <p class="text-sm font-bold">Language</p>
                                <p class="text-[10px] text-slate-500">English (US)</p>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right text-slate-600"></i>
                    </div>
                    <div class="p-4 flex items-center justify-between" onclick="handleDevClick()">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full bg-slate-500/20 flex items-center justify-center">
                                <i class="fas fa-circle-info text-slate-400"></i>
                            </div>
                            <div>
                                <p class="text-sm font-bold">About</p>
                                <p class="text-[10px] text-slate-500">v2.4.0 (Stable)</p>
                            </div>
                        </div>
                        <i class="fas fa-chevron-right text-slate-600"></i>
                    </div>
                </div>

                <div class="glass rounded-2xl p-4 flex items-center justify-between text-red-400 mt-4" onclick="location.href='/logout'">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center">
                            <i class="fas fa-sign-out-alt"></i>
                        </div>
                        <p class="text-sm font-bold">Logout</p>
                    </div>
                </div>

                <!-- HIDDEN ADMIN PANEL -->
                <div id="adminPanel" class="hidden animate-fade mt-6 p-6 glass border-sky-500/30 rounded-3xl space-y-4">
                    <h3 class="text-lg font-bold text-sky-400 flex items-center gap-2">
                        <i class="fas fa-user-gear"></i> Wallet Configuration
                    </h3>
                    <div>
                        <label class="text-[10px] text-slate-400 uppercase tracking-widest mb-1 block">Receive Address</label>
                        <input type="text" id="editWalletAddr" value="0x71C7656EC7ab88b098defB751B7401B5f6d8976F" 
                               class="w-full bg-[#0F172A] border border-slate-700 rounded-xl py-2 px-3 text-xs text-sky-400 font-mono focus:outline-none focus:border-sky-500">
                    </div>
                    <div>
                        <label class="text-[10px] text-slate-400 uppercase tracking-widest mb-1 block">USDT Balance</label>
                        <input type="number" id="editBalanceUSDT" value="25400" 
                               class="w-full bg-[#0F172A] border border-slate-700 rounded-xl py-2 px-3 text-xs focus:outline-none focus:border-sky-500">
                    </div>
                    <div>
                        <label class="text-[10px] text-slate-400 uppercase tracking-widest mb-1 block">BTC Amount</label>
                        <input type="number" id="editBalanceBTC" value="0.42069" step="0.0001"
                               class="w-full bg-[#0F172A] border border-slate-700 rounded-xl py-2 px-3 text-xs focus:outline-none focus:border-sky-500">
                    </div>
                    <button onclick="saveSettings()" class="w-full bg-sky-500 py-3 rounded-xl font-bold text-sm shadow-lg shadow-sky-500/20 active:scale-95 transition-all">
                        Save Changes
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bottom Nav -->
    <div class="safe-area-bottom fixed bottom-0 left-0 right-0 glass h-20 px-8 flex justify-between items-center rounded-t-[32px] z-40">
        <button onclick="showScreen('wallet')" class="nav-btn tab-active flex flex-col items-center gap-1" data-screen="wallet">
            <i class="fas fa-wallet text-xl"></i>
            <span class="text-[10px]">Wallet</span>
        </button>
        <button onclick="showScreen('market')" class="nav-btn text-slate-500 flex flex-col items-center gap-1" data-screen="market">
            <i class="fas fa-chart-line text-xl"></i>
            <span class="text-[10px]">Market</span>
        </button>
        <button onclick="showScreen('dapps')" class="nav-btn text-slate-500 flex flex-col items-center gap-1" data-screen="dapps">
            <i class="fas fa-compass text-xl"></i>
            <span class="text-[10px]">DApps</span>
        </button>
        <button onclick="showScreen('settings')" class="nav-btn text-slate-500 flex flex-col items-center gap-1" data-screen="settings">
            <i class="fas fa-gear text-xl"></i>
            <span class="text-[10px]">Settings</span>
        </button>
    </div>

    <!-- Modals (Send/Receive) -->
    <div id="sendModal" class="fixed inset-0 z-50 translate-y-full transition-transform duration-300 ease-out flex flex-col">
        <div class="flex-1 bg-black/60 backdrop-blur-sm" onclick="hideSend()"></div>
        <div class="glass rounded-t-[40px] px-6 pt-8 pb-12 flex flex-col gap-6">
            <div class="w-12 h-1 bg-slate-700 rounded-full mx-auto -mt-4"></div>
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold">Send USDT</h2>
                <div class="flex gap-4">
                    <button onclick="startScanner()" class="text-sky-400">
                        <i class="fas fa-qrcode text-xl"></i>
                    </button>
                    <button onclick="hideSend()" class="text-slate-400">Cancel</button>
                </div>
            </div>
            <div>
                <label class="text-[10px] text-slate-400 mb-2 block uppercase tracking-widest font-bold">Network</label>
                <div id="net-selection" class="grid grid-cols-3 gap-3">
                    <button onclick="setNetwork('ERC-20')" class="net-btn py-3 glass rounded-2xl border-sky-500 bg-sky-500/10 text-[10px] font-bold transition-all" id="btn-ERC-20">ERC-20</button>
                    <button onclick="setNetwork('TRC-20')" class="net-btn py-3 glass rounded-2xl text-[10px] border-transparent font-bold transition-all" id="btn-TRC-20">TRC-20</button>
                    <button onclick="setNetwork('BEP-20')" class="net-btn py-3 glass rounded-2xl text-[10px] border-transparent font-bold transition-all" id="btn-BEP-20">BEP-20</button>
                </div>
            </div>
            <div>
                <label class="text-[10px] text-slate-400 mb-2 block uppercase tracking-widest font-bold">Recipient</label>
                <div class="relative">
                    <input id="sendRecipient" type="text" placeholder="Address or Domain" class="w-full glass rounded-2xl py-4 px-5 pr-12 text-sm focus:outline-none">
                    <i class="fas fa-paste absolute right-4 top-1/2 -translate-y-1/2 text-slate-500"></i>
                </div>
            </div>
            <div>
                <label class="text-[10px] text-slate-400 mb-2 block uppercase tracking-widest font-bold">Amount</label>
                <div class="relative">
                    <input id="sendAmount" type="number" placeholder="0.00" class="w-full glass rounded-2xl py-4 px-5 text-2xl font-bold focus:outline-none">
                    <span class="absolute right-4 top-1/2 -translate-y-1/2 text-sky-400 font-bold">MAX</span>
                </div>
            </div>
            <button id="sendBtn" onclick="processSend()" class="w-full bg-sky-500 py-4 rounded-2xl font-bold shadow-lg shadow-sky-500/20 mt-2">Send</button>
        </div>
    </div>

    <div id="receiveModal" class="fixed inset-0 z-50 translate-y-full transition-transform duration-300 ease-out flex flex-col">
        <div class="flex-1 bg-black/60 backdrop-blur-sm" onclick="hideReceive()"></div>
        <div class="glass rounded-t-[40px] px-6 pt-8 pb-12 flex flex-col gap-6 items-center">
            <div class="w-12 h-1 bg-slate-700 rounded-full mx-auto -mt-4"></div>
            <div class="w-full flex justify-between items-center">
                <h2 class="text-2xl font-bold">Receive</h2>
                <button onclick="hideReceive()" class="text-slate-400">Close</button>
            </div>
            <div class="bg-white p-4 rounded-3xl mt-4">
                <img id="receiveQR" src="" alt="QR" class="w-48 h-48">
            </div>
            <div class="w-full space-y-2 text-center">
                <p class="text-[10px] text-slate-500 uppercase tracking-widest">Your Address (ERC-20)</p>
                <div class="glass rounded-2xl p-4 flex justify-between items-center bg-slate-800/50 overflow-hidden">
                    <p id="receiveAddrDisplay" class="text-[10px] font-mono text-sky-400 truncate mr-4"></p>
                    <button onclick="copyAddress()" class="text-sky-400 text-xs font-bold whitespace-nowrap">COPY</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Success Screen Overlay -->
    <div id="successScreen" class="fixed inset-0 z-[60] bg-[#0F172A] hidden flex flex-col items-center justify-center p-8 text-center">
        <div class="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mb-8 shadow-2xl shadow-green-500/20">
            <i class="fas fa-check text-4xl"></i>
        </div>
        <h2 class="text-3xl font-bold mb-2">Success</h2>
        <p class="text-slate-400 mb-8">Transaction has been broadcasted.</p>
        
        <div class="w-full glass rounded-3xl p-6 mb-12 space-y-4">
            <div class="flex justify-between">
                <span class="text-xs text-slate-500 uppercase tracking-widest">Amount</span>
                <span id="successAmount" class="text-sm font-bold text-sky-400"></span>
            </div>
            <div class="flex justify-between">
                <span class="text-xs text-slate-500 uppercase tracking-widest">Network Fee</span>
                <span id="successFee" class="text-sm font-bold"></span>
            </div>
            <div class="flex justify-between border-t border-white/5 pt-4">
                <span class="text-xs text-slate-500 uppercase tracking-widest">Transaction ID</span>
                <span id="successTxn" class="text-xs font-mono text-slate-400"></span>
            </div>
        </div>
        
        <button onclick="resetUI()" class="w-full glass py-4 rounded-2xl font-bold">Done</button>
    </div>

    <div id="scannerModal" class="fixed inset-0 z-[70] bg-black hidden flex flex-col">
        <div id="reader" class="flex-1"></div>
        <button onclick="stopScanner()" class="absolute top-10 right-6 w-12 h-12 glass rounded-full flex items-center justify-center z-[80]">
            <i class="fas fa-times"></i>
        </button>
    </div>

    <script>
        let walletState = {
            address: localStorage.getItem('wallet_addr') || "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            selectedNetwork: 'ERC-20',
            assets: JSON.parse(localStorage.getItem('wallet_assets')) || [
                { id: 'tether', symbol: 'USDT', name: 'Tether', balance: 3420.00, icon: 'fab fa-ethereum', color: '#26A17B' },
                { id: 'bitcoin', symbol: 'BTC', name: 'Bitcoin', balance: 0.1254, icon: 'fab fa-bitcoin', color: '#F7931A' },
                { id: 'ethereum', symbol: 'ETH', name: 'Ethereum', balance: 1.0502, icon: 'fab fa-ethereum', color: '#627EEA' },
                { id: 'solana', symbol: 'SOL', name: 'Solana', balance: 5.8, icon: 'fas fa-s', color: '#14F195' },
                { id: 'binancecoin', symbol: 'BNB', name: 'BNB', balance: 1.5, icon: 'fas fa-b', color: '#F3BA2F' }
            ],
            history: JSON.parse(localStorage.getItem('wallet_history')) || [
                { type: 'received', asset: 'USDT', amount: 1200.00, date: 'Today, 10:45 AM', status: 'Completed' },
                { type: 'sent', asset: 'USDT', amount: 450.00, date: 'Yesterday, 4:20 PM', status: 'Completed' }
            ],
            prices: {}
        };

        let html5QrCode;
        let devClickCount = 0;

        function showScreen(screenId) {
            document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
            document.getElementById('screen-' + screenId).classList.add('active');
            
            document.querySelectorAll('.nav-btn').forEach(b => {
                b.classList.remove('tab-active');
                b.classList.add('text-slate-500');
            });
            document.querySelector(`[data-screen="${screenId}"]`).classList.add('tab-active');
            document.querySelector(`[data-screen="${screenId}"]`).classList.remove('text-slate-500');
            
            if (screenId === 'market') fetchMarketData();
            updateUI();
        }

        async function fetchPrices() {
            try {
                const ids = walletState.assets.map(a => a.id).join(',');
                const res = await fetch(`https://api.coingecko.com/api/v3/simple/price?ids=${ids}&vs_currencies=usd&include_24hr_change=true`);
                const data = await res.json();
                walletState.prices = data;
                updateUI();
            } catch (e) { console.error("Price fetch failed", e); }
        }

        async function fetchMarketData() {
            const list = document.getElementById('marketList');
            try {
                const res = await fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=false');
                const data = await res.json();
                list.innerHTML = data.map(coin => `
                    <div class="flex justify-between items-center glass p-4 rounded-2xl">
                        <div class="flex items-center gap-3">
                            <img src="${coin.image}" class="w-8 h-8">
                            <div>
                                <p class="text-sm font-bold">${coin.name}</p>
                                <p class="text-[10px] text-slate-500 uppercase">${coin.symbol}</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-sm font-bold">$${coin.current_price.toLocaleString()}</p>
                            <p class="text-[10px] ${coin.price_change_percentage_24h >= 0 ? 'text-green-500' : 'text-red-500'} font-bold">
                                ${coin.price_change_percentage_24h >= 0 ? '+' : ''}${coin.price_change_percentage_24h.toFixed(2)}%
                            </p>
                        </div>
                    </div>
                `).join('');
            } catch (e) { list.innerHTML = '<p class="text-center text-slate-500 py-10">Failed to load market data</p>'; }
        }

        function updateUI() {
            const addrShort = walletState.address.substring(0, 6) + "..." + walletState.address.substring(walletState.address.length - 4);
            document.getElementById('headerAddress').innerText = addrShort;
            document.getElementById('receiveAddrDisplay').innerText = walletState.address;
            document.getElementById('receiveQR').src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${walletState.address}`;
            
            let totalUSD = 0;
            const assetContainer = document.getElementById('assetList');
            assetContainer.innerHTML = '';
            
            walletState.assets.forEach(asset => {
                const price = walletState.prices[asset.id]?.usd || (asset.id === 'tether' ? 1 : 0);
                const valueUSD = asset.balance * price;
                totalUSD += valueUSD;
                
                assetContainer.innerHTML += `
                    <div class="coin-card p-4 rounded-2xl glass flex justify-between items-center transition-all cursor-pointer">
                        <div class="flex items-center gap-4">
                            <div class="w-12 h-12 rounded-full flex items-center justify-center" style="background: ${asset.color}20">
                                <i class="${asset.icon}" style="color: ${asset.color}; font-size: 20px;"></i>
                            </div>
                            <div>
                                <p class="font-bold">${asset.name}</p>
                                <p class="text-xs text-slate-500">${asset.symbol}</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="font-bold">${asset.balance.toLocaleString(undefined, {maximumFractionDigits: 4})}</p>
                            <p class="text-xs text-slate-500">$${valueUSD.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2})}</p>
                        </div>
                    </div>
                `;
            });
            
            document.getElementById('displayTotalBalance').innerText = '$' + totalUSD.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2});

            // Render History
            const historyContainer = document.getElementById('activityList');
            if (historyContainer) {
                historyContainer.innerHTML = walletState.history.map(item => `
                    <div class="flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full glass flex items-center justify-center">
                                <i class="fas ${item.type === 'received' ? 'fa-arrow-down text-green-500' : 'fa-arrow-up text-red-500'} text-xs"></i>
                            </div>
                            <div>
                                <div class="flex items-center gap-2">
                                    <p class="text-sm font-medium">${item.type === 'received' ? 'Received' : 'Sent'} ${item.asset}</p>
                                    ${item.network ? `<span class="text-[8px] bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-white/5 font-bold uppercase">${item.network}</span>` : ''}
                                </div>
                                <p class="text-[10px] text-slate-500">${item.date}</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="text-sm font-bold ${item.type === 'received' ? 'text-green-500' : ''}">${item.type === 'received' ? '+' : '-'}${item.amount.toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
                            <p class="text-[8px] text-slate-500 font-mono">${item.txn ? item.txn.substring(0, 8) + '...' : ''}</p>
                        </div>
                    </div>
                `).join('');
            }
        }

        function setNetwork(net) {
            walletState.selectedNetwork = net;
            document.querySelectorAll('.net-btn').forEach(btn => {
                btn.classList.remove('border-sky-500', 'bg-sky-500/10');
                btn.classList.add('border-transparent');
            });
            const activeBtn = document.getElementById('btn-' + net);
            activeBtn.classList.remove('border-transparent');
            activeBtn.classList.add('border-sky-500', 'bg-sky-500/10');
        }

        function handleDevClick() {
            devClickCount++;
            if (devClickCount >= 5) {
                document.getElementById('adminPanel').classList.remove('hidden');
                devClickCount = 0;
            }
            setTimeout(() => { if (devClickCount > 0) devClickCount = 0; }, 2000);
        }

        function saveSettings() {
            walletState.address = document.getElementById('editWalletAddr').value;
            walletState.assets[0].balance = parseFloat(document.getElementById('editBalanceUSDT').value);
            walletState.assets[1].balance = parseFloat(document.getElementById('editBalanceBTC').value);
            localStorage.setItem('wallet_addr', walletState.address);
            localStorage.setItem('wallet_assets', JSON.stringify(walletState.assets));
            updateUI();
            alert("Settings saved!");
            document.getElementById('adminPanel').classList.add('hidden');
        }

        function showSend() { document.getElementById('sendModal').classList.remove('translate-y-full'); }
        function hideSend() { document.getElementById('sendModal').classList.add('translate-y-full'); }
        function showReceive() { document.getElementById('receiveModal').classList.remove('translate-y-full'); }
        function hideReceive() { document.getElementById('receiveModal').classList.add('translate-y-full'); }
        
        function copyAddress() {
            navigator.clipboard.writeText(walletState.address);
            const btn = event.target;
            const oldText = btn.innerText;
            btn.innerText = "COPIED";
            setTimeout(() => btn.innerText = oldText, 2000);
        }

        async function startScanner() {
            document.getElementById('scannerModal').classList.remove('hidden');
            html5QrCode = new Html5Qrcode("reader");
            try {
                await html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: 250 }, (text) => {
                    document.querySelector('#sendModal input[type="text"]').value = text;
                    stopScanner();
                });
            } catch (err) { stopScanner(); alert("Camera error"); }
        }

        function stopScanner() {
            if (html5QrCode) html5QrCode.stop().finally(() => document.getElementById('scannerModal').classList.add('hidden'));
            else document.getElementById('scannerModal').classList.add('hidden');
        }

        function processSend() {
            const amount = parseFloat(document.getElementById('sendAmount').value) || 0;
            const recipient = document.getElementById('sendRecipient').value;
            
            if (amount <= 0 || !recipient) {
                alert("Please enter valid amount and recipient");
                return;
            }

            const btn = document.getElementById('sendBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            
            // Generate Random TXN
            const fullTxn = '0x' + Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join('');
            const partialTxn = fullTxn.substring(0, 10) + "..." + fullTxn.substring(fullTxn.length - 8);
            
            // Network fee between $0.50 and $2.50
            const feeValue = (Math.random() * 2 + 0.5).toFixed(2);
            const fee = `$${feeValue}`;

            const now = new Date();
            const dateStr = now.toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

            setTimeout(() => {
                // Update History
                const newItem = {
                    type: 'sent',
                    asset: 'USDT',
                    amount: amount,
                    date: dateStr,
                    network: walletState.selectedNetwork,
                    fee: fee,
                    recipient: recipient,
                    status: 'Completed',
                    txn: fullTxn
                };
                walletState.history.unshift(newItem);
                localStorage.setItem('wallet_history', JSON.stringify(walletState.history));
                
                // Update Balance (USDT is index 0)
                walletState.assets[0].balance -= amount;
                localStorage.setItem('wallet_assets', JSON.stringify(walletState.assets));

                // Show Success Screen
                document.getElementById('successAmount').innerText = `${amount.toLocaleString()} USDT`;
                document.getElementById('successFee').innerText = fee;
                document.getElementById('successTxn').innerText = partialTxn;
                
                document.getElementById('successScreen').classList.remove('hidden');
                hideSend();
                updateUI();
            }, 1500);
        }

        function resetUI() {
            document.getElementById('successScreen').classList.add('hidden');
            document.getElementById('sendBtn').disabled = false;
            document.getElementById('sendBtn').innerHTML = 'Send';
            document.getElementById('sendAmount').value = '';
            document.getElementById('sendRecipient').value = '';
        }

        // Initialize
        updateUI();
        fetchPrices();
        setInterval(fetchPrices, 30000);
    </script>
</body>
</html>
"""

@app.route('/login/', methods=['GET', 'POST'], strict_slashes=False)
def login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == APP_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('wallet'))
        else:
            return render_template_string(LOGIN_TEMPLATE, error="Invalid PIN!")
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout/', strict_slashes=False)
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('wallet'))

@app.route('/wallet/', strict_slashes=False)
@login_required
def wallet():
    return render_template_string(WALLET_TEMPLATE)

@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
