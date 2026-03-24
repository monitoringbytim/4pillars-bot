import os, requests, re
import google.generativeai as genai

# 환경 변수 설정
TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 🎯 구글 뉴스 RSS를 통해 포필러스 최신글 낚기 (가장 안정적인 우회로)
    search_query = "site:4pillars.io/ko/articles"
    rss_url = f"https://news.google.com/rss/search?q={search_query}&hl=ko&gl=KR&ceid=KR:ko"
    
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(rss_url, headers=headers, timeout=15)
        # 구글 뉴스 RSS에서 4pillars 기사 주소만 추출
        links = re.findall(r'https://4pillars\.io/ko/articles/[a-zA-Z0-9-]+', res.text)
        
        if links:
            return links[0] # 가장 최신 링크 반환
            
    except Exception as e:
        print(f"구글 뉴스 우회 에러: {e}")
    return None

def main():
    latest_url = get_latest_article()
    
    if not latest_url:
        print("구글 뉴스에서도 주소를 찾지 못했습니다. 사이트가 업데이트된 지 얼마 안 되었을 수 있습니다.")
        return

    # 중복 체크
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print(f"이미 처리된 기사입니다.")
                return

    # Gemini 요약
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"아래 기사를 읽고 한국어로 핵심을 요약해줘. 원문 링크: {latest_url}"
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        summary = f"(요약 에러 발생)"

    # 텔레그램 전송
    msg = f"🆕 **포필러스 최신 리서치 (구글 뉴스 우회)**\n\n{summary}\n\n🔗 원문: {latest_url}"
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    # 새로운 주소 저장
    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print(f"✅ 구글 뉴스 우회 전송 성공: {latest_url}")

if __name__ == "__main__":
    main()
