import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import os

# 1. 설정 (GitHub Secrets에서 가져옴)
URL = "https://www.kvca.or.kr/Program/board/list.html?a_gb=board&a_cd=5&a_item=0&sm=3_1"
GMAIL_ID = os.environ.get('GMAIL_ID')
GMAIL_PW = os.environ.get('GMAIL_PW') 
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')

def get_latest_post():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 게시판 리스트 탐색 (공지는 제외하고 첫 번째 일반 글 찾기)
    rows = soup.select('table tbody tr')
    for row in rows:
        num_td = row.select_one('td') # 번호 칸
        # 번호가 숫자로 된 것이 일반 최신글 (공지는 제외됨)
        if num_td and num_td.text.strip().isdigit():
            title_tag = row.select_one('td.subject a') or row.select_one('a')
            title = title_tag.text.strip()
            link = "https://www.kvca.or.kr" + title_tag['href']
            return title, link
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
        return

    file_path = 'latest_post.txt'
    
    # 파일이 없으면 처음 실행이므로 현재 글을 저장만 하고 종료
    if not os.path.exists(file_path):
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(latest_title)
        return

    # 이전 글 제목 불러오기
    with open(file_path, 'r', encoding='utf-8') as f:
        last_title = f.read().strip()

    # 최신 글과 저장된 글이 다르면 (새 글이 올라왔으면)
    if latest_title != last_title:
        send_email(latest_title, latest_link) # 메일 발송
        # 새 글 제목으로 텍스트 파일 덮어쓰기
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(latest_title)

if __name__ == "__main__":
    main()
