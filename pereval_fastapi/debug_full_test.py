import asyncio
import json
from httpx import AsyncClient, ASGITransport
from app.main import app

PAYLOAD_TEMPLATE = {
    "beauty_title": "Перевал Тестовый",
    "title": "Тестовый перевал",
    "other_titles": "Тестовый;Пример",
    "connect": "Точка A - Точка B",
    "add_time": "2024-01-01 12:00:00",
    "user": {"email": "fulltest@example.com", "phone": "+79990001122", "fam": "Петров", "name": "Пётр", "otc": "Петрович"},
    "coords": {"latitude": 46.0, "longitude": 38.0, "height": 1000},
    "level": {"winter": "2A", "summer": "2A", "autumn": "2A", "spring": "2A"},
    "images": [{"title": "Вершина", "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMB/0l7fQAAAABJRU5ErkJggg=="}]
}

async def run():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print('\n-- POST 1')
        r1 = await client.post('/api/v1/submitData', json=PAYLOAD_TEMPLATE)
        print('status', r1.status_code)
        print('body', r1.json())
        id1 = r1.json().get('id')

        print('\n-- POST 2 (same user)')
        payload2 = PAYLOAD_TEMPLATE.copy()
        payload2['title'] = 'Тестовый перевал 2'
        r2 = await client.post('/api/v1/submitData', json=payload2)
        print('status', r2.status_code)
        print('body', r2.json())
        id2 = r2.json().get('id')

        print('\n-- LIST all')
        rl = await client.get('/api/v1/submitData')
        print('status', rl.status_code)
        print('count', len(rl.json()))

        print('\n-- LIST by user email')
        rle = await client.get('/api/v1/submitData', params={'user__email': 'fulltest@example.com'})
        print('status', rle.status_code)
        print('count', len(rle.json()))

        print('\n-- GET by id (id1)')
        rg1 = await client.get(f'/api/v1/submitData/{id1}')
        print('status', rg1.status_code)
        print('body', json.dumps(rg1.json(), ensure_ascii=False)[:1000])

        print('\n-- PATCH attempt: change connect and user.email (user change should be ignored/rejected)')
        patch_payload = {
            'connect': 'Новая связь A-B',
            'user': {'email': 'hacked@example.com'}
        }
        rp = await client.patch(f'/api/v1/submitData/{id1}', json=patch_payload)
        print('status', rp.status_code)
        try:
            print('body', json.dumps(rp.json(), ensure_ascii=False))
        except Exception:
            print('body_text', rp.text)

        print('\n-- PATCH allowed: change connect only')
        patch2 = {'connect': 'Новая связь A-B'}
        rp2 = await client.patch(f'/api/v1/submitData/{id1}', json=patch2)
        print('status', rp2.status_code)
        try:
            print('body', json.dumps(rp2.json(), ensure_ascii=False))
        except Exception:
            print('body_text', rp2.text)

        print('\n-- GET by id after PATCH (check connect/user)')
        rg2 = await client.get(f'/api/v1/submitData/{id1}')
        print('status', rg2.status_code)
        print('body', json.dumps(rg2.json(), ensure_ascii=False)[:1000])

if __name__ == '__main__':
    asyncio.run(run())
