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
        
        results = []
        # 데이터가 없거나 차단된 경우 샘플 데이터 반환
        if not items or len(items) <= 1:
            return [{"title": "샘플: 2026 자율주행 경진대회", "host": "산업부", "status": "접수중"}] * 10

        for item in items[:15]:
            title_tag = item.select_one('.tit a')
            if not title_tag: continue
            results.append({
                "title": title_tag.text.strip(),
                "host": item.select_one('.organ').text.strip() if item.select_one('.organ') else "주최사미상",
                "status": item.select_one('.status').text.strip() if item.select_one('.status') else "진행중"
            })
        return results
    except Exception:
        return [{"title": "데이터 로딩 중", "host": "-", "status": "-"}]

@app.get("/", response_class=HTMLResponse)
async def read_root():
    data = get_wevity_data()
    
    # HTML 코드를 직접 변수에 담음 (파일 에러 방지)
    rows = ""
    for idx, c in enumerate(data, 1):
        rows += f"<tr><td>{idx}</td><td>{c['title']}</td><td>{c['host']}</td><td>{c['status']}</td></tr>"

    html_content = f"""
    <html>
        <head>
            <title>공모전 크롤러</title>
            <style>
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f4f4f4; }}
                h1 {{ color: #333; }}
            </style>
        </head>
        <body>
            <h1>🚀 최신 공모전 목록 (위비티)</h1>
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
