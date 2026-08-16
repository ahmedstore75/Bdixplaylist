# --- CONFIG ---
DATA_URL = "https://raw.githubusercontent.com/ahmedstore75/Iptvbdlive/refs/heads/main/mixiptvchannel.m3u"
PHP_PROXY = "http://xown.site/token/stream.php"

# ব্রাউজার User-Agent (যাতে সার্ভার ব্লক না করে)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 2️⃣ Download JSON Data directly from URL ---
def fetch_json_data():
    try:
        res = requests.get(DATA_URL, headers=HEADERS, timeout=15, verify=False)
        print(f"📡 HTTP Response Status: {res.status_code}")
        
        res.raise_for_status()
        data = res.json()
        
        categories = []
        channels = []
        
        if isinstance(data, dict):
            categories = data.get("categories") or data.get("category") or []
            channels = data.get("channels") or data.get("streams") or data.get("live_streams") or data.get("data") or []
        elif isinstance(data, list):
            channels = data
            
        return categories, channels
    except Exception as e:
        print("❌ Error downloading JSON data:", e)
        # সার্ভার কী রেসপন্স পাঠাচ্ছে তা দেখার জন্য
        if 'res' in locals():
            print("📄 Server Response Content:", res.text[:300])
        return [], []
