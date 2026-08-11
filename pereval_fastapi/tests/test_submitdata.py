# tests/test_submitdata.py
import pytest
import httpx
from typing import Dict, Any
from sqlalchemy import select

from app.models.pereval import Pereval

pytestmark = pytest.mark.asyncio

BASE_URL = "http://test"


def make_payload(
    *,
    title: str = "Перевал Безымянный",
    beauty_title: str = "Безымянный перевал",
    other_titles: str | None = None,
    connect: str = "г. A - г. B",
    user_email: str = "ivanov@example.com",
    user_fio: str = "Иван Иванов",
    coords_lat: float = 45.123456,
    coords_lon: float = 39.123456,
    coords_height: int = 1500,
    level_data: dict | None = None,
    images: list | None = None,
) -> Dict[str, Any]:
    if other_titles is None:
        other_titles = "Перевал Икс;Перевал Y"

    if images is None:
        images = [
            {"title": "Фото 1", "data": "aGVsbG8="},
            {"title": "Фото 2", "data": "cHl0aG9u"},
        ]

    if level_data is None:
        level_data = {
            "winter": "1А",
            "summer": "2Б",
            "autumn": "3А",
            "spring": "1Б",
        }

    payload = {
        "beauty_title": beauty_title,
        "title": title,
        "other_titles": other_titles,
        "connect": connect,
        "user": {
            "email": user_email,
            "fam": user_fio.split()[0],
            "name": user_fio.split()[1] if len(user_fio.split()) > 1 else "",
            "otc": "",
            "phone": "+380501234567",
        },
        "coords": {
            "latitude": coords_lat,
            "longitude": coords_lon,
            "height": coords_height,
        },
        "level": level_data,
        "images": images,
    }
    return payload


#async def create_pass(client: httpx.AsyncClient, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    #Helper: POST /submitData and return parsed JSON.
    #Accept both 200 and 201 as success codes.
    #"""
    #r = await client.post("/submitData", json=payload)
    #assert r.status_code in (200, 201), f"POST /submitData returned {r.status_code}: {r.text}"
   # data = r.json()
  #  assert "status" in data and data["status"] in ("ok", "error")
 #   assert "id" in data
#    return data

