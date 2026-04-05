from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import requests
from bs4 import BeautifulSoup

app = FastAPI()

def get_wevity_data():
    url = "https://www.wevity.com/?c=find&s=1"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('ul.list li')
        
        # 데이터가 없으면 샘플 데이터 반환
        if not items or len(items) <= 1:
            return [{"title": "샘플: 2026 자율주행 경진대회", "host": "산업통상자원부", "status": "접수중"}] * 5

        results = []
        for item in items[:15]:
            title_tag = item.select_one('.tit a')
            if not title_tag: continue
            results.append({
                "title": title_tag.text.strip(),
                "host": item.select_one('.organ').text.strip() if item.select_one('.organ') else "위비티",
                "status": item.select_one('.status').text.strip() if item.select_one('.status') else "진행중"
            })
        return results
    except Exception:
        return [{"title": "데이터 로딩 실패", "host": "-", "status": "-"}]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    data = get_wevity_data()
    
    # HTML 표 내용을 문자열로 직접 생성
    rows = ""
    for idx, c in enumerate(data, 1):
        rows += f"<tr><td>{idx}</td><td>{c['title']}</td><td>{c['host']}</td><td>{c['status']}</td></tr>"

    # 전체 HTML 구조
    html_content = f"""
    <html>
        <head>
            <meta charset="utf-8">
            <title>최준명 공모전 크롤러</title>
            <style>
                body {{ font-family: sans-serif; padding: 20px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f8f9fa; }}
                h1 {{ color: #007bff; }}
            </style>
        </head>
        <body>
            <h1>🚀 실시간 공모전 목록 (위비티)</h1>
            <table>
                <thead>
                    <tr><th>번호</th><th>공모전명</th><th>주최사</th><th>상태</th></tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </body>
    </html>
    """
    return html_content
