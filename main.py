import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup

app = FastAPI()

# [무적의 경로 설정] 현재 파일의 위치를 기준으로 templates 폴더를 찾음
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(Path(BASE_DIR, "templates")))

def get_wevity_data():
    url = "https://www.wevity.com/?c=find&s=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        contest_items = soup.select('ul.list li')
        
        # 만약 차단당하거나 데이터가 없으면 샘플 데이터 반환 (화면 안 꺼지게)
        if not contest_items or len(contest_items) <= 1:
            return [
                {"title": "서버 IP 차단으로 인해 샘플 데이터를 표시합니다.", "host": "시스템", "status": "알림"},
                {"title": "로컬(PC) 환경에서는 정상 수집됨을 확인했습니다.", "host": "시스템", "status": "확인"},
                {"title": "2026 대학생 자율주행 경진대회", "host": "산업통상자원부", "status": "접수중"},
                {"title": "제15회 앱 공모전", "host": "한국정보화진흥원", "status": "D-5"}
            ]

        results = []
        for item in contest_items:
            title_tag = item.select_one('.tit a')
            if not title_tag: continue
            
            results.append({
                "title": title_tag.text.strip(),
                "host": item.select_one('.organ').text.strip() if item.select_one('.organ') else "주최사미상",
                "status": item.select_one('.status').text.strip() if item.select_one('.status') else "진행중"
            })
        return results
    except Exception:
        return [{"title": "데이터 로드 실패", "host": "Error", "status": "-"}]

@app.get("/")
async def read_root(request: Request):
    data = get_wevity_data()
    # 경로 에러 발생 시 예외 처리를 위해 try-except 추가
    try:
        return templates.TemplateResponse("index.html", {"request": request, "contests": data})
    except Exception as e:
        return {"error": f"Template Error: {str(e)}", "path": str(BASE_DIR)}
