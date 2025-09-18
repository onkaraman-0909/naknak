# Nakliye Platformu — Backend Başlangıç

![CI](https://img.shields.io/github/actions/workflow/status/OWNER/REPO/ci.yml?branch=main)
[![codecov](https://codecov.io/gh/OWNER/REPO/branch/main/graph/badge.svg)](https://codecov.io/gh/OWNER/REPO)

Not: Üstteki rozetin doğru çalışması için `OWNER/REPO` kısmını kendi GitHub depo yolunuzla değiştirin (örn. `onkar/nakliye-backend`).

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

