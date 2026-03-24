import os, requests, re
import google.generativeai as genai

# 환경 변수 설정
TELE_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

def get_latest_article():
    # 🎯 포필러스 정문이 아닌, 구글 검색 결과를 통해 주소 낚기
    # "site:4pillars.io/ko/articles" 키워드로 검색
    search_url = "https://www.google.com/search?q=site:4pillars.io/ko/articles"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        # 구글 검색 결과 페이지 요청
        res = requests.get(search_url, headers=headers, timeout=15)
        
        # 검색 결과 HTML 내에서 기사 주소 패턴 추출
        links = re.findall(r'https://4pillars\.io/ko/articles/[a-zA-Z0-9-]+', res.text)
        
        if links:
            # 중복 제거 및 첫 번째(최신) 링크 반환
            return list(dict.fromkeys(links))[0]
            
    except Exception as e:
        print(f"구글 검색 우회 에러: {e}")
    return None

def main():
    latest_url = get_latest_article()
    
    if not latest_url:
        print("구글 검색에서도 주소를 찾지 못했습니다. (보안 매우 강력)")
        return

    # 중복 체크
    if os.path.exists("last_url.txt"):
        with open("last_url.txt", "r") as f:
            if f.read().strip() == latest_url:
                print(f"이미 처리된 기사입니다: {latest_url}")
                return

    # Gemini 요약
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"다음 웹사이트 기사를 한국어로 요약해줘. 핵심 내용 3가지를 포함해서 전문적인 톤으로 작성해줘:\nURL: {latest_url}"
    
    try:
        response = model.generate_content(prompt)
        summary = response.text
    except Exception as e:
        summary = f"(요약 생성 중 오류 발생. 원문 링크를 확인하세요.)"

    # 텔레그램 전송
    msg = f"🆕 **포필러스 새로운 리서치 (구글 우회 수집)**\n\n{summary}\n\n🔗 원문: {latest_url}"
    requests.post(f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

    # 새로운 주소 저장
    with open("last_url.txt", "w") as f:
        f.write(latest_url)
    print(f"✅ 구글 우회 전송 성공: {latest_url}")

if __name__ == "__main__":
    main()
