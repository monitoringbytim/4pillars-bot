import os, requests, google.generativeai as genai

# 환경 변수 설정
TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 🎯 포필러스 내부 데이터 API (이게 핵심 우회로입니다!)
    api_url = "https://4pillars.io/api/articles?lang=ko&limit=1"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    try:
        res = requests.get(api_url, headers=headers, timeout=15)
        data = res.json()
        # API 응답에서 기사 슬러그(주소 끝부분) 추출
        article = data.get('articles', [])[0]
        if article:
            return f"https://4pillars.io/ko/articles/{article.get('slug')}"
    except Exception as e:
        print(f"API 접속 에러: {e}")
    return None

def main():
    latest_url = get_latest_article()
    if not latest_url:
        print("기사 주소를 찾지 못했습니다. (API 우회 실패)")
        return

    # 중복 체크
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print(f"이미 처리된 기사입니다: {latest_url}")
                return

    # Gemini 요약
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"아래 웹사이트 기사를 읽고 한국어로 핵심을 요약해줘. 1문장 정의, 3가지 핵심 포인트, 시사점 1문장 순서로 작성해줘:\nURL: {latest_url}"
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        print(f"요약 에러: {e}")
        return

    # 텔레그램 전송
    msg = f"🆕 **포필러스 새로운 리서치**\n\n{summary}\n\n🔗 원문: {latest_url}"
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    # 새로운 주소 저장
    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print(f"전송 완료! 주소: {latest_url}")

if __name__ == "__main__":
    main()
