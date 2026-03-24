import os, requests, re, google.generativeai as genai

TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 🎯 우회로: AllOrigins라는 무료 프록시 서비스를 경유해서 접속합니다.
    # 이렇게 하면 포필러스는 GitHub IP가 아닌 프록시 서버 IP를 보게 됩니다.
    target_url = "https://4pillars.io/ko/articles"
    proxy_url = f"https://api.allorigins.win/get?url={target_url}"
    
    try:
        res = requests.get(proxy_url, timeout=30)
        # 프록시 서비스는 실제 내용을 'contents'라는 키 안에 담아 줍니다.
        html_content = res.json().get('contents', '')
        
        links = re.findall(r'/ko/articles/[a-zA-Z0-9-]+', html_content)
        if links:
            unique_links = list(dict.fromkeys(links))
            return f"https://4pillars.io{unique_links[0]}"
    except Exception as e:
        print(f"프록시 우회 실패: {e}")
    return None

def main():
    latest_url = get_latest_article()
    
    if not latest_url:
        print("프록시 우회마저 실패했습니다. 포필러스의 방어력이 최상급입니다.")
        return

    # 중복 체크 (기존과 동일)
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print(f"이미 처리된 기사입니다.")
                return

    model = genai.GenerativeModel('gemini-1.5-flash')
    # 기사 요약 프롬프트
    prompt = f"아래 기사를 한국어로 요약해줘:\nURL: {latest_url}"
    response = model.generate_content(prompt)
    
    # 텔레그램 전송
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": f"🆕 {latest_url}\n\n{response.text}"})

    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print("✅ 프록시 우회 성공 및 전송 완료!")

if __name__ == "__main__":
    main()
