import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# 설정
URL = "https://www.kvca.or.kr/Program/board/list.html?a_gb=board&a_cd=5&a_item=0&sm=3_1"
GMAIL_ID = os.environ.get('GMAIL_ID')
GMAIL_PW = os.environ.get('GMAIL_PW') 
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

def get_latest_post():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9'
    }
    
    print("웹사이트 접속 시도 중...")
    response = requests.get(URL, headers=headers)
    
    if response.status_code != 200:
        print(f"접속 실패: 에러 코드 {response.status_code}")
        return None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    
    rows = soup.select('table tr')
    if not rows:
        print("게시판 형태를 찾을 수 없습니다.")
        return None, None

    for row in rows:
        tds = row.find_all('td')
        if not tds:
            continue
            
        num_text = tds[0].text.strip()
        
        if num_text.isdigit():
            title_tag = row.select_one('a')
            if title_tag:
                title = title_tag.text.strip()
                link_href = title_tag['href']
                
                # [수정된 부분] 링크 주소 완성 로직 개선
                if link_href.startswith('http'):
                    link = link_href
                elif link_href.startswith('/'):
                    # 슬래시(/)로 시작하면 도메인 바로 뒤에 붙임
                    link = "https://www.kvca.or.kr" + link_href
                else:
                    # 슬래시 없이 시작하면 중간 경로(Program/board)를 포함하여 붙임
                    link = "https://www.kvca.or.kr/Program/board/" + link_href
                    
                print(f"✅ 최신 글 발견 성공: {title}")
                return title, link
                
    print("일반 게시글(숫자 번호)을 찾지 못했습니다.")
    return None, None

def send_email(title, link):
    msg = MIMEText(f"새로운 공지사항이 올라왔습니다.\n\n제목: {title}\n링크: {link}")
    msg['Subject'] = f"[알림] 벤처캐피탈협회 새 공지사항: {title}"
    msg['From'] = GMAIL_ID
    msg['To'] = RECEIVER_EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(GMAIL_ID, GMAIL_PW)
        server.send_message(msg)

def main():
    latest_title, latest_link = get_latest_post()
    if not latest_title:
        print("최신 글을 가져오지 못해 종료합니다.")
        return

    file_path = 'latest_post.txt'
    
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        print("기존 파일이 비어있어, 현재 글을 새로 저장합니다.")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(latest_title)
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        last_title = f.read().strip()

    print(f"이전 글: {last_title}")
    print(f"현재 글: {latest_title}")

    if latest_title != last_title:
        print("새로운 글이 발견되어 메일을 발송합니다!")
        send_email(latest_title, latest_link)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(latest_title)
    else:
        print("새로운 글이 없습니다.")

if __name__ == "__main__":
    main()
