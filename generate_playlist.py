import os, json, random, string, requests
from datetime import datetime
import pytz

# --- CONFIG ---
DATA_URL = "https://sm-monirul.top/api/app/info/channel_data.json"
PHP_PROXY = "http://xown.site/token/stream.php"
HEADERS = {"User-Agent": "Dalvik/2.1.0 (Linux; Android 10)"}

# TARGET CATEGORY IDS
TARGET_CATEGORY_IDS = {
    "1715", "1716", "1718", "1732", "1735", "1736", "1737", "1531", "1356"
}

# --- 1️⃣ Generate new 32-char token ---
def generate_token():
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    timestamp = int(datetime.now().timestamp())
    with open("token.json", "w") as f:
        json.dump({"token": token, "generated_at": timestamp}, f, indent=2)
    return token

# --- 2️⃣ Download JSON Data directly from URL ---
def fetch_json_data():
    try:
        res = requests.get(DATA_URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
        data = res.json()
        
        categories = []
        channels = []
        
        # JSON স্ট্রাকচার চেক করে ডাটা এক্সট্র্যাক্ট করা
        if isinstance(data, dict):
            categories = data.get("categories") or data.get("category") or []
            channels = data.get("channels") or data.get("streams") or data.get("live_streams") or data.get("data") or []
        elif isinstance(data, list):
            channels = data
            
        return categories, channels
    except Exception as e:
        print("❌ Error downloading JSON data:", e)
        return [], []

# --- 3️⃣ Generate organized playlist ---
def generate_playlist(channels, categories, token):
    bd_tz = pytz.timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    # Category ID to Name mapping
    category_map = {}
    if isinstance(categories, list):
        for cat in categories:
            if isinstance(cat, dict) and "category_id" in cat:
                category_map[str(cat["category_id"])] = cat.get("category_name", "Unknown")
    
    channels_by_category = {}
    selected_count = 0
    skipped_channels = 0
    
    for ch in channels:
        if not ch or not isinstance(ch, dict):
            skipped_channels += 1
            continue
            
        cat_id = str(ch.get("category_id", ""))
        
        if cat_id in TARGET_CATEGORY_IDS:
            category_name = category_map.get(cat_id, f"Category {cat_id}")
            
            name = ch.get("name")
            stream_id = ch.get("stream_id")
            
            if not name or not stream_id:
                skipped_channels += 1
                continue
                
            if category_name not in channels_by_category:
                channels_by_category[category_name] = []
            
            channels_by_category[category_name].append(ch)
            selected_count += 1
    
    print(f"📊 Processed {len(channels)} channels, selected {selected_count}, skipped {skipped_channels}")
    
    lines = [
        "#EXTM3U",
        "# 📦 filoox-bdix Auto Playlist (Selected Categories)",
        f"# ⏰ BD Updated time: {bd_time}",
        f"# 🔄 Updated hourly — Total channels: {selected_count}",
        f"# 🎯 Selected categories: {len(TARGET_CATEGORY_IDS)}",
        f"# 📊 Skipped invalid: {skipped_channels}",
        "# 🔁 Each stream link uses token validation",
        "# 🌐 @ Credit: @sultanarabi161"
    ]
    
    lines.extend([
        '#EXTINF:-1 tvg-id="" tvg-name="📺 Welcome" tvg-logo="https://filexo.vercel.app/image/sultanarabi161.jpg" group-title="Intro",📺 Welcome',
        'https://filexo.vercel.app/video/credit_developed_by_sultanarabi161.mp4'
    ])
    
    for category_name, category_channels in sorted(channels_by_category.items()):
        lines.append(f"# 🟢 {category_name} ({len(category_channels)} channels)")
        
        for ch in category_channels:
            name = str(ch.get("name", "Unknown")).strip()
            logo = str(ch.get("stream_icon", "")).strip()
            stream_id = ch.get("stream_id")
            
            if not name or name == "Unknown" or not stream_id:
                continue
                
            stream_url = f"{PHP_PROXY}?id={stream_id}&token={token}"
            extinf_line = f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="{logo}" group-title="{category_name}",{name}'
            lines.append(extinf_line)
            lines.append(stream_url)
    
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return selected_count

# --- MAIN ---
if __name__ == "__main__":
    print("🔄 Starting playlist generation (Selected Categories)...")
    
    try:
        new_token = generate_token()
        print("✅ Token generated")
        
        categories, channels = fetch_json_data()
        
        if not channels:
            print("❌ No channels fetched from JSON link")
            exit(1)
            
        print(f"📊 Fetched {len(categories)} categories and {len(channels)} channels from JSON")
        
        total_channels = generate_playlist(channels, categories, new_token)
        
        print(f"✅ Playlist generated with {total_channels} channels from selected categories")
        print("🎯 Token & playlist updated successfully")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        exit(1)
