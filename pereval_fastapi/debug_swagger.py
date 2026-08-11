import asyncio
import json
from httpx import AsyncClient, ASGITransport
from app.main import app

async def run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # GET /docs (HTML)
        r_docs = await client.get("/docs")
        print('docs_status', r_docs.status_code)
        print('docs_snippet', r_docs.text[:200])

        # GET OpenAPI JSON
        r_open = await client.get("/openapi.json")
        print('openapi_status', r_open.status_code)
        openapi = r_open.json()
        # Check path presence
        paths = list(openapi.get('paths', {}).keys())
        submit_path = '/api/v1/submitData'
        print('submit_path_exists', submit_path in paths)
        if submit_path in paths:
            print('submit_path_methods', list(openapi['paths'][submit_path].keys()))
            print('submit_path_schema_snippet')
            print(json.dumps(openapi['paths'][submit_path], indent=2)[:800])

        # perform POST (valid base64 1x1 png)
        payload = {
            "beauty_title": "Перевал Безымянный",
            "title": "Безымянный перевал",
            "other_titles": "Перевал Икс;Перевал Y",
            "connect": "г. A - г. B",
            "add_time": "2024-01-01 12:00:00",
            "user": {"email": "swagger_test@example.com", "phone": "+79991234567", "fam": "Иванов", "name": "Иван", "otc": "Иванович"},
            "coords": {"latitude": 45.123456, "longitude": 39.123456, "height": 1500},
            "level": {"winter": "1A", "summer": "1A", "autumn": "1A", "spring": "1A"},
            "images": [{"title": "Седловина", "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/0l7fQAAAABJRU5ErkJggg=="}]
        }
        r_post = await client.post(submit_path, json=payload)
        print('post_status', r_post.status_code)
        try:
            print('post_json', json.dumps(r_post.json(), indent=2, ensure_ascii=False))
        except Exception:
            print('post_text', r_post.text)
            return

        # GET by id if created
        j = r_post.json()
        created_id = j.get('id')
        if created_id:
            r_get = await client.get(f"/api/v1/submitData/{created_id}")
            print('get_status', r_get.status_code)
            try:
                print('get_json', json.dumps(r_get.json(), indent=2, ensure_ascii=False)[:1000])
            except Exception:
                print('get_text', r_get.text)

if __name__ == '__main__':
    asyncio.run(run())
