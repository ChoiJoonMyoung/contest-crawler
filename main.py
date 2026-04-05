from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_wevity_data():
    url = "https://www.wevity.com/?c=find&s=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        contest_items = soup.select('ul.list li')
        
        print(f"찾은 항목 개수: {len(contest_items)}개")

        results = []
        for item in contest_items:
            title_tag = item.select_one('.tit a')
            if not title_tag: continue
            
            title = title_tag.text.strip()
            host = item.select_one('.organ').text.strip() if item.select_one('.organ') else "주최사 정보 없음"
            status = item.select_one('.status').text.strip() if item.select_one('.status') else "진행중"

            results.append({
                "title": title,
                "host": host,
                "status": status
            })
            
            if len(results) >= 15: break
            
        return results
    except Exception as e:
        print(f"ERROR: {e}")
        return []

@app.get("/")
async def read_root(request: Request):
    data = get_wevity_data()
    return templates.TemplateResponse("index.html", {"request": request, "contests": data})