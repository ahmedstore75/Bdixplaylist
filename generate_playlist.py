import os, json, random, string, requests, re
from datetime import datetime
import pytz

# --- CONFIG ---
DATA_URL = "https://raw.githubusercontent.com/ahmedstore75/Iptvbdlive/refs/heads/main/mixiptvchannel.m3u"
PHP_PROXY = "https://iptvlive-beta.vercel.app"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 1️⃣ Generate new 32-char token ---
def generate_token():
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
    timestamp = int(datetime.now().timestamp())
    with open("token.json", "w") as f:
        json.dump({"token": token, "generated_at": timestamp}, f, indent=2)
    return token

# --- 2️⃣ Download and Parse M3U Data ---
def fetch_m3u_data():
    try:
        res = requests.get(DATA_URL, headers=HEADERS, timeout=15)
        res.raise_for_status()
        lines = res.text.splitlines()
        
        channels = []
        current_ch = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("#EXTINF:"):
                current_ch = {}
                # Extract group-title (Category)
                group_match = re.search(r'group-title="([^"]*)"', line)
                cat_name = group_match.group(1) if group_match else "Uncategorized"
                
                # Extract tvg-logo
                logo_match = re.search(r'tvg-logo="([^"]*)"', line)
                logo = logo_match.group(1) if logo_match else ""
                
                # Extract Channel Name
                name = line.split(",")[-1].strip() if "," in line else "Unknown"
                
                current_ch["category_name"] = cat_name if cat_name else "Uncategorized"
                current_ch["name"] = name
                current_ch["stream_icon"] = logo
                
            elif not line.startswith("#") and current_ch:
                # Extract Stream ID from URL
                stream_id = line
                id_match = re.search(r'[?&]id=([^&]+)', line)
                if id_match:
                    stream_id = id_match.group(1)
                elif line.startswith("http"):
                    parts = line.rstrip('/').split('/')
                    stream_id = parts[-1] if parts else line
                
                current_ch["stream_id"] = stream_id
                current_ch["raw_url"] = line
                channels.append(current_ch)
                current_ch = {}
                
        return channels
    except Exception as e:
        print("❌ Error downloading M3U data:", e)
        return []

# --- 3️⃣ Generate playlist with valid Stream ID ---
def generate_playlist(channels, token):
    bd_tz = pytz.timezone('Asia/Dhaka')
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    total_count = 0
    skipped_channels = 0
    
    lines = [
        "#EXTM3U",
        "# 📦 filoox-bdix Auto Playlist",
        f"# ⏰ BD Updated time: {bd_time}",
        "# 🌐 @ Credit: @sultanarabi161"
    ]
    
    # Intro Video
    lines.extend([
        '#EXTINF:-1 tvg-id="" tvg-name="📺 Welcome" tvg-logo="https://filexo.vercel.app/image/sultanarabi161.jpg" group-title="Intro",📺 Welcome',
        'https://filexo.vercel.app/video/credit_developed_by_sultanarabi161.mp4'
    ])
    
    for ch in channels:
        if not ch or not isinstance(ch, dict):
            skipped_channels += 1
            continue
            
        name = str(ch.get("name", "Unknown")).strip()
        logo = str(ch.get("stream_icon", "")).strip()
        category_name = str(ch.get("category_name", "Uncategorized")).strip()
        stream_id = ch.get("stream_id")
        
        if not name or name == "Unknown" or not stream_id:
            skipped_channels += 1
            continue
            
        # Vercel ব্যাকএন্ডের জন্য সঠিক stream_id ব্যবহার করা হয়েছে
        stream_url = f"{PHP_PROXY}?id={stream_id}&token={token}"
        
        extinf_line = f'#EXTINF:-1 tvg-id="" tvg-name="{name}" tvg-logo="{logo}" group-title="{category_name}",{name}'
        lines.append(extinf_line)
        lines.append(stream_url)
        total_count += 1
    
    print(f"📊 Processed {len(channels)} channels, total added: {total_count}, skipped: {skipped_channels}")
    
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return total_count

# --- MAIN ---
if __name__ == "__main__":
    print("🔄 Starting playlist generation...")
    
    try:
        new_token = generate_token()
        print("✅ Token generated")
        
        channels = fetch_m3u_data()
        
        if not channels:
            print("❌ No channels fetched from M3U link")
            exit(1)
            
        print(f"📊 Parsed {len(channels)} channels from M3U")
        
        total_channels = generate_playlist(channels, new_token)
        
        print(f"✅ Playlist generated with {total_channels} channels")
        print("🎯 Token & playlist updated successfully")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        exit(1)
