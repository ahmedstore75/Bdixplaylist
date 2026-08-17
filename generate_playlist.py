import random
import string
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta

# --- CONFIG ---
DATA_URL = "https://raw.githubusercontent.com/ahmedstore75/Iptvbdlive/refs/heads/main/mixiptvchannel.m3u"
PHP_PROXY = "https://iptvlive.ahmed-bd-org.workers.dev"  # আপনার ক্লাউডফ্লেয়ার ডোমেইন
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- 1️⃣ Generate new 8-char short token (In-Memory) ---
def generate_token():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

# --- 2️⃣ Download and Parse M3U Data ---
def fetch_m3u_data():
    try:
        req = urllib.request.Request(DATA_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
        
        lines = content.splitlines()
        channels = []
        current_extinf = ""
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("#EXTINF:"):
                current_extinf = line
            elif not line.startswith("#") and current_extinf:
                channels.append({
                    "extinf": current_extinf,
                    "raw_url": line
                })
                current_extinf = ""
                
        return channels
    except Exception as e:
        print("❌ Error downloading M3U data:", e)
        return []

# --- Helper: Create Clean Channel Slug ---
def get_channel_slug(extinf, index):
    try:
        name = extinf.split(",")[-1].strip() if "," in extinf else f"Channel_{index}"
        clean_name = re.sub(r'[^\w\s\u0980-\u09FF-]', '', name)
        slug = re.sub(r'\s+', '_', clean_name.strip())
        return slug if slug else f"ch_{index}"
    except Exception:
        return f"ch_{index}"

# --- 3️⃣ Generate playlist ---
def generate_playlist(channels, token):
    # বাংলাদেশ সময় (UTC+6)
    bd_tz = timezone(timedelta(hours=6))
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    total_count = 0
    skipped_channels = 0
    
    lines = [
        "#EXTM3U",
        "# 📦 iptvlive Auto Playlist",
        f"# ⏰ BD Updated time: {bd_time}",
        "# 🌐 @ Credit: @ahmedstore75"
    ]
    
    for idx, ch in enumerate(channels, 1):
        if not ch or not isinstance(ch, dict):
            skipped_channels += 1
            continue
            
        extinf = ch.get("extinf", "").strip()
        raw_url = ch.get("raw_url", "").strip()
        
        if not extinf or not raw_url:
            skipped_channels += 1
            continue
            
        # চ্যানেলের নাম + .m3u8 যুক্ত করে লিংক তৈরি
        ch_slug = get_channel_slug(extinf, idx)
        stream_url = f"{PHP_PROXY}?id={urllib.parse.quote(ch_slug)}.m3u8&token={token}"
        
        lines.append(extinf)
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
        print(f"✅ Generated token: {new_token}")
        
        channels = fetch_m3u_data()
        
        if not channels:
            print("❌ No channels fetched from M3U link")
            exit(1)
            
        print(f"📊 Parsed {len(channels)} channels from M3U")
        
        total_channels = generate_playlist(channels, new_token)
        
        print(f"✅ Playlist generated with {total_channels} channels")
        print("🎯 Playlist updated successfully")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        exit(1)
