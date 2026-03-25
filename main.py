import os
import requests
import re
import google.generativeai as genai

# 환경 변수 로드
TELE_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')
genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def get_latest_article():
    target_url = "https://4pillars.io/ko/articles"
    # 브라우저인 척 위장 헤더
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }

    try:
        print(f"📡 {target_url} 접속 시도...")
        res = requests.get(target_url, headers=headers, timeout=20)
        print(f"📊 응답 상태 코드: {res.status_code}")
        
        if res.status_code == 200:
            links = re.findall(r'/ko/articles/[a-zA-Z0-9-]+', res.text)
            if links:
                unique_links = list(dict.fromkeys(links))
                full_url = f"https://4pillars.io{unique_links[0]}"
                print(f"🔗 발견된 최신 링크: {full_url}")
                return full_url
            else:
                print("⚠️ 링크를 찾지 못했습니다. HTML 구조가 바뀐 것 같습니다.")
        else:
            print(f"❌ 접속 실패: {res.text[:100]}") # 에러 내용 일부 출력
    except Exception as e:
        print(f"🚨 접속 중 에러: {e}")
    return None

def main():
    latest_url = get_latest_article()
    
    if not latest_url:
        print("😭 기사 주소를 가져오지 못해 종료합니다.")
        return

    # [테스트용] 중복 체크를 잠시 해제하거나 강제 실행 로그를 남깁니다.
    print(f"🤖 Gemini 분석 시작: {latest_url}")
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"다음 기사 내용을 한국어로 아주 짧게 요약해줘: {latest_url}"
        response = model.generate_content(prompt)
        
        if response.text:
            print("✨ Gemini 분석 완료. 텔레그램 전송 중...")
            tele_res = requests.post(
                f"https://api.telegram.org/bot{TELE_TOKEN}/sendMessage",
                data={"chat_id": CHAT_ID, "text": f"✅ 테스트 성공!\n\n{response.text}\n\n🔗 {latest_url}"}
            )
            print(f"📨 텔레그램 응답: {tele_res.status_code}")
        else:
            print("⚠️ Gemini 응답이 없습니다.")
    except Exception as e:
        print(f"🚨 전송 단계 에러: {e}")

if __name__ == "__main__":
    main()
