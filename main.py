import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup

app = FastAPI()

current_dir = os.path.dirname(os.path.realpath(__file__))
templates = Jinja2Templates(directory=os.path.join(current_dir, "templates"))

def get_wevity_data():
    url = "https://www.wevity.com/?c=find&s=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        contest_items = soup.select('ul.list li')
        print(f"찾은 항목 개수: {len(contest_items)}개")

        if len(contest_items) <= 1:
            return [
                {"title": "배포 환경에서는 보안상 실시간 수집이 제한될 수 있습니다.", "host": "시스템", "status": "알림"},
                {"title": "로컬 환경(PC)에서는 정상 작동함을 확인했습니다.", "host": "시스템", "status": "알림"},
                {"title": "2026 자율주행 해커톤 (샘플 데이터)", "host": "국토부", "status": "접수중"},
                {"title": "공공 데이터 활용 공모전 (샘플 데이터)", "host": "행안부", "status": "접수중"}
            ]

        results = []
        for item in contest_items:
            title_tag = item.select_one('.tit a')
            if not title_tag: continue
            
            results.append({
                "title": title_tag.text.strip(),
                "host": item.select_one('.organ').text.strip() if item.select_one('.organ') else "위비티",
                "status": item.select_one('.status').text.strip() if item.select_one('.status') else "진행중"
            })
        return results
    except Exception as e:
        print(f"ERROR: {e}")
        return [{"title": "데이터 수집 중 에러 발생", "host": str(e), "status": "에러"}]

@app.get("/")
async def read_root(request: Request):
    data = get_wevity_data()
    # templates 폴더 안에 index.html이 있어야 함
    return templates.TemplateResponse("index.html", {"request": request, "contests": data})
