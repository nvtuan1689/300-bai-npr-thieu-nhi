#!/usr/bin/env python3
"""
Demo script - Test các chức năng cơ bản
"""

import requests
from bs4 import BeautifulSoup
import re

# Test URL
test_url = "https://www.npr.org/transcripts/nx-s1-5655252"

print("="*70)
print("TESTING NPR SCRAPER FUNCTIONS")
print("="*70)

# 1. Test download webpage
print("\n1️⃣ Testing webpage download...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(test_url, headers=headers, timeout=10)
    print(f"   ✅ Status: {response.status_code}")
    print(f"   ✅ Content length: {len(response.text)} characters")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# 2. Test parse HTML
print("\n2️⃣ Testing HTML parsing...")
try:
    soup = BeautifulSoup(response.text, 'html.parser')
    print(f"   ✅ Parsed successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# 3. Test find title
print("\n3️⃣ Testing title extraction...")
try:
    title = None
    title_h1 = soup.find('h1', class_='transcript')
    if title_h1:
        title = title_h1.get_text(strip=True)
        title = re.sub(r'^<\s*', '', title)
    
    if not title:
        title_meta = soup.find('meta', property='og:title')
        if title_meta:
            title = title_meta.get('content', '').strip()
    
    if title:
        print(f"   ✅ Title found: {title[:60]}...")
    else:
        print(f"   ⚠️ Title not found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Test find transcript
print("\n4️⃣ Testing transcript extraction...")
try:
    article = soup.find('article')
    if article:
        paragraphs = article.find_all('p')
        transcript_parts = []
        in_transcript = False
        
        for p in paragraphs:
            text = p.get_text(strip=True)
            if 'HOST:' in text or 'BYLINE:' in text:
                in_transcript = True
            
            if in_transcript:
                transcript_parts.append(text)
                
                if 'Thank you' in text and len(transcript_parts) > 10:
                    break
        
        transcript = '\n\n'.join(transcript_parts)
        
        if transcript:
            print(f"   ✅ Transcript found: {len(transcript)} characters")
            print(f"   ✅ First 100 chars: {transcript[:100]}...")
        else:
            print(f"   ⚠️ Transcript not found")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Test find audio URL
print("\n5️⃣ Testing audio URL extraction...")
try:
    audio_url = None
    mp3_pattern = r'https?://[^\s<>"]+?\.mp3[^\s<>"]*'
    matches = re.findall(mp3_pattern, response.text)
    
    if matches:
        for match in matches:
            if 'npr' in match.lower() or 'ondemand' in match.lower():
                audio_url = match.replace('\\', '')
                break
    
    if audio_url:
        print(f"   ✅ Audio URL found")
        print(f"   🔗 {audio_url[:80]}...")
    else:
        print(f"   ⚠️ Audio URL not found")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("✅ ALL TESTS COMPLETED!")
print("="*70)
