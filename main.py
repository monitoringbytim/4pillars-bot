import os, requests, re
import google.generativeai as genai

# 환경 변수 설정
TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    url = "https://4pillars.io/ko/articles"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        # 기사 주소 패턴 매칭
        match = re.search(r'/ko/articles/[a-zA-Z0-9-]+', res.text)
        if match:
            return f"https://4pillars.io{match.group()}"
    except Exception as e:
        print(f"접속 에러: {e}")
    return None

def main():
    latest_url = get_latest_article()
    if not latest_url:
        print("기사 주소를 찾지 못했습니다.")
        return

    # 중복 체크
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print("이미 처리된 기사입니다. 종료합니다.")
                return

    # Gemini 요약 (프롬프트 강화)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # 📝 여기에 사용자님의 핵심 프롬프트를 넣었습니다!
    prompt = f"""
    아래 웹사이트의 내용을 읽고 한국어로 핵심 내용을 요약해줘:
    URL: {latest_url}

    요약 가이드라인:
    1. 이 리서치가 무엇을 다루고 있는지 1문장으로 정의해줘.
    2. 가장 중요한 포인트 3가지를 불렛포인트로 정리해줘.
    3. 이 글이 시장에 주는 시사점이나 결론을 1문장으로 덧붙여줘.
    4. 톤앤매너는 전문적이면서도 읽기 쉽게 작성해줘.
    """
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        print(f"Gemini 요약 에러: {e}")
        return

    # 텔레그램 메시지 구성
    msg = f"🆕 **포필러스 새로운 리서치**\n\n{summary}\n\n🔗 원문 읽기: {latest_url}"
    
    # 텔레그램 전송
    tele_url = f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    
    requests.post(tele_url, data=payload)

    # 새로운 주소 저장 (기억 장치)
    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print(f"성공적으로 전송 완료: {latest_url}")

if __name__ == "__main__":
    main()
