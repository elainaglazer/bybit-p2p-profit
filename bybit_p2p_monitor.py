import requests
import time
import winsound
import ctypes
import os
from datetime import datetime

# Configuration
URL = "https://api2.bybit.com/fiat/otc/item/online"
TOKEN = "USDT"
CURRENCY = "VND"
THRESHOLD = 190 # VND
CHECK_INTERVAL = 30  # seconds
CAPITAL = 5500000  # VND - Max limit for seller's min amount (and target trade amount)
ALERT_MP3 = "alert.mp3"  # Put your MP3 file in the same folder

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-Type": "application/json"
}

def fetch_best_price(side_code, capital=CAPITAL):
    """
    Fetches the best price for a given side.
    side_code: "1" for User Buy (Merchant Sell), "0" for User Sell (Merchant Buy)
    Returns: (price, merchant_name) or (None, None) if failed
    """
    payload = {
        "userId": "",
        "tokenId": TOKEN,
        "currencyId": CURRENCY,
        "payment": [],
        "side": side_code,
        "size": "5",  # We only need the top few to find the best
        "page": "1",
        "amount": str(capital)
    }

    try:
        response = requests.post(URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data['ret_code'] == 0 and data['result']['items']:
            items = data['result']['items']
            # Explicitly sort to be safe
            # side="1" (User Buy) -> We want the LOWEST price (Merchant selling cheap)
            # side="0" (User Sell) -> We want the HIGHEST price (Merchant buying expensive)
            
            if side_code == "1":
                best_item = min(items, key=lambda x: float(x['price']))
            else:
                best_item = max(items, key=lambda x: float(x['price']))
                
            return float(best_item['price']), best_item['nickName']
        else:
            print(f"Error fetching data for side {side_code}: {data.get('ret_msg', 'Unknown error')}")
            return None, None

    except requests.RequestException as e:
        print(f"Network error fetching side {side_code}: {e}")
        return None, None
    except (KeyError, ValueError, IndexError) as e:
        print(f"Parsing error for side {side_code}: {e}")
        return None, None

def play_custom_sound():
    """
    Plays an MP3 file using Windows MCI (Native, Lightweight, Non-blocking).
    """
    sound_path = os.path.abspath(ALERT_MP3)
    
    if os.path.exists(sound_path):
        try:
            mci = ctypes.windll.winmm.mciSendStringW
            # Close any previous instance to ensure we can replay
            mci('close my_alert', None, 0, 0)
            # Open the file
            mci(f'open "{sound_path}" type mpegvideo alias my_alert', None, 0, 0)
            # Play asynchronously (script continues immediately)
            mci('play my_alert', None, 0, 0)
        except Exception as e:
            print(f"Error playing sound: {e}")
            winsound.Beep(1000, 1000)
    else:
        # Fallback if file is missing
        print(f"[Info] {ALERT_MP3} not found. Using system beep.")
        winsound.Beep(1000, 1000)

def trigger_alert(spread, buy_price, sell_price, buy_merchant, sell_merchant):
    print(f"\n[ALERT] Profitable Arbitrage Opportunity!")
    print(f"Spread: {spread:,.2f} VND")
    print(f"Buy from: {buy_merchant} @ {buy_price:,.2f} VND")
    print(f"Sell to:  {sell_merchant} @ {sell_price:,.2f} VND")
    
    play_custom_sound()

def main():
    print(f"Starting Bybit P2P Monitor ({TOKEN}/{CURRENCY})...")
    print(f"Target Spread: >= {THRESHOLD} VND")
    print(f"Capital Amount: {CAPITAL:,.0f} VND")
    print("Press Ctrl+C to stop.\n")

    while True:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 1. Fetch Lowest SELL price (User Buy) -> side="1"
            # This is the price I pay to buy USDT.
            user_buy_price, buy_merchant = fetch_best_price("1", CAPITAL)

            # 2. Fetch Highest BUY price (User Sell) -> side="0"
            # This is the price I get when I sell USDT.
            user_sell_price, sell_merchant = fetch_best_price("0", CAPITAL)

            if user_buy_price is not None and user_sell_price is not None:
                # Spread = (Price I sell at) - (Price I buy at)
                spread = user_sell_price - user_buy_price
                
                print(f"[{timestamp}] Buy: {user_buy_price:,.2f} ({buy_merchant}) | Sell: {user_sell_price:,.2f} ({sell_merchant}) | Spread: {spread:,.2f}")

                if spread >= THRESHOLD:
                    trigger_alert(spread, user_buy_price, user_sell_price, buy_merchant, sell_merchant)
            
            else:
                print(f"[{timestamp}] Failed to retrieve prices.")

        except KeyboardInterrupt:
            print("\nStopping monitor.")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
