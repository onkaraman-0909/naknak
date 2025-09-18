# F4ST — Backend API
## Docker ile Çalıştırma

Yerelde Docker imajı oluşturma:
```
docker build -t nakliye-api .
```

Konteyneri çalıştırma (host 8000 → container 8000):
```
docker run --rm -p 8000:8000 --env-file .env nakliye-api
```

Sağlık kontrolü ve dokümantasyon:
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/docs

## Docker Compose

Tüm sistemi tek komutla başlat (Postgres + API):
```
docker compose up --build
```

Testleri container içinde çalıştırmak için (compose):
```
docker compose run --rm tests
```

Notlar:
- Compose ortamında API `DATABASE_URL` içinde `db` servisini host olarak kullanır: `postgresql+psycopg://postgres:postgres@db:5432/nakliye`.
- `.env` dosyası konteynere read-only mount edilir; gizli değerleri depoya koymayın.


## Ortam Değişkenleri (.env)

Aşağıdaki anahtarlar `app/config.py` içinde okunur ve uygulamada kullanılır.

- `ENV`:
  - Değerler: `local`, `staging`, `prod`
  - OpenAPI `servers` sıralamasını belirler.
- `DATABASE_URL`:
  - Örnek: `postgresql+psycopg://postgres:postgres@localhost:5432/nakliye`
- `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_MINUTES`
- `PROD_API_URL`, `STAGING_API_URL`, `LOCAL_API_URL`:
  - OpenAPI `servers` bölümüne dinamik olarak eklenir (bkz. `app/main.py -> custom_openapi`).

Örnek dosya: `.env.example`


## Listeleme — Sayfalama ve Filtreleme

Liste uç noktalarında basit sayfalama ve (uygunsa) filtre desteği bulunur. Aşağıdaki örneklerde Bearer access token ile yetkili olduğun varsayılır.

- `GET /orgs/`
  - Sorgu parametreleri: `limit`, `offset`
  - Örnek:
    ```http
    GET /orgs/?limit=10&offset=20
    Authorization: Bearer <ACCESS_TOKEN>
    ```

- `GET /vehicles/`
  - Sorgu parametreleri: `organization_id`, `limit`, `offset`
  - Örnekler:
    ```http
    # Sadece belirli organizasyona ait araçlar
    GET /vehicles/?organization_id=3
    Authorization: Bearer <ACCESS_TOKEN>

    # Sadece ilk kaydı al
    GET /vehicles/?limit=1
    Authorization: Bearer <ACCESS_TOKEN>
    ```

- `GET /loads/`
  - Sorgu parametreleri: `organization_id`, `limit`, `offset`
  - Örnekler:
    ```http
    GET /loads/?organization_id=5&limit=5&offset=5
    Authorization: Bearer <ACCESS_TOKEN>
    ```

Notlar
- `limit` ve `offset` sıfırdan büyük sayılar olmalıdır.
- `organization_id` belirtilirse, ilgili organizasyon için RBAC kuralları geçerlidir; admin olmayanlar yetkisizse 403 dönebilir.


![CI](https://img.shields.io/github/actions/workflow/status/onkaraman-0909/naknak/ci.yml?branch=main)
[![codecov](https://codecov.io/gh/onkaraman-0909/naknak/branch/main/graph/badge.svg)](https://codecov.io/gh/onkaraman-0909/naknak)

Not: Rozetler `onkaraman-0909/naknak` deposuna göre yapılandırıldı.

## Hızlı Başlangıç

1) Python ortamını hazırlayın ve bağımlılıkları yükleyin:
```
pip install -r requirements.txt
```

2) Ortam değişkenlerini ayarlayın:
- `.env.example` dosyasını kopyalayıp `.env` olarak düzenleyin:
```
copy .env.example .env
```
- `DATABASE_URL` değerini kendi PostgreSQL bilgilerinizle güncelleyin.

3) Uygulamayı çalıştırın:
```
uvicorn app.main:app --reload
```
- Sağlık kontrolü: http://127.0.0.1:8000/health

4) Alembic migration (ileride modeller eklendikten sonra):
```
alembic revision -m "init"
alembic upgrade head
```

Notlar:
- PostgreSQL sürücüsü psycopg3 kullanır: bağlantı dizesi `postgresql+psycopg://...`
- Alembic `.ini` içindeki `sqlalchemy.url` değeri `.env` içindeki `DATABASE_URL` ile override edilebilir.

## Testler

Yerelde test çalıştırma:
```
pytest -q
```

Coverage (yerel):
```
pytest -q --cov=app --cov-report=term-missing --cov-report=xml
```
`coverage.xml` CI tarafından artifact olarak yüklenecek şekilde yapılandırılmıştır.

## CI (GitHub Actions)

- Dosya: `.github/workflows/ci.yml`
- Python 3.12 ve 3.13 için matris
- PostgreSQL 16 servisi başlatılır ve hazır olunca:
  - `alembic upgrade head`
  - `pytest` (coverage ile)
- `coverage.xml` artifact olarak yüklenir
