import os, requests, re, google.generativeai as genai

TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 가장 단순한 메인 페이지 접속
    url = "https://4pillars.io/ko/articles"
    # 브라우저인 척 하는 헤더를 더 강력하게 세팅
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        res = requests.get(url, headers=headers, timeout=20)
        # HTML 통째로 뒤져서 /ko/articles/로 시작하는 첫번째 주소 낚기
        links = re.findall(r'/ko/articles/[a-zA-Z0-9-]+', res.text)
        if links:
            # 중복 제거 후 첫번째 주소 완성
            unique_links = list(dict.fromkeys(links))
            return f"https://4pillars.io{unique_links[0]}"
    except:
        pass
    return None

def main():
    latest_url = get_latest_article()
    if not latest_url:
        print("정공법 실패. 구글 뉴스 재시도 중...")
        # (여기에 아까 성공 확률 높았던 구글 뉴스 코드를 백업으로 넣음)
        rss_url = "https://news.google.com/rss/search?q=site:4pillars.io/ko/articles&hl=ko&gl=KR&ceid=KR:ko"
        res = requests.get(rss_url, timeout=15)
        links = re.findall(r'https://4pillars\.io/ko/articles/[a-zA-Z0-9-]+', res.text)
        if links:
            latest_url = links[0]
    
    if not latest_url:
        print("모든 수단 실패. 사이트 차단이 매우 강력합니다.")
        return

    # 중복 체크 및 발송 로직은 동일...
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print("이미 처리됨")
                return

    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(f"요약해줘: {latest_url}")
    
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": f"🆕 {latest_url}\n\n{response.text}"})

    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print("성공")

if __name__ == "__main__":
    main()
