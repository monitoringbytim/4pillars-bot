import os, requests, google.generativeai as genai

# 환경 변수 설정
TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 🎯 포필러스 진짜 데이터 서버 주소 (여기는 보안이 훨씬 유연합니다)
    api_url = "https://api.4pillars.io/v1/articles?language=ko&limit=1"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Origin": "https://4pillars.io",
        "Referer": "https://4pillars.io/"
    }
    
    try:
        res = requests.get(api_url, headers=headers, timeout=15)
        # 만약 응답이 성공적이지 않으면 에러 출력
        if res.status_code != 200:
            print(f"상태 코드 에러: {res.status_code}")
            return None
            
        data = res.json()
        # API 응답에서 첫 번째 기사의 슬러그 추출
        # 데이터 구조: [ { "slug": "...", ... } ] 또는 { "data": [ { ... } ] }
        articles = data.get('data', data) if isinstance(data, dict) else data
        
        if articles and len(articles) > 0:
            slug = articles[0].get('slug')
            return f"https://4pillars.io/ko/articles/{slug}"
            
    except Exception as e:
        print(f"데이터 서버 접속 에러: {e}")
    return None

def main():
    latest_url = get_latest_article()
    if not latest_url:
        print("최종 우회로도 차단되었습니다.")
        return

    # 중복 체크
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print(f"이미 처리된 기사입니다.")
                return

    # Gemini 요약
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"아래 기사를 한국어로 3줄 요약해줘:\nURL: {latest_url}"
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        summary = f"(요약 에러 발생: 원문을 확인하세요)"

    # 텔레그램 전송
    msg = f"🆕 **포필러스 최신 리서치**\n\n{summary}\n\n🔗 원문: {latest_url}"
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    # 새로운 주소 저장
    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print(f"✅ 전송 성공: {latest_url}")

if __name__ == "__main__":
    main()
