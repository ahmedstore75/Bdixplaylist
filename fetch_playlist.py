import os
import json
import requests

API_URL = "https://sm-monirul.top/api/app/info/channel_data.json"
OUTPUT_DIR = "Bangla-Iptv"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def extract_channels(data):
    """
    JSON ডাটার ভেতরে যেখানেই ক্যাটাগরি বা চ্যানেলের লিস্ট থাকুক না কেন, 
    তা রিকার্সিভলি (Recursively) খুঁজে বের করবে।
    """
    channels = []
    
    if isinstance(data, list):
        for item in data:
            channels.extend(extract_channels(item))
    elif isinstance(data, dict):
        # যদি অবজেক্টটির ভেতরে স্ট্রিম লিঙ্ক থাকে, তবে এটি একটি চ্যানেল
        has_url = any(k in data for k in ["url", "stream_url", "link", "src", "stream", "m3u8"])
        if has_url:
            channels.append(data)
        else:
            # না থাকলে ভেতরের লিস্ট বা ক্যাটাগরির মধ্যে সার্চ করবে
            for value in data.values():
                if isinstance(value, (list, dict)):
                    channels.extend(extract_channels(value))
                    
    return channels

def generate_playlists():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        # ১. API থেকে ডাটা আনা
        print("Fetching JSON data from API...")
        response = requests.get(API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        # ২. Bangla-Iptv/playlist.json সেভ করা
        json_file_path = os.path.join(OUTPUT_DIR, "playlist.json")
        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print("✅ JSON playlist saved successfully.")

        # ৩. সেভ হওয়া JSON থেকে চ্যানেলের তালিকা এক্সট্র্যাক্ট করা
        channels = extract_channels(data)
        print(f"Total channels extracted: {len(channels)}")

        # ৪. M3U ফাইল তৈরি করা
        m3u_file_path = os.path.join(OUTPUT_DIR, "playlist.m3u")
        m3u_content = "#EXTM3U\n"

        valid_channel_count = 0
        for ch in channels:
            # চ্যানেল নেম খোঁজা
            name = (ch.get("name") or ch.get("channel_name") or 
                    ch.get("title") or ch.get("channel_title") or 
                    ch.get("tvg-name") or "Unknown Channel")
            
            # লোগো ইউআরএল খোঁজা
            logo = (ch.get("logo") or ch.get("icon") or 
                    ch.get("image") or ch.get("channel_logo") or 
                    ch.get("tvg-logo") or "")
            
            # স্ট্রিম ইউআরএল খোঁজা
            url = (ch.get("url") or ch.get("stream_url") or 
                   ch.get("link") or ch.get("src") or 
                   ch.get("stream") or ch.get("m3u8") or "")

            if url and isinstance(url, str) and url.startswith("http"):
                m3u_content += f'#EXTINF:-1 tvg-logo="{logo}",{name}\n{url}\n'
                valid_channel_count += 1

        # ৫. Bangla-Iptv/playlist.m3u সেভ করা
        with open(m3u_file_path, "w", encoding="utf-8") as f:
            f.write(m3u_content)
        
        print(f"✅ M3U playlist saved successfully with {valid_channel_count} channels.")

    except Exception as e:
        print(f"❌ Error generating playlists: {e}")

if __name__ == "__main__":
    generate_playlists()
