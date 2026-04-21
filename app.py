from flask import Flask, request, jsonify, render_template_string, session, redirect, url_for, send_file
import os
import logging
from functools import wraps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NexusWalletWeb")

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "super-secret-key-nexus-v3")
# Use the PIN requested by the user
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
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="Nexus Wallet">
    <meta name="theme-color" content="#0F172A">
    <link rel="apple-touch-icon" href="/icon.png">
    <link rel="manifest" href="/manifest.json">
    <title>Nexus Wallet - Unlock</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        body { background-color: #0F172A; color: white; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
        .pin-dot { width: 12px; height: 12px; border: 2px solid #334155; border-radius: 50%; transition: all 0.2s; }
        .pin-dot.filled { background-color: #38BDF8; border-color: #38BDF8; box-shadow: 0 0 10px #38BDF8; }
        .key { height: 70px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: 600; border-radius: 50%; transition: all 0.1s; cursor: pointer; }
        .key:active { background-color: #334155; transform: scale(0.9); }
        .shake { animation: shake 0.4s; }
        @keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-10px); } 75% { transform: translateX(10px); } }
    </style>
</head>
<body class="flex flex-col items-center justify-center min-h-screen p-6 select-none">
    <div class="mb-12 text-center">
        <div class="w-20 h-20 rounded-2xl bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20 mx-auto mb-6">
            <i class="fas fa-lock text-3xl"></i>
        </div>
        <h1 class="text-2xl font-bold mb-2">Enter Passcode</h1>
        <p class="text-slate-400 text-sm">Enter your 6-digit PIN to access</p>
    </div>

    <div id="pinContainer" class="flex gap-4 mb-16">
        <div class="pin-dot"></div>
        <div class="pin-dot"></div>
        <div class="pin-dot"></div>
        <div class="pin-dot"></div>
        <div class="pin-dot"></div>
        <div class="pin-dot"></div>
    </div>

    <div class="w-full max-w-[280px] grid grid-cols-3 gap-y-4 gap-x-8 mx-auto">
        <div class="key" onclick="press(1)">1</div>
        <div class="key" onclick="press(2)">2</div>
        <div class="key" onclick="press(3)">3</div>
        <div class="key" onclick="press(4)">4</div>
        <div class="key" onclick="press(5)">5</div>
        <div class="key" onclick="press(6)">6</div>
        <div class="key" onclick="press(7)">7</div>
        <div class="key" onclick="press(8)">8</div>
        <div class="key" onclick="press(9)">9</div>
        <div class="key flex flex-col items-center justify-center">
            <i class="fas fa-fingerprint text-slate-600 text-xl"></i>
        </div>
        <div class="key" onclick="press(0)">0</div>
        <div class="key" onclick="backspace()">
            <i class="fas fa-backspace text-xl"></i>
        </div>
    </div>

    <form id="loginForm" method="POST" class="hidden">
        <input type="hidden" name="password" id="pinInput">
    </form>

    {% if error %}
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const container = document.getElementById('pinContainer');
            container.classList.add('shake');
            setTimeout(() => container.classList.remove('shake'), 400);
        });
    </script>
    {% endif %}

    <script>
        let pin = "";
        const dots = document.querySelectorAll('.pin-dot');

        function press(num) {
            if (pin.length < 6) {
                pin += num;
                updateDots();
                if (pin.length === 6) {
                    submitPin();
                }
            }
        }

        function backspace() {
            if (pin.length > 0) {
                pin = pin.slice(0, -1);
                updateDots();
            }
        }

        function updateDots() {
            dots.forEach((dot, i) => {
                if (i < pin.length) dot.classList.add('filled');
                else dot.classList.remove('filled');
            });
        }

        function submitPin() {
            document.getElementById('pinInput').value = pin;
            document.getElementById('loginForm').submit();
        }

        document.addEventListener('keydown', (e) => {
            if (e.key >= '0' && e.key <= '9') press(e.key);
            if (e.key === 'Backspace') backspace();
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
    <meta name="theme-color" content="#0F172A">
    <link rel="apple-touch-icon" href="/icon.png">
    <title>Nexus Wallet</title>
    <link rel="manifest" href="/manifest.json">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://unpkg.com/html5-qrcode"></script>
    <style>
        body { background-color: #0F172A; color: white; -webkit-tap-highlight-color: transparent; user-select: none; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto; }
        .safe-area-top { padding-top: env(safe-area-inset-top); }
        .safe-area-bottom { padding-bottom: env(safe-area-inset-bottom); }
        .glass { background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .tab-content { display: none; }
        .tab-content.active { display: flex; flex-direction: column; }
        .coin-card { transition: all 0.2s; }
        .coin-card:active { transform: scale(0.96); background: rgba(30, 41, 59, 0.8); }
        .btn-active { color: #38BDF8; }
        ::-webkit-scrollbar { display: none; }
    </style>
</head>
<body class="safe-area-top h-screen flex flex-col overflow-hidden">
    <!-- Header -->
    <div class="px-6 py-4 flex justify-between items-center z-10">
        <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
                <i class="fas fa-wallet text-sm"></i>
            </div>
            <div>
                <p id="headerAddress" class="font-mono text-xs text-sky-400">0x71C7...976F</p>
                <div class="flex items-center gap-1">
                    <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                    <p class="text-[10px] text-slate-400 uppercase tracking-tighter">Mainnet Connected</p>
                </div>
            </div>
        </div>
        <div class="flex gap-3">
            <button class="w-10 h-10 rounded-full glass flex items-center justify-center">
                <i class="fas fa-bell text-slate-400"></i>
            </button>
            <a href="/logout" class="w-10 h-10 rounded-full glass flex items-center justify-center text-red-400">
                <i class="fas fa-power-off"></i>
            </a>
        </div>
    </div>

    <div id="walletTab" class="tab-content active flex-1 overflow-y-auto px-6 pb-32">
        <!-- Balance Card -->
        <div class="mt-4 p-8 rounded-[40px] bg-gradient-to-br from-blue-600 to-indigo-800 shadow-2xl shadow-blue-500/20 relative overflow-hidden min-h-[180px] flex flex-col justify-center">
            <div class="absolute -right-10 -top-10 w-48 h-48 bg-white/10 rounded-full blur-3xl"></div>
            <div class="absolute -left-10 -bottom-10 w-32 h-32 bg-blue-400/10 rounded-full blur-2xl"></div>
            
            <p class="text-blue-100/70 text-xs font-bold uppercase tracking-widest mb-1">Total Balance</p>
            <div class="flex items-baseline gap-2">
                <h2 id="totalBalance" class="text-4xl font-bold text-white tracking-tight">$0.00</h2>
                <i onclick="manualRefresh()" id="refreshIcon" class="fas fa-rotate-right text-blue-200/40 text-xs cursor-pointer hover:text-white transition-all"></i>
            </div>
            
            <div class="flex items-center gap-2 mt-5">
                <div class="flex items-center gap-1 bg-green-500/20 text-green-400 px-2 py-1 rounded-lg text-[10px] font-black">
                    <i class="fas fa-caret-up"></i>
                    <span>5.24%</span>
                </div>
                <span class="text-blue-100/40 text-[10px] font-bold uppercase tracking-tighter">Profit today</span>
            </div>

            <div id="portfolioBar" class="flex h-1.5 w-full bg-white/10 rounded-full mt-6 overflow-hidden">
                <!-- Injected by JS -->
            </div>
        </div>

        <!-- Quick Actions -->
        <div class="grid grid-cols-4 gap-4 mt-8">
            <button onclick="showModal('sendModal')" class="flex flex-col items-center gap-2 group">
                <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center text-blue-400 shadow-lg group-active:scale-90 transition-all border border-white/5">
                    <i class="fas fa-arrow-up-from-bracket text-lg"></i>
                </div>
                <span class="text-[10px] font-black text-slate-500 uppercase tracking-tighter">Send</span>
            </button>
            <button onclick="showModal('receiveModal')" class="flex flex-col items-center gap-2 group">
                <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center text-emerald-400 shadow-lg group-active:scale-90 transition-all border border-white/5">
                    <i class="fas fa-qrcode text-lg"></i>
                </div>
                <span class="text-[10px] font-black text-slate-500 uppercase tracking-tighter">Receive</span>
            </button>
            <button onclick="showModal('swapModal')" class="flex flex-col items-center gap-2 group">
                <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center text-amber-400 shadow-lg group-active:scale-90 transition-all border border-white/5">
                    <i class="fas fa-repeat text-lg"></i>
                </div>
                <span class="text-[10px] font-black text-slate-500 uppercase tracking-tighter">Swap</span>
            </button>
            <button class="flex flex-col items-center gap-2 group opacity-50">
                <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center text-violet-400 shadow-lg border border-white/5">
                    <i class="fas fa-plus text-lg"></i>
                </div>
                <span class="text-[10px] font-black text-slate-500 uppercase tracking-tighter">Buy</span>
            </button>
        </div>

        <!-- Asset List -->
        <div class="mt-10">
            <div class="flex justify-between items-center mb-6">
                <h3 class="text-lg font-black tracking-tight">Your Assets</h3>
                <button class="w-8 h-8 rounded-lg glass flex items-center justify-center text-slate-400">
                    <i class="fas fa-sliders text-xs"></i>
                </button>
            </div>
            <div id="assetContainer" class="space-y-3">
                <!-- Assets injected by JS -->
            </div>
        </div>

        <!-- History -->
        <div class="mt-10 mb-8">
            <h3 class="text-lg font-bold mb-5">Activity</h3>
            <div id="historyContainer" class="space-y-5">
                <!-- History injected by JS -->
            </div>
        </div>
    </div>

    <div id="marketTab" class="tab-content flex-1 overflow-y-auto px-6 pb-24">
        <h2 class="text-2xl font-bold mt-6 mb-6">Market</h2>
        <div class="flex gap-3 mb-6 overflow-x-auto">
            <span class="px-4 py-2 glass rounded-full text-xs font-bold text-sky-400">All</span>
            <span class="px-4 py-2 glass rounded-full text-xs font-bold text-slate-500">Gaining</span>
            <span class="px-4 py-2 glass rounded-full text-xs font-bold text-slate-500">Losing</span>
            <span class="px-4 py-2 glass rounded-full text-xs font-bold text-slate-500">New</span>
        </div>
        <div id="marketList" class="space-y-4">
            <!-- Market coins injected by JS -->
        </div>
    </div>

    <div id="dappsTab" class="tab-content flex-1 overflow-y-auto px-6 pb-32">
        <h2 class="text-2xl font-bold mt-6 mb-6">Explore DApps</h2>
        <div class="glass p-4 rounded-3xl mb-8 flex items-center gap-4">
            <i class="fas fa-search text-slate-500"></i>
            <input type="text" placeholder="Search or enter URL" class="bg-transparent text-sm focus:outline-none w-full">
        </div>

        <div class="mb-8">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-sm font-bold text-slate-400 uppercase tracking-widest">Popular</h3>
                <span class="text-xs text-sky-400">See all</span>
            </div>
            <div class="grid grid-cols-4 gap-4">
                <a href="https://app.uniswap.org" target="_blank" class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center">
                        <img src="https://cryptologos.cc/logos/uniswap-uni-logo.png" class="w-8 h-8 rounded-full">
                    </div>
                    <span class="text-[8px] font-bold">Uniswap</span>
                </a>
                <a href="https://opensea.io" target="_blank" class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center text-blue-400">
                        <i class="fas fa-ship text-xl"></i>
                    </div>
                    <span class="text-[8px] font-bold">OpenSea</span>
                </a>
                <a href="https://pancakeswap.finance" target="_blank" class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center">
                        <img src="https://cryptologos.cc/logos/pancakeswap-cake-logo.png" class="w-8 h-8">
                    </div>
                    <span class="text-[8px] font-bold">Pancake</span>
                </a>
                <a href="https://curve.fi" target="_blank" class="flex flex-col items-center gap-2">
                    <div class="w-14 h-14 rounded-2xl glass flex items-center justify-center">
                        <i class="fas fa-chart-area text-xl text-green-400"></i>
                    </div>
                    <span class="text-[8px] font-bold">Curve</span>
                </a>
            </div>
        </div>

        <div>
            <h3 class="text-sm font-bold text-slate-400 uppercase tracking-widest mb-4">Recommended</h3>
            <div class="space-y-4">
                <div class="p-4 glass rounded-3xl flex items-center gap-4">
                    <div class="w-12 h-12 bg-indigo-500/20 rounded-2xl flex items-center justify-center text-indigo-400">
                        <i class="fas fa-link text-xl"></i>
                    </div>
                    <div>
                        <p class="font-bold text-sm">Lido Staking</p>
                        <p class="text-[10px] text-slate-500">Stake ETH and receive stETH</p>
                    </div>
                </div>
                <div class="p-4 glass rounded-3xl flex items-center gap-4">
                    <div class="w-12 h-12 bg-blue-500/20 rounded-2xl flex items-center justify-center text-blue-400">
                        <i class="fas fa-building-columns text-xl"></i>
                    </div>
                    <div>
                        <p class="font-bold text-sm">Aave V3</p>
                        <p class="text-[10px] text-slate-500">Liquidity protocol for earning interest</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div id="settingsTab" class="tab-content flex-1 overflow-y-auto px-6 pb-24">
        <h2 class="text-2xl font-bold mt-6 mb-8">Settings</h2>
        
        <div class="space-y-2">
            <div class="p-4 glass rounded-3xl flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-sky-500/20 rounded-xl flex items-center justify-center">
                        <i class="fas fa-shield-halved text-sky-400"></i>
                    </div>
                    <span class="font-medium">Security</span>
                </div>
                <i class="fas fa-chevron-right text-slate-600"></i>
            </div>
            <div class="p-4 glass rounded-3xl flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-purple-500/20 rounded-xl flex items-center justify-center">
                        <i class="fas fa-bell text-purple-400"></i>
                    </div>
                    <span class="font-medium">Notifications</span>
                </div>
                <i class="fas fa-chevron-right text-slate-600"></i>
            </div>
            <div class="p-4 glass rounded-3xl flex items-center justify-between">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-orange-500/20 rounded-xl flex items-center justify-center">
                        <i class="fas fa-wallet text-orange-400"></i>
                    </div>
                    <span class="font-medium">Wallet Connect</span>
                </div>
                <i class="fas fa-chevron-right text-slate-600"></i>
            </div>
            <div onclick="handleDevClick()" class="p-4 glass rounded-3xl flex items-center justify-between cursor-pointer">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 bg-slate-700/50 rounded-xl flex items-center justify-center">
                        <i class="fas fa-circle-info text-slate-400"></i>
                    </div>
                    <span class="font-medium">About</span>
                </div>
                <span class="text-xs text-slate-600">v2.6.0</span>
            </div>
        </div>

        <div id="devConsole" class="hidden mt-8 p-6 glass rounded-[32px] border-sky-500/30">
            <h3 class="text-sky-400 font-bold mb-4 flex items-center gap-2">
                <i class="fas fa-terminal"></i> Console
            </h3>
            <div class="space-y-4">
                <div>
                    <label class="text-[10px] text-slate-500 uppercase font-bold">Wallet Address</label>
                    <input type="text" id="editAddr" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-xs mt-1">
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="text-[10px] text-slate-500 uppercase font-bold">USDT Bal</label>
                        <input type="number" step="any" id="editUsdt" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-xs mt-1">
                    </div>
                    <div>
                        <label class="text-[10px] text-slate-500 uppercase font-bold">BTC Bal</label>
                        <input type="number" step="any" id="editBtc" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-xs mt-1">
                    </div>
                </div>
                <div class="grid grid-cols-3 gap-2">
                    <div>
                        <label class="text-[10px] text-slate-500 uppercase font-bold text-[8px]">ETH</label>
                        <input type="number" step="any" id="editEth" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-xs mt-1">
                    </div>
                    <div>
                        <label class="text-[10px] text-slate-500 uppercase font-bold text-[8px]">SOL</label>
                        <input type="number" step="any" id="editSol" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-xs mt-1">
                    </div>
                    <div>
                        <label class="text-[10px] text-slate-500 uppercase font-bold text-[8px]">BNB</label>
                        <input type="number" step="any" id="editBnb" class="w-full bg-slate-900/50 border border-slate-700 rounded-xl p-3 text-xs mt-1">
                    </div>
                </div>
                <button onclick="saveDevChanges()" class="w-full bg-sky-500 py-3 rounded-xl font-bold text-xs">Apply Changes</button>
            </div>
        </div>

        <button onclick="window.location.href='/logout'" class="w-full mt-8 p-4 text-red-400 font-bold">Sign Out</button>
    </div>

    <!-- Bottom Nav -->
    <div class="fixed bottom-0 left-0 right-0 glass h-20 px-8 flex justify-between items-center rounded-t-[32px] safe-area-bottom z-20">
        <button onclick="switchTab('wallet')" class="nav-btn btn-active flex flex-col items-center gap-1">
            <i class="fas fa-wallet text-xl"></i>
            <span class="text-[10px] font-bold">Wallet</span>
        </button>
        <button onclick="switchTab('market')" class="nav-btn text-slate-500 flex flex-col items-center gap-1">
            <i class="fas fa-chart-line text-xl"></i>
            <span class="text-[10px] font-bold">Market</span>
        </button>
        <button onclick="switchTab('dapps')" class="nav-btn text-slate-500 flex flex-col items-center gap-1">
            <i class="fas fa-compass text-xl"></i>
            <span class="text-[10px] font-bold">DApps</span>
        </button>
        <button onclick="switchTab('settings')" class="nav-btn text-slate-500 flex flex-col items-center gap-1">
            <i class="fas fa-gear text-xl"></i>
            <span class="text-[10px] font-bold">Settings</span>
        </button>
    </div>

    <!-- Send Modal -->
    <div id="sendModal" class="fixed inset-0 z-50 translate-y-full transition-transform duration-300 ease-out flex flex-col">
        <div class="flex-1 bg-black/60 backdrop-blur-sm" onclick="hideModal('sendModal')"></div>
        <div class="glass rounded-t-[40px] px-6 pt-8 pb-12 flex flex-col gap-6">
            <div class="w-12 h-1 bg-slate-700 rounded-full mx-auto -mt-4 mb-2"></div>
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold">Send USDT</h2>
                <button onclick="hideModal('sendModal')" class="text-slate-400">Cancel</button>
            </div>
            <div id="assetSelector" class="relative">
                <label class="text-[10px] text-slate-500 uppercase font-bold mb-3 block">Asset</label>
                <button onclick="toggleAssetDropdown()" id="selectedAssetBtn" class="w-full glass rounded-2xl py-4 px-5 flex items-center justify-between border border-white/5">
                    <div class="flex items-center gap-3">
                        <div id="selectedAssetIcon" class="w-8 h-8 rounded-xl bg-sky-500/10 flex items-center justify-center">
                            <i class="fab fa-ethereum text-sky-400"></i>
                        </div>
                        <div class="text-left">
                            <p id="selectedAssetName" class="text-sm font-bold">Tether</p>
                            <p id="selectedAssetSym" class="text-[10px] text-slate-500 font-bold tracking-widest uppercase">USDT</p>
                        </div>
                    </div>
                    <i class="fas fa-chevron-down text-slate-600 text-xs"></i>
                </button>
                <div id="assetDropdown" class="hidden absolute top-full left-0 right-0 mt-2 glass rounded-2xl border border-white/5 overflow-hidden z-[60] shadow-2xl">
                    <!-- Dropdown items injected by JS -->
                </div>
            </div>
            <div>
                <label class="text-[10px] text-slate-500 uppercase font-bold mb-3 block">Network</label>
                <div id="networkGrid" class="grid grid-cols-3 gap-2">
                    <!-- Network buttons injected by JS -->
                </div>
            </div>
            <div class="relative">
                <label class="text-[10px] text-slate-500 uppercase font-bold mb-2 block">Recipient Address</label>
                <input type="text" id="sendAddr" placeholder="0x... or ENS" class="w-full glass rounded-2xl py-4 px-5 pr-12 text-sm focus:outline-none border border-white/5">
                <i onclick="startScanner()" class="fas fa-qrcode absolute right-5 bottom-4 text-sky-400 text-lg cursor-pointer"></i>
            </div>
            <div>
                <label class="text-[10px] text-slate-500 uppercase font-bold mb-2 block">Amount</label>
                <div class="relative">
                    <input type="number" id="sendAmount" placeholder="0.00" class="w-full glass rounded-2xl py-4 px-5 pr-20 text-2xl font-bold focus:outline-none border border-white/5">
                    <span onclick="setMax()" class="absolute right-4 top-1/2 -translate-y-1/2 text-sky-400 font-bold text-xs bg-sky-500/10 px-3 py-1 rounded-lg cursor-pointer">MAX</span>
                </div>
                <p id="sendBalanceText" class="text-[10px] text-slate-500 mt-2 px-1">Available: 0.00 USDT</p>
            </div>
            <button id="confirmSendBtn" onclick="executeSend()" class="w-full bg-sky-500 py-4 rounded-2xl font-bold shadow-lg shadow-sky-500/20 active:scale-95 transition-all mt-2">
                Send Now
            </button>
        </div>
    </div>

    <!-- Swap Modal -->
    <div id="swapModal" class="fixed inset-0 z-50 translate-y-full transition-transform duration-300 ease-out flex flex-col">
        <div class="flex-1 bg-black/60 backdrop-blur-sm" onclick="hideModal('swapModal')"></div>
        <div class="glass rounded-t-[40px] px-6 pt-8 pb-12 flex flex-col gap-6">
            <div class="w-12 h-1 bg-slate-700 rounded-full mx-auto -mt-4 mb-2"></div>
            <div class="flex justify-between items-center">
                <h2 class="text-2xl font-bold">Swap</h2>
                <button onclick="hideModal('swapModal')" class="text-slate-400">Cancel</button>
            </div>
            
            <div class="space-y-2">
                <div class="glass rounded-2xl p-5 border border-white/5">
                    <div class="flex justify-between mb-2">
                        <span class="text-[10px] text-slate-500 font-bold uppercase">Sell</span>
                        <span id="swapFromBal" class="text-[10px] text-slate-500 font-bold">Balance: 0.00</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <div onclick="openSwapAssetList('from')" class="flex items-center gap-3 bg-white/5 px-3 py-2 rounded-xl cursor-pointer">
                            <div id="swapFromIcon" class="w-6 h-6 rounded-lg bg-sky-500/10 flex items-center justify-center">
                                <i class="fab fa-ethereum text-sky-400 text-xs"></i>
                            </div>
                            <span id="swapFromSym" class="font-bold text-sm">USDT</span>
                            <i class="fas fa-chevron-down text-[8px] text-slate-600"></i>
                        </div>
                        <input type="number" id="swapAmount" oninput="calculateSwap()" placeholder="0.00" class="bg-transparent text-right text-2xl font-bold focus:outline-none w-1/2">
                    </div>
                </div>

                <div class="flex justify-center -my-3 relative z-10">
                    <button onclick="flipSwap()" class="w-10 h-10 bg-slate-800 rounded-xl border border-white/10 flex items-center justify-center text-sky-400 shadow-xl">
                        <i class="fas fa-arrow-down"></i>
                    </button>
                </div>

                <div class="glass rounded-2xl p-5 border border-white/5">
                    <div class="flex justify-between mb-2">
                        <span class="text-[10px] text-slate-500 font-bold uppercase">Buy</span>
                        <span id="swapToBal" class="text-[10px] text-slate-500 font-bold">Balance: 0.00</span>
                    </div>
                    <div class="flex justify-between items-center">
                        <div onclick="openSwapAssetList('to')" class="flex items-center gap-3 bg-white/5 px-3 py-2 rounded-xl cursor-pointer">
                            <div id="swapToIcon" class="w-6 h-6 rounded-lg bg-purple-500/10 flex items-center justify-center">
                                <i class="fab fa-ethereum text-purple-400 text-xs"></i>
                            </div>
                            <span id="swapToSym" class="font-bold text-sm">ETH</span>
                            <i class="fas fa-chevron-down text-[8px] text-slate-600"></i>
                        </div>
                        <div id="swapResult" class="text-2xl font-bold text-slate-500">0.00</div>
                    </div>
                </div>
            </div>

            <div class="px-2 space-y-2">
                <div class="flex justify-between text-[10px] font-bold">
                    <span class="text-slate-500">Estimated Gas Fee</span>
                    <span id="swapFee" class="text-slate-300">0.00 USDT</span>
                </div>
                <div class="flex justify-between text-[10px] font-bold">
                    <span class="text-slate-500">Price Impact</span>
                    <span class="text-green-400">< 0.01%</span>
                </div>
            </div>

            <button id="confirmSwapBtn" onclick="executeSwap()" class="w-full bg-amber-500 py-4 rounded-2xl font-bold shadow-lg shadow-amber-500/20 active:scale-95 transition-all">
                Swap Now
            </button>
        </div>
    </div>

    <!-- TX Details Modal -->
    <div id="txDetailsModal" class="fixed inset-0 z-50 translate-y-full transition-transform duration-300 ease-out flex flex-col">
        <div class="flex-1 bg-black/60 backdrop-blur-sm" onclick="hideModal('txDetailsModal')"></div>
        <div class="glass rounded-t-[40px] px-8 pt-8 pb-12">
            <div class="w-12 h-1 bg-slate-700 rounded-full mx-auto -mt-4 mb-6"></div>
            <div class="text-center mb-8">
                <div id="detIcon" class="w-16 h-16 rounded-full mx-auto flex items-center justify-center mb-4 text-2xl">
                    <i class="fas fa-arrow-up"></i>
                </div>
                <h2 id="detType" class="text-xl font-bold">Transaction Details</h2>
                <p id="detDate" class="text-slate-500 text-xs">April 22, 2026 at 6:15 AM</p>
            </div>

            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <span class="text-xs text-slate-500 font-bold uppercase">Status</span>
                    <span class="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-[10px] font-black uppercase">Confirmed</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-slate-500 font-bold uppercase">Amount</span>
                    <span id="detAmount" class="font-bold">0.00 USDT</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-slate-500 font-bold uppercase">Network</span>
                    <span id="detNet" class="font-bold text-slate-300">Ethereum</span>
                </div>
                <div class="flex justify-between items-center">
                    <span class="text-xs text-slate-500 font-bold uppercase">Network Fee</span>
                    <span id="detFee" class="text-slate-300 font-bold">$1.24</span>
                </div>
                <div class="pt-4 border-t border-white/5">
                    <p class="text-[10px] text-slate-500 font-bold uppercase mb-2">Transaction Hash</p>
                    <div class="glass rounded-xl p-3 flex justify-between items-center">
                        <p id="detHash" class="text-[10px] font-mono text-sky-400 truncate mr-4">0x...</p>
                        <i onclick="copyText(document.getElementById('detHash').innerText)" class="fas fa-copy text-sky-400 cursor-pointer"></i>
                    </div>
                </div>
            </div>
            <button onclick="hideModal('txDetailsModal')" class="w-full mt-10 py-4 glass rounded-2xl font-bold text-slate-400">Close</button>
        </div>
    </div>

    <!-- Success Screen -->
    <div id="successScreen" class="fixed inset-0 z-[60] bg-[#0F172A] hidden flex flex-col items-center justify-center p-8 text-center">
        <div class="w-24 h-24 bg-green-500 rounded-full flex items-center justify-center mb-8 shadow-2xl shadow-green-500/40 animate-bounce">
            <i class="fas fa-check text-4xl"></i>
        </div>
        <h2 id="successTitle" class="text-3xl font-bold mb-3">Success</h2>
        <p class="text-slate-400 text-sm mb-12 px-6">Your transaction has been broadcasted to the network.</p>
        
        <div class="w-full glass rounded-[32px] p-6 mb-12 space-y-4">
            <div class="flex justify-between text-xs">
                <span class="text-slate-500 uppercase font-bold">Amount</span>
                <span id="resAmount" class="font-bold">0.00 USDT</span>
            </div>
            <div class="flex justify-between text-xs">
                <span class="text-slate-500 uppercase font-bold">Network Fee</span>
                <span id="resFee" class="text-slate-300">$1.24</span>
            </div>
            <div class="flex justify-between text-xs overflow-hidden">
                <span class="text-slate-500 uppercase font-bold shrink-0">TXN Hash</span>
                <span id="resHash" class="text-sky-400 truncate ml-8 font-mono italic">0x...</span>
            </div>
        </div>
        <button onclick="hideSuccess()" class="w-full py-5 glass rounded-2xl font-bold text-sky-400">Back to Wallet</button>
    </div>

    <!-- Receive Modal -->
    <div id="receiveModal" class="fixed inset-0 z-50 translate-y-full transition-transform duration-300 ease-out flex flex-col">
        <div class="flex-1 bg-black/60 backdrop-blur-sm" onclick="hideModal('receiveModal')"></div>
        <div class="glass rounded-t-[40px] px-6 pt-8 pb-12 flex flex-col items-center gap-8">
            <div class="w-12 h-1 bg-slate-700 rounded-full -mt-4 mb-2"></div>
            <div class="w-full flex justify-between items-center">
                <h2 class="text-2xl font-bold">Receive</h2>
                <button onclick="hideModal('receiveModal')" class="text-slate-400">Close</button>
            </div>
            <div class="bg-white p-5 rounded-[40px] shadow-2xl shadow-white/5">
                <img id="qrCode" src="" alt="QR" class="w-48 h-48">
            </div>
            <div class="w-full space-y-3">
                <p class="text-[10px] text-slate-500 text-center uppercase font-bold tracking-widest">Your Public Address (ERC-20)</p>
                <div class="glass rounded-2xl p-5 flex justify-between items-center">
                    <p id="fullAddr" class="text-[10px] font-mono text-sky-400 truncate mr-4">0x71C7656EC7ab88b098defB751B7401B5f6d8976F</p>
                    <button onclick="copyAddr()" class="text-[10px] font-bold text-sky-400 bg-sky-500/10 px-4 py-2 rounded-xl">Copy</button>
                </div>
            </div>
            <p class="text-[10px] text-slate-500 text-center px-10 italic">
                Only send USDT to this address on the Ethereum (ERC-20) network.
            </p>
        </div>
    </div>

    <!-- Scanner -->
    <div id="scannerModal" class="fixed inset-0 z-[70] bg-black hidden flex flex-col">
        <div class="p-8 flex justify-between items-center">
            <h2 class="text-xl font-bold">Scan QR</h2>
            <button onclick="stopScanner()" class="w-12 h-12 rounded-full glass flex items-center justify-center">
                <i class="fas fa-times"></i>
            </button>
        </div>
        <div id="reader" class="flex-1"></div>
    </div>

    <script>
        const APP_VERSION = "2.6.0";
        if (localStorage.getItem('app_version') !== APP_VERSION) {
            localStorage.removeItem('wallet_assets');
            localStorage.removeItem('wallet_history');
            localStorage.setItem('app_version', APP_VERSION);
        }

        let walletState = {
            address: localStorage.getItem('wallet_addr') || "0x71C7656EC7ab88b098defB751B7401B5f6d8976F",
            assets: JSON.parse(localStorage.getItem('wallet_assets')) || [
                { name: 'Tether', sym: 'USDT', balance: 5120.00, icon: 'fab fa-ethereum', color: '#26A17B' },
                { name: 'Bitcoin', sym: 'BTC', balance: 0.015, icon: 'fab fa-bitcoin', color: '#F7931A' },
                { name: 'Ethereum', sym: 'ETH', balance: 0.25, icon: 'fab fa-ethereum', color: '#627EEA' },
                { name: 'Solana', sym: 'SOL', balance: 1.8, icon: 'fas fa-s', color: '#14F195' },
                { name: 'Binance', sym: 'BNB', balance: 0.2, icon: 'fas fa-b', color: '#F3BA2F' }
            ],
            history: JSON.parse(localStorage.getItem('wallet_history')) || [
                { type: 'Received', sym: 'USDT', amount: 500.00, date: 'Today, 10:45 AM', status: 'Confirmed', net: 'ERC-20' },
                { type: 'Sent', sym: 'USDT', amount: 120.00, date: 'Yesterday, 4:20 PM', status: 'Confirmed', net: 'TRC-20' }
            ],
            prices: { USDT: 1, BTC: 64500, ETH: 3450, SOL: 145, BNB: 580 }
        };

        let selectedAssetIdx = 0;
        let devClicks = 0;
        let html5QrCode;

        function updateUI() {
            try {
                // Header
                const shortAddr = walletState.address.slice(0, 6) + "..." + walletState.address.slice(-4);
                const headerAddr = document.getElementById('headerAddress');
                const fullAddr = document.getElementById('fullAddr');
                const qrCode = document.getElementById('qrCode');
                
                if (headerAddr) headerAddr.innerText = shortAddr;
                if (fullAddr) fullAddr.innerText = walletState.address;
                if (qrCode) qrCode.src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${walletState.address}`;
                
                // Assets & Balance
                let total = 0;
                const container = document.getElementById('assetContainer');
                if (container) {
                    container.innerHTML = '';
                    walletState.assets.forEach(asset => {
                        const price = walletState.prices[asset.sym] || 0;
                        const val = asset.balance * price;
                        total += val;
                        
                        container.innerHTML += `
                            <div class="coin-card p-5 rounded-[32px] glass flex justify-between items-center" onclick="openSendWithAsset('${asset.sym}')">
                                <div class="flex items-center gap-4">
                                    <div class="w-12 h-12 rounded-2xl flex items-center justify-center" style="background: ${asset.color}15">
                                        <i class="${asset.icon}" style="color: ${asset.color}"></i>
                                    </div>
                                    <div>
                                        <p class="font-bold text-sm text-white">${asset.name}</p>
                                        <p class="text-[10px] text-slate-500 font-black uppercase tracking-widest">${asset.sym}</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="font-bold text-sm text-white">${asset.balance.toLocaleString(undefined, {minimumFractionDigits: asset.sym === 'USDT' ? 2 : 4})}</p>
                                    <p class="text-[10px] text-slate-500 font-bold tracking-tight">$${val.toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
                                </div>
                            </div>
                        `;
                    });
                }

                const totalEl = document.getElementById('totalBalance');
                if (totalEl) {
                    totalEl.innerText = `$${total.toLocaleString(undefined, {minimumFractionDigits: 2})}`;
                }

                // Update Portfolio Bar
                const portfolioBar = document.getElementById('portfolioBar');
                if (portfolioBar) {
                    portfolioBar.innerHTML = '';
                    walletState.assets.forEach(asset => {
                        const price = walletState.prices[asset.sym] || 0;
                        const val = asset.balance * price;
                        const pct = total > 0 ? (val / total) * 100 : 0;
                        if (pct > 1) {
                            portfolioBar.innerHTML += `<div style="width: ${pct}%; background: ${asset.color}; height: 100%"></div>`;
                        }
                    });
                }
                
                // Update Send Modal State
                updateSendModalUI();
                updateSwapUI();
                
                // History
                const histContainer = document.getElementById('historyContainer');
                if (histContainer) {
                    histContainer.innerHTML = '';
                    walletState.history.slice().reverse().forEach((h, i) => {
                        const originalIdx = walletState.history.length - 1 - i;
                        const isSent = h.type === 'Sent' || h.type === 'Swap';
                        const asset = walletState.assets.find(a => a.sym === h.sym) || { icon: 'fas fa-coins', color: '#94A3B8' };
                        
                        histContainer.innerHTML += `
                            <div class="flex items-center justify-between py-1 cursor-pointer active:opacity-50 transition-opacity" onclick="showTxDetails(${originalIdx})">
                                <div class="flex items-center gap-4">
                                    <div class="w-10 h-10 rounded-full glass flex items-center justify-center border border-white/5 relative">
                                        <i class="${asset.icon}" style="color: ${asset.color}; font-size: 10px;"></i>
                                        <div class="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-slate-900 flex items-center justify-center border border-white/10">
                                            <i class="fas ${h.type === 'Received' ? 'fa-arrow-down text-emerald-400' : (h.type === 'Swap' ? 'fa-repeat text-amber-400' : 'fa-arrow-up text-red-400')} text-[6px]"></i>
                                        </div>
                                    </div>
                                    <div>
                                        <p class="text-xs font-bold text-white">${h.type} ${h.sym}</p>
                                        <p class="text-[10px] text-slate-500 font-medium">${h.date} • ${h.net || 'Network'}</p>
                                    </div>
                                </div>
                                <div class="text-right">
                                    <p class="text-xs font-black ${h.type === 'Received' ? 'text-emerald-400' : 'text-white'}">${h.type === 'Received' ? '+' : '-'}${h.amount.toLocaleString(undefined, {minimumFractionDigits: h.sym === 'USDT' ? 2 : 4})} ${h.sym}</p>
                                    <p class="text-[8px] text-slate-600 font-bold">$${(h.amount * (walletState.prices[h.sym] || 1)).toLocaleString(undefined, {minimumFractionDigits: 2})}</p>
                                </div>
                            </div>
                        `;
                    });
                }

                localStorage.setItem('wallet_assets', JSON.stringify(walletState.assets));
                localStorage.setItem('wallet_history', JSON.stringify(walletState.history));
                localStorage.setItem('wallet_addr', walletState.address);
            } catch (err) {
                console.error("UI Update Error:", err);
            }
        }

        let swapState = { fromIdx: 0, toIdx: 2 }; 

        function updateSwapUI() {
            const from = walletState.assets[swapState.fromIdx];
            const to = walletState.assets[swapState.toIdx];
            
            document.getElementById('swapFromIcon').innerHTML = `<i class="${from.icon}" style="color: ${from.color}"></i>`;
            document.getElementById('swapFromSym').innerText = from.sym;
            document.getElementById('swapFromBal').innerText = `Balance: ${from.balance.toLocaleString(undefined, {maximumFractionDigits: 4})}`;
            
            document.getElementById('swapToIcon').innerHTML = `<i class="${to.icon}" style="color: ${to.color}"></i>`;
            document.getElementById('swapToSym').innerText = to.sym;
            document.getElementById('swapToBal').innerText = `Balance: ${to.balance.toLocaleString(undefined, {maximumFractionDigits: 4})}`;
            
            calculateSwap();
        }

        function calculateSwap() {
            const from = walletState.assets[swapState.fromIdx];
            const to = walletState.assets[swapState.toIdx];
            const amt = parseFloat(document.getElementById('swapAmount').value) || 0;
            
            const res = (amt * (walletState.prices[from.sym] || 0)) / (walletState.prices[to.sym] || 1);
            document.getElementById('swapResult').innerText = res.toLocaleString(undefined, {maximumFractionDigits: 6});
            
            const fee = (amt * 0.003).toLocaleString(undefined, {maximumFractionDigits: 4});
            document.getElementById('swapFee').innerText = `${fee} ${from.sym}`;
        }

        function flipSwap() {
            const tmp = swapState.fromIdx;
            swapState.fromIdx = swapState.toIdx;
            swapState.toIdx = tmp;
            updateSwapUI();
        }

        function executeSwap() {
            const from = walletState.assets[swapState.fromIdx];
            const to = walletState.assets[swapState.toIdx];
            const amt = parseFloat(document.getElementById('swapAmount').value);
            
            if (!amt || amt <= 0) return alert("Enter amount");
            if (amt > from.balance) return alert("Insufficient balance");

            const btn = document.getElementById('confirmSwapBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> swapping...';

            setTimeout(() => {
                const resAmt = (amt * walletState.prices[from.sym]) / walletState.prices[to.sym];
                from.balance -= amt;
                to.balance += resAmt;

                const hash = '0x' + Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join('');
                walletState.history.push({
                    type: 'Swap',
                    sym: from.sym,
                    amount: amt,
                    date: 'Just now',
                    status: 'Confirmed',
                    net: 'Nexus DEX',
                    hash: hash,
                    toSym: to.sym,
                    toAmount: resAmt
                });

                updateUI();
                hideModal('swapModal');
                
                document.getElementById('resAmount').innerText = `${amt.toLocaleString()} ${from.sym} → ${resAmt.toLocaleString()} ${to.sym}`;
                document.getElementById('resFee').innerText = "$0.00 (Gasless)";
                document.getElementById('resHash').innerText = hash.slice(0, 10) + "..." + hash.slice(-8);
                document.getElementById('successTitle').innerText = "Swap Successful";
                document.getElementById('successScreen').classList.remove('hidden');

                btn.disabled = false;
                btn.innerHTML = 'Swap Now';
                document.getElementById('swapAmount').value = '';
            }, 1500);
        }

        function showTxDetails(idx) {
            const tx = walletState.history[idx];
            const asset = walletState.assets.find(a => a.sym === tx.sym) || { icon: 'fas fa-coins', color: '#94A3B8' };
            
            document.getElementById('detIcon').style.background = asset.color + '20';
            document.getElementById('detIcon').style.color = asset.color;
            document.getElementById('detIcon').innerHTML = `<i class="${tx.type === 'Received' ? 'fas fa-arrow-down' : (tx.type === 'Swap' ? 'fas fa-repeat' : 'fas fa-arrow-up')}"></i>`;
            
            document.getElementById('detType').innerText = tx.type + " " + tx.sym;
            document.getElementById('detDate').innerText = tx.date;
            document.getElementById('detAmount').innerText = (tx.type === 'Received' ? '+' : '-') + tx.amount.toLocaleString() + " " + tx.sym;
            document.getElementById('detNet').innerText = tx.net || 'Mainnet';
            document.getElementById('detFee').innerText = tx.fee ? "$" + tx.fee : "Gasless";
            document.getElementById('detHash').innerText = tx.hash || '0x' + '0'.repeat(64);
            
            showModal('txDetailsModal');
        }

        function copyText(text) {
            navigator.clipboard.writeText(text);
            alert("Copied!");
        }

        function openSwapAssetList(side) {
            // Simplified: just flip for now or rotate
            if (side === 'from') swapState.fromIdx = (swapState.fromIdx + 1) % walletState.assets.length;
            else swapState.toIdx = (swapState.toIdx + 1) % walletState.assets.length;
            if (swapState.fromIdx === swapState.toIdx) swapState.toIdx = (swapState.toIdx + 1) % walletState.assets.length;
            updateSwapUI();
        }

        function updateSendModalUI() {
            const asset = walletState.assets[selectedAssetIdx];
            document.getElementById('selectedAssetName').innerText = asset.name;
            document.getElementById('selectedAssetSym').innerText = asset.sym;
            document.getElementById('selectedAssetIcon').innerHTML = `<i class="${asset.icon}" style="color: ${asset.color}"></i>`;
            document.getElementById('selectedAssetIcon').style.background = asset.color + '15';
            document.getElementById('sendBalanceText').innerText = `Available: ${asset.balance.toLocaleString(undefined, {minimumFractionDigits: asset.sym === 'USDT' ? 2 : 4})} ${asset.sym}`;
            
            // Network selection based on asset
            const netGrid = document.getElementById('networkGrid');
            let networks = [];
            if (asset.sym === 'USDT') networks = ['ERC-20', 'TRC-20', 'BEP-20'];
            else if (asset.sym === 'BTC') networks = ['Bitcoin'];
            else if (asset.sym === 'ETH') networks = ['Ethereum'];
            else if (asset.sym === 'SOL') networks = ['Solana'];
            else if (asset.sym === 'BNB') networks = ['BSC'];

            netGrid.innerHTML = '';
            networks.forEach((net, i) => {
                const isActive = i === 0;
                netGrid.innerHTML += `
                    <button onclick="selectNetwork(this)" class="network-btn py-3 glass rounded-2xl border ${isActive ? 'border-sky-500 bg-sky-500/10' : 'border-transparent'} text-[10px] font-bold">
                        ${net}
                    </button>
                `;
            });

            // Populate Dropdown
            const dropdown = document.getElementById('assetDropdown');
            dropdown.innerHTML = '';
            walletState.assets.forEach((a, idx) => {
                dropdown.innerHTML += `
                    <div onclick="selectAsset(${idx})" class="p-4 hover:bg-white/5 flex items-center justify-between cursor-pointer border-b border-white/5 last:border-0">
                        <div class="flex items-center gap-3">
                            <i class="${a.icon}" style="color: ${a.color}"></i>
                            <div>
                                <p class="text-sm font-bold">${a.name}</p>
                                <p class="text-[10px] text-slate-500 uppercase">${a.sym}</p>
                            </div>
                        </div>
                        <p class="text-xs font-bold">${a.balance.toLocaleString(undefined, {maximumFractionDigits: 4})}</p>
                    </div>
                `;
            });
        }

        function toggleAssetDropdown() {
            document.getElementById('assetDropdown').classList.toggle('hidden');
        }

        function selectAsset(idx) {
            selectedAssetIdx = idx;
            updateSendModalUI();
            toggleAssetDropdown();
        }

        function selectNetwork(btn) {
            document.querySelectorAll('.network-btn').forEach(b => {
                b.classList.remove('border-sky-500', 'bg-sky-500/10');
                b.classList.add('border-transparent');
            });
            btn.classList.add('border-sky-500', 'bg-sky-500/10');
            btn.classList.remove('border-transparent');
        }

        function openSendWithAsset(sym) {
            const idx = walletState.assets.findIndex(a => a.sym === sym);
            if (idx !== -1) {
                selectedAssetIdx = idx;
                updateSendModalUI();
                showModal('sendModal');
            }
        }

        function manualRefresh() {
            const icon = document.getElementById('refreshIcon');
            icon.classList.add('fa-spin');
            fetchPrices().finally(() => {
                setTimeout(() => icon.classList.remove('fa-spin'), 1000);
            });
        }

        async function fetchPrices() {
            try {
                const res = await fetch('https://api.coingecko.com/api/v2/simple/price?ids=bitcoin,ethereum,tether,solana,binancecoin&vs_currencies=usd');
                const data = await res.json();
                walletState.prices = {
                    USDT: data.tether.usd,
                    BTC: data.bitcoin.usd,
                    ETH: data.ethereum.usd,
                    SOL: data.solana.usd,
                    BNB: data.binancecoin.usd
                };
                updateUI();
                updateMarket(data);
            } catch (e) {
                console.error("Price fetch failed", e);
            }
        }

        function updateMarket(data) {
            const list = document.getElementById('marketList');
            list.innerHTML = '';
            const coins = [
                { id: 'bitcoin', sym: 'BTC', name: 'Bitcoin' },
                { id: 'ethereum', sym: 'ETH', name: 'Ethereum' },
                { id: 'tether', sym: 'USDT', name: 'Tether' },
                { id: 'solana', sym: 'SOL', name: 'Solana' },
                { id: 'binancecoin', sym: 'BNB', name: 'BNB' }
            ];

            coins.forEach(c => {
                const p = data[c.id].usd;
                list.innerHTML += `
                    <a href="https://www.coingecko.com/en/coins/${c.id}" target="_blank" class="p-5 glass rounded-3xl flex items-center justify-between">
                        <div class="flex items-center gap-4">
                            <div class="w-10 h-10 rounded-full bg-slate-800 flex items-center justify-center font-bold text-xs">
                                ${c.sym}
                            </div>
                            <div>
                                <p class="font-bold text-sm">${c.name}</p>
                                <p class="text-[10px] text-slate-500 font-bold uppercase">${c.sym}/USD</p>
                            </div>
                        </div>
                        <div class="text-right">
                            <p class="font-bold text-sm">$${p.toLocaleString()}</p>
                            <p class="text-[10px] text-green-400 font-bold">+2.4%</p>
                        </div>
                    </a>
                `;
            });
        }

        function switchTab(tabId) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('btn-active'));
            document.querySelectorAll('.nav-btn').forEach(b => b.classList.add('text-slate-500'));
            
            document.getElementById(tabId + 'Tab').classList.add('active');
            event.currentTarget.classList.add('btn-active');
            event.currentTarget.classList.remove('text-slate-500');
        }

        function showModal(id) {
            document.getElementById(id).classList.remove('translate-y-full');
        }

        function hideModal(id) {
            document.getElementById(id).classList.add('translate-y-full');
        }

        function setMax() {
            document.getElementById('sendAmount').value = walletState.assets[selectedAssetIdx].balance;
        }

        function executeSend() {
            const asset = walletState.assets[selectedAssetIdx];
            const amt = parseFloat(document.getElementById('sendAmount').value);
            const addr = document.getElementById('sendAddr').value;
            if (!amt || !addr) return alert("Fill all fields");
            if (amt > asset.balance) return alert("Insufficient balance");

            const netBtn = document.querySelector('.network-btn.border-sky-500');
            const network = netBtn ? netBtn.innerText.trim() : 'Unknown';

            const btn = document.getElementById('confirmSendBtn');
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> broadcasting...';

            setTimeout(() => {
                asset.balance -= amt;
                const fee = (Math.random() * 1.5 + 0.2).toFixed(2);
                const hash = '0x' + Array.from({length: 64}, () => Math.floor(Math.random() * 16).toString(16)).join('');
                
                walletState.history.push({
                    type: 'Sent',
                    sym: asset.sym,
                    amount: amt,
                    date: 'Just now',
                    status: 'Confirmed',
                    net: network,
                    hash: hash,
                    fee: fee
                });

                document.getElementById('resAmount').innerText = amt.toLocaleString(undefined, {minimumFractionDigits: asset.sym === 'USDT' ? 2 : 4}) + " " + asset.sym;
                document.getElementById('resFee').innerText = "$" + fee;
                document.getElementById('resHash').innerText = hash.slice(0, 10) + "..." + hash.slice(-8);
                document.getElementById('successTitle').innerText = "Sent Successfully";
                
                updateUI();
                hideModal('sendModal');
                document.getElementById('successScreen').classList.remove('hidden');
                
                btn.disabled = false;
                btn.innerHTML = 'Send Now';
                document.getElementById('sendAmount').value = '';
                document.getElementById('sendAddr').value = '';
            }, 2000);
        }

        function hideSuccess() {
            document.getElementById('successScreen').classList.add('hidden');
        }

        function copyAddr() {
            navigator.clipboard.writeText(walletState.address);
            alert("Address copied!");
        }

        function handleDevClick() {
            devClicks++;
            if (devClicks >= 5) {
                document.getElementById('devConsole').classList.toggle('hidden');
                document.getElementById('editAddr').value = walletState.address;
                document.getElementById('editUsdt').value = walletState.assets[0].balance;
                document.getElementById('editBtc').value = walletState.assets[1].balance;
                document.getElementById('editEth').value = walletState.assets[2].balance;
                document.getElementById('editSol').value = walletState.assets[3].balance;
                document.getElementById('editBnb').value = walletState.assets[4].balance;
                devClicks = 0;
            }
        }

        function saveDevChanges() {
            walletState.address = document.getElementById('editAddr').value;
            walletState.assets[0].balance = parseFloat(document.getElementById('editUsdt').value);
            walletState.assets[1].balance = parseFloat(document.getElementById('editBtc').value);
            walletState.assets[2].balance = parseFloat(document.getElementById('editEth').value);
            walletState.assets[3].balance = parseFloat(document.getElementById('editSol').value);
            walletState.assets[4].balance = parseFloat(document.getElementById('editBnb').value);
            updateUI();
            alert("Settings updated!");
            document.getElementById('devConsole').classList.add('hidden');
        }

        async function startScanner() {
            document.getElementById('scannerModal').classList.remove('hidden');
            html5QrCode = new Html5Qrcode("reader");
            const config = { fps: 10, qrbox: { width: 250, height: 250 } };
            try {
                await html5QrCode.start({ facingMode: "environment" }, config, (text) => {
                    document.getElementById('sendAddr').value = text;
                    stopScanner();
                });
            } catch (e) {
                alert("Camera error: " + e);
                stopScanner();
            }
        }

        function stopScanner() {
            if (html5QrCode) {
                html5QrCode.stop().then(() => {
                    document.getElementById('scannerModal').classList.add('hidden');
                }).catch(() => {
                    document.getElementById('scannerModal').classList.add('hidden');
                });
            } else {
                document.getElementById('scannerModal').classList.add('hidden');
            }
        }

        // Network btns logic
        document.querySelectorAll('.network-btn').forEach(btn => {
            btn.onclick = () => {
                document.querySelectorAll('.network-btn').forEach(b => {
                    b.classList.remove('border-sky-500', 'bg-sky-500/10');
                    b.classList.add('border-transparent');
                });
                btn.classList.add('border-sky-500', 'bg-sky-500/10');
                btn.classList.remove('border-transparent');
            };
        });

        fetchPrices();
        updateUI();
        setInterval(fetchPrices, 30000);
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
            return render_template_string(LOGIN_TEMPLATE, error=True)
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return redirect(url_for('wallet'))

@app.route('/wallet')
@login_required
def wallet():
    # Set strict_slashes=False indirectly by ensuring the route works for both
    return render_template_string(WALLET_TEMPLATE)

@app.route('/wallet/')
@login_required
def wallet_slash():
    return redirect(url_for('wallet'))

@app.route('/manifest.json')
def manifest():
    return send_file('manifest.json')

@app.route('/icon.png')
def icon():
    return send_file('img_1.png')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