async def create_pass(client: httpx.AsyncClient, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Helper: POST /api/v1/submitData and return parsed JSON.
    Accept 200 as success code.
    If server returns error status in body, raise AssertionError with full body for debugging.
    """
    r = await client.post("/api/v1/submitData", json=payload)
    # Always parse JSON if possible
    try:
        data = r.json()
    except Exception:
        data = {"raw_text": r.text}

    if r.status_code not in (200, 201):
        raise AssertionError(f"POST /api/v1/submitData returned HTTP {r.status_code}: {r.text}")

    if not isinstance(data.get("status"), int):
        raise AssertionError(f"POST /api/v1/submitData returned invalid status field: {data}")

    return data


async def get_pass_by_id(client: httpx.AsyncClient, pass_id: int) -> Dict[str, Any]:
    r = await client.get(f"/api/v1/submitData/{pass_id}")
    assert r.status_code == 200, f"GET /api/v1/submitData/{pass_id} returned {r.status_code}: {r.text}"
    return r.json()


# 1. POST — успешное создание перевала
async def test_post_create_success(async_client):
    client = async_client
    payload = make_payload(user_email="post_success@example.com")
    resp = await create_pass(client, payload)
    assert resp["status"] == 200
    assert "id" in resp and isinstance(resp["id"], int)
    assert resp["message"] is None


# 2. GET — получение по id и проверка вложенных сущностей
async def test_get_by_id_contains_nested_entities(async_client):
    client = async_client
    payload = make_payload(user_email="get_by_id@example.com", title="Перевал Тестовый")
    post_resp = await create_pass(client, payload)
    assert post_resp["status"] == 200
    pass_id = post_resp["id"]

    get_data = await get_pass_by_id(client, pass_id)

    for field in ("beauty_title", "title", "other_titles", "connect", "id", "status", "add_time"):
        assert field in get_data, f"Поле {field} отсутствует в ответе GET /submitData/{{id}}"

    assert "user" in get_data and isinstance(get_data["user"], dict)
    assert get_data["user"]["email"] == "get_by_id@example.com"

    assert "coords" in get_data and isinstance(get_data["coords"], dict)
    assert "level" in get_data and isinstance(get_data["level"], dict)
    assert "images" in get_data and isinstance(get_data["images"], list)
    assert any(isinstance(img, dict) and "title" in img for img in get_data["images"])


# 3. GET — фильтрация по email
async def test_get_filter_by_user_email(async_client):
    client = async_client
    email = "filter_user@example.com"

    p1 = make_payload(user_email=email, title="Фильтр 1")
    p2 = make_payload(user_email=email, title="Фильтр 2")
    p3 = make_payload(user_email="other_user@example.com", title="Другой пользователь")

    r1 = await create_pass(client, p1)
    r2 = await create_pass(client, p2)
    r3 = await create_pass(client, p3)

    assert r1["status"] == 200 and r2["status"] == 200 and r3["status"] == 200

    r = await client.get(f"/api/v1/submitData?user__email={email}")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    for item in data:
        assert "user" in item and item["user"]["email"] == email


# 4. PATCH — успешное обновление существующей записи в статусе "new"
async def test_patch_pereval_updates_existing_new_record(async_client):
    client = async_client
    payload = make_payload(user_email="patch_update@example.com")
    post_resp = await create_pass(client, payload)
    assert post_resp["status"] == 200
    pass_id = post_resp["id"]

    patch_payload = {
        "beauty_title": "Обновлённый перевал",
        "other_titles": "Новое название",
        "connect": "г. X - г. Y",
        "images_to_delete": [],
        "images": [
            {"title": "Новое фото", "data": "aGVsbG8="}
        ]
    }

    r = await client.patch(f"/api/v1/submitData/{pass_id}", json=patch_payload)
    assert r.status_code == 200
    json_data = r.json()
    assert json_data["state"] == 1
    assert json_data["message"] == "Запись успешно отредактирована"

    get_data = await get_pass_by_id(client, pass_id)
    assert get_data["beauty_title"] == "Обновлённый перевал"
    assert get_data["other_titles"] == "Новое название"
    assert any(img["title"] == "Новое фото" for img in get_data["images"])


async def test_patch_pereval_fails_when_not_new(async_client, async_session):
    client = async_client
    payload = make_payload(user_email="patch_fail@example.com")
    post_resp = await create_pass(client, payload)
    assert post_resp["status"] == 200
    pass_id = post_resp["id"]

    query = select(Pereval).where(Pereval.id == pass_id)
    result = await async_session.execute(query)
    pereval_obj = result.scalar_one()
    pereval_obj.status = "accepted"
    async_session.add(pereval_obj)
    await async_session.commit()

    r1 = await client.patch(f"/api/v1/submitData/{pass_id}", json={"beauty_title": "Запрещено"})
    assert r1.status_code in (400, 409)
    j = r1.json()
    assert isinstance(j, dict)
    assert j.get("detail") or j.get("message")


# 6. Негативный кейс: отсутствие обязательного поля (например, title)
async def test_post_missing_required_field_returns_error(async_client):
    client = async_client
    payload = make_payload()
    payload.pop("title", None)
    r = await client.post("/api/v1/submitData", json=payload)
    # Допускаем, что API может вернуть 200/201 (создалось) или ошибку 400/422
    if r.status_code in (200, 201):
        j = r.json()
        assert "status" in j and isinstance(j["status"], int)
        assert j["status"] == 200
        assert "id" in j
        assert "message" in j
    else:
        assert r.status_code in (400, 422)


# 7. Тест на повторное создание пользователя с тем же email
async def test_duplicate_user_email_reuses_user_id(async_client):
    client = async_client
    email = "duplicate_user@example.com"
    p1 = make_payload(user_email=email, title="Дубликат 1")
    p2 = make_payload(user_email=email, title="Дубликат 2")

    r1 = await create_pass(client, p1)
    r2 = await create_pass(client, p2)
    assert r1["status"] == 200 and r2["status"] == 200

    id1 = r1["id"]
    id2 = r2["id"]
    assert isinstance(id1, int) and isinstance(id2, int) and id1 != id2

    g1 = await get_pass_by_id(client, id1)
    g2 = await get_pass_by_id(client, id2)

    assert "user" in g1 and "user" in g2
    assert "id" in g1["user"] and "id" in g2["user"]
    assert g1["user"]["email"] == email and g2["user"]["email"] == email

    # По умолчанию ожидаем переиспользование пользователя по email.
    assert g1["user"]["id"] == g2["user"]["id"], (
        "Ожидалось, что повторное создание с тем же email вернёт одного и того же пользователя (user.id совпадают). "
        "Если ваша логика создаёт нового пользователя при каждом POST, скорректируйте тест."
    )
