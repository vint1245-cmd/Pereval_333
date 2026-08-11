import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

payload = {
  "beauty_title": "Перевал Безымянный",
  "title": "Безымянный перевал",
  "other_titles": "Перевал Икс;Перевал Y",
  "connect": "г. A - г. B",
  "add_time": "2024-01-01 12:00:00",
  "user": {
    "email": "ivanov@example.com",
    "phone": "+79991234567",
    "fam": "Иванов",
    "name": "Иван",
    "otc": "Иванович"
  },
  "coords": {"latitude": 45.123456, "longitude": 39.123456, "height": 1500},
  "level": {"winter": "1A", "summer": "1A", "autumn": "1A", "spring": "1A"},
  "images": [{"title": "Седловина", "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/0l7fQAAAABJRU5ErkJggg=="}]
}

async def run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post("/api/v1/submitData", json=payload)
        print('STATUS', r.status_code)
        try:
            print(r.json())
        except Exception:
            print(r.text)

if __name__ == '__main__':
    asyncio.run(run())
