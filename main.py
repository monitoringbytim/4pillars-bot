import os, requests, google.generativeai as genai

# 환경 변수 가져오기
TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 포필러스 최신글 주소 낚기 (보안 우회 헤더 포함)
    url = "https://4pillars.io/ko/articles"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    import re
    match = re.search(r'/ko/articles/[a-zA-Z0-9-]+', res.text)
    return f"https://4pillars.io{match.group()}" if match else None

def main():
    latest_url = get_latest_article()
    if not latest_url: return

    # 중복 체크 (last_url.txt 파일과 비교)
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print("중복 기사입니다. 종료.")
                return

    # Gemini 요약 (프롬프트는 기존 것 활용)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"다음 기사를 읽고 한국어로 핵심 요약해줘: {latest_url}")
    summary = response.text

    # 텔레그램 전송
    msg = f"🆕 **새로운 리서치**\n\n{summary}\n\n🔗 원문: {latest_url}"
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    # 새로운 주소 저장
    with open("last_url.txt", "w") as f:
        f.write(latest_url)

if __name__ == "__main__":
    main()
