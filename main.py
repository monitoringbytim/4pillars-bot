import os
import requests
import re
import time
import google.generativeai as genai

# 환경 변수 설정
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')
TELE_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

genai.configure(api_key=GEMINI_KEY)

def get_latest_article():
    target_url = "https://4pillars.io/ko/articles"
    
    # [차별점] 실제 브라우저와 거의 흡사한 헤더 세팅
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8',
        'Referer': 'https://www.google.com/', # 구글에서 타고 들어온 척 합니다.
    }

    try:
        print(f"📡 포필러스 직접 연결 시도...")
        # 세션을 사용해 쿠키 등을 유지하며 접근합니다.
        session = requests.Session()
        res = session.get(target_url, headers=headers, timeout=20)
        
        if res.status_code == 200:
            print("✅ 접속 성공! HTML 분석 중...")
            # 링크 추출 (/ko/articles/...)
            links = re.findall(r'/ko/articles/[a-zA-Z0-9-]+', res.text)
            if links:
                unique_links = list(dict.fromkeys(links))
                return f"https://4pillars.io{unique_links[0]}"
        else:
            print(f"❌ 접속 차단됨 (코드: {res.status_code})")
    except Exception as e:
        print(f"🚨 접속 중 에러: {e}")
    return None
