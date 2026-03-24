import os, requests, re
import google.generativeai as genai

# 환경 변수 설정
TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 🎯 포필러스 공식 RSS 피드 (차단 확률이 가장 낮습니다)
    rss_url = "https://4pillars.io/ko/rss.xml"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(rss_url, headers=headers, timeout=15)
        if res.status_code != 200:
            print(f"상태 코드 에러: {res.status_code}")
            return None
            
        # XML 데이터에서 기사 링크 추출
        # <link>https://4pillars.io/ko/articles/...</link> 패턴 찾기
        links = re.findall(r'<link>(https://4pillars\.io/ko/articles/[^<]+)</link>', res.text)
        
        if links:
            # 첫 번째 링크가 가장 최신 글입니다
            return links[0]
            
    except Exception as e:
        print(f"RSS 피드 접속 에러: {e}")
    return None

def main():
    latest_url = get_latest_article()
    if not latest_url:
        print("RSS 피드에서도 기사를 찾지 못했습니다.")
        return

    # 중복 체크
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print(f"이미 처리된 기사입니다.")
                return

    # Gemini 요약
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"아래 기사 내용을 한국어로 요약해줘. 1문장 정의, 3가지 핵심 포인트, 시사점 순서로 작성해줘:\nURL: {latest_url}"
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        summary = f"(요약 생성 중 오류가 발생했습니다. 원문을 확인하세요.)"

    # 텔레그램 전송
    msg = f"🆕 **포필러스 최신 리서치**\n\n{summary}\n\n🔗 원문: {latest_url}"
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    # 새로운 주소 저장
    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print(f"✅ RSS를 통한 전송 성공: {latest_url}")

if __name__ == "__main__":
    main()
