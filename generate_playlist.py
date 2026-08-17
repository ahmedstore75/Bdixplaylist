import re
import urllib.request
from datetime import datetime, timezone, timedelta

# --- CONFIG ---
DATA_URL = "https://raw.githubusercontent.com/ahmedstore75/Iptvbdlive/refs/heads/main/mixiptvchannel.m3u"
PHP_PROXY = "https://iptvlive.ahmed-bd-org.workers.dev"  # আপনার ক্লাউডফ্লেয়ার ডোমেইন
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (Chrome/120.0.0.0) Safari/537.36"
}

# --- Helper: Create Clean Base Channel Slug ---
def get_channel_slug(extinf, index):
    try:
        name = extinf.split(",")[-1].strip() if "," in extinf else f"Channel_{index}"
        clean_name = re.sub(r'[^\w\s\u0980-\u09FF-]', '', name)
        slug = re.sub(r'[\s_]+', '-', clean_name.strip()).lower()
        return slug if slug else f"ch-{index}"
    except Exception:
        return f"ch-{index}"

# --- Download and Parse M3U Data ---
def fetch_m3u_data():
    try:
        req = urllib.request.Request(DATA_URL, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read().decode('utf-8')
        
        lines = content.splitlines()
        channels = []
        current_meta = []
        
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            
            if line_str.startswith("#"):
                if line_str.startswith("#EXTM3U"):
                    continue
                current_meta.append(line_str)
            else:
                if current_meta:
                    channels.append({
                        "meta_lines": current_meta,
                        "raw_url": line_str
                    })
                    current_meta = []
                    
        return channels
    except Exception as e:
        print("❌ Error downloading M3U data:", e)
        return []

# --- Generate Playlist with Duplicate Handling (-1, -2, -3) ---
def generate_playlist(channels):
    bd_tz = timezone(timedelta(hours=6))
    bd_time = datetime.now(bd_tz).strftime('%Y-%m-%d %H:%M:%S')
    
    total_count = 0
    slug_tracker = {}  # ডুপ্লিকেট চ্যানেল গণনা ট্র্যাক রাখার জন্য
    
    lines = [
        "#EXTM3U",
        f"# ⏰ Updated: {bd_time}"
    ]
    
    for idx, ch in enumerate(channels, 1):
        meta_lines = ch.get("meta_lines", [])
        raw_url = ch.get("raw_url", "")
        
        if not meta_lines or not raw_url:
            continue
        
        extinf_line = next((m for m in meta_lines if m.startswith("#EXTINF:")), "")
        base_slug = get_channel_slug(extinf_line, idx)
        
        # একই স্লাগ কতবার এসেছে তা গণনা করা
        slug_tracker[base_slug] = slug_tracker.get(base_slug, 0) + 1
        occurrence = slug_tracker[base_slug]
        
        # ১, ২, ৩ নম্বর যোগ করে ইউনিক স্লাগ তৈরি (যেমন: jamuna-tv-1, jamuna-tv-2)
        unique_slug = f"{base_slug}-{occurrence}"
        stream_url = f"{PHP_PROXY}/{unique_slug}/index.m3u8"
        
        lines.extend(meta_lines)
        lines.append(stream_url)
        total_count += 1
    
    print(f"📊 Processed {total_count} channels with unique indexed slugs.")
    
    with open("playlist.m3u", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    return total_count

if __name__ == "__main__":
    print("🔄 Generating playlist with duplicate channel indexing...")
    try:
        channels = fetch_m3u_data()
        if not channels:
            print("❌ No channels fetched")
            exit(1)
            
        generate_playlist(channels)
        print("✅ Playlist generated successfully")
    except Exception as e:
        print(f"❌ Critical error: {e}")
        exit(1)
