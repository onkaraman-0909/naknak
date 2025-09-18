# Nakliye Platformu – Proje Planı

Bu plan, yük gönderen ve araç sahiplerini aynı platformda buluşturan, web ve mobil uyumlu (PWA) çok dilli bir uygulamanın uçtan uca geliştirilmesi için yol haritasını içerir.

## 1) Amaç ve Kapsam
- Kullanıcılar tek bir hesapla hem yük gönderen hem de taşıyıcı rolünde işlem yapabilsin.
- Yük/araç ilanı oluşturma ve bunları konum, tarih, kapasite ve kategori kriterleriyle eşleştirme.
- Çok dilli (TR/EN/ZH/AR) UI, OTP ile e-posta/SMS doğrulama, şifre sıfırlama.
- Ücretli üyelik ile listeleme önceliği, işlem sonu puanlama/anket (yalnızca seçilebilir cevaplar) ve rota üzerinde teklif önerileri.
- Web’den %100 kullanılabilir, aynı kod tabanıyla PWA olarak iOS/Android uyumlu.

## 2) Teknoloji Yığını ve Altyapı
- Backend: Python, FastAPI
- DB: PostgreSQL, göç yönetimi: Alembic
- ORM: SQLAlchemy
- Cache/Queue: Redis (oturum, hız limiti, kısa ömürlü veri), Celery/RQ (asenkron işler: OTP, e-posta/SMS, bildirim)
- Kimlik Doğrulama: JWT (Access/Refresh), OTP (e-posta/SMS)
- Dosya/Medya: S3 uyumlu depolama (örn. AWS S3/MinIO) – opsiyonel
- Bildirim: E-posta (örn. SendGrid/Mailgun), SMS (örn. Twilio/NetGSM/Turkey local)
- i18n: frontend ve backend mesajları için çeviri dosyaları (JSON/po)
- Frontend: React + Vite veya Next.js (SSR/SSG avantajları) + UI Kütüphanesi (MUI/Tailwind)
- Mobil Uyumluluk: PWA (Service Worker, manifest, offline temel kabiliyetler, push bildirimler)
- Harita/Coğrafi: OpenStreetMap + Nominatim/Photon veya Mapbox/Google Maps (rota ve mesafe hesapları)
- Konteyner/DevOps: Docker, docker-compose; CI/CD (GitHub Actions/GitLab CI)

## 3) Mimarî ve Modüller
- API Katmanı: REST (opsiyonel: GraphQL). Sürümleme: `/api/v1`.
- Kimlik ve Yetkilendirme: JWT, rol/izin sistemi (admin, user, corporate_admin, corporate_user).
- Kullanıcı ve Organizasyon: bireysel/kurumsal hesaplar, kurumsalda alt kullanıcı ve yetki devretme.
- Adres/Coğrafi Veri: İl/İlçe/Mahalle + ülke/şehir (yurtdışı) seçenekleri; serbest metin değil.
- İlan Yönetimi:
  - Yük ilanı: isim (denetimli), miktar + birim (KG/TON/LİTRE vb.), çıkış günü, alınacak/bırakılacak konum, kategori (Gıda/Tehlikeli vs.)
  - Araç ilanı: çıkış/varış konumu, çıkış tarihi, kapasite, lisans/uygunluk (Gıda/Tehlikeli taşıyabilir vb.)
- Eşleştirme ve Öneri: rota/koridor bazlı yakınlık, zaman uyumu, kapasite uygunluğu, ücretli üyelik önceliği.
- Puanlama/Anket: işlem sonrası 3-4 soruluk, seçilebilir yanıtlar; ortalama puanların herkese açık görünümü.
- Bildirim: e-posta/SMS ve push; yeni uygun ilan/teklif uyarıları.
- Üyelik/Ödeme: ücretli üyelik planları, faturalama (opsiyonel stripe/iyzico/iyzico-türkiye vb.).
- Admin Paneli: kullanıcı/organizasyon yönetimi, yetki devri, şikayet/uygunsuz içerik moderasyonu, veri sözlüğü yönetimi.

## 4) Veri Modeli (Taslak)
- User: id, email, phone, password_hash, locale, roles[], status, created_at
- Profile: user_id, type (bireysel/kurumsal), name/surname veya title, tax_office, tax_number(10), addresses[]
- Organization: id, title, tax_office, tax_number, address_id, owner_user_id
- OrgUser: org_id, user_id, role(corporate_admin/corporate_user), status
- Address: id, country, admin1(il), admin2(ilçe), admin3(mahalle), line_optional
- Vehicle: id, owner_user_id veya org_id, capacity_value, capacity_unit, can_food, can_dg, licenses[], active
- Load (Yük): id, owner_user_id veya org_id, name, name_validated(bool), quantity_value, quantity_unit, category(enum), pickup_address_id, dropoff_address_id, pickup_day(date), intl(bool)
- TruckOffer (Araç İlanı): id, vehicle_id, from_address_id, to_address_id, depart_date
- Match: id, load_id, truck_offer_id, status (pending/accepted/rejected/completed), price_optional
- Rating: id, rater_user_id, ratee_user_id, match_id, q1..q4 (1-5), overall
- Membership: id, user_id veya org_id, plan, start_at, end_at, priority_score
- OTP: id, user_id, channel(email/sms), code_hash, expires_at, used_at
- AuditLog, Notification, FileUpload (opsiyonel)

Not: `name_validated` ile yük adı marka/özel bilgi sızdırmıyor mu kontrolü yapılır (örn. “DDST marka peynir” reddedilir, “peynir” kabul edilir). Bu kontrol backend’de regex/kelime listesi ile yapılır.

## 5) İş Kuralları ve Akışlar
- Kayıt & Doğrulama:
  - Bireysel veya Kurumsal kayıt; kurumsal için: unvan, vergi dairesi, vergi no(10), adres zorunlu.
  - E-posta ve telefon OTP ile doğrulanır (kayıt anında). Şifre sıfırlamada OTP gereklidir.
  - Bireysel -> Kurumsal geçiş: yeni organizasyon oluşturma ve alt kullanıcı tanımlama.
- Yük Girişi:
  - Sadece isim (kontrollü) ve miktar metin/numara; diğer tüm sahalar seçilebilir.
  - Kategori (Gıda, Tehlikeli, …), birim (KG/TON/LİTRE…), çıkış günü (yalnızca gün), konumlar seçmeli.
  - Yurt dışı için ülke/şehir seçmeli.
- Araç Girişi:
  - Kalkış/varış konumları seçmeli, çıkış tarihi (yalnız tarih), kapasite, lisans/uygunluk seçmeli.
  - Kullanıcı önceden araçlarını profiline kayıt edebilir.
- Eşleştirme & Öneri:
  - Rota üzerinde uygun yük/araç ilanlarını öner; yeni ilanlar e-posta/push ile bildir.
  - Ücretli üyelik alanlara sıralama önceliği.
- Puanlama:
  - İşlem tamamlandıktan sonra 3-4 soru, 1-5 ölçek; metin alanı yok.
  - Toplam puan ve tamamlanan işlem sayıları herkese açık.
- Yetkiler:
  - Kurumsal admin alt kullanıcı ekleyip yetki devredebilir; platform admini de devreye girebilir.

## 6) Çok Dillilik (i18n) ve Yerelleştirme
- Diller: Türkçe, İngilizce, Çince, Arapça. RTL desteği (Arapça) için tema ve yön desteği.
- UI metinleri: `locales/{tr,en,zh,ar}.json`.
- Backend doğrulama ve hata mesajları: locale algılama (Accept-Language/JWT claim) ve çeviri.

## 7) PWA ve Mobil Stratejisi
- Manifest, Service Worker, offline önbellekleme, ikonlar/splash.
- Push bildirimleri (web push) ve iOS uyarlamaları.
- Responsive UI ve dokunma etkileşimleri; harita/konum seçiciler mobil-dostu.

## 8) Güvenlik ve Uyum
- Şifreler: bcrypt/argon2; JWT refresh rotation; cihaz/oturum yönetimi.
- Hız limiti ve brute force koruması (Redis tabanlı rate limit).
- Girdi doğrulama (özellikle yük adı marka/sızdırma kontrolü), dosya yükleme güvenliği.
- Log/Audit ve saklama politikaları (KVKK/GDPR farkındalığı), kişisel verilerin maskelemesi.

## 9) Adres ve Konum Veri Seti
- TR için İl/İlçe/Mahalle sabit veri seti (güncel kaynak veya resmi veri). Yabancı ülke/şehir listesi.
- API uçları: arama/öneri (typeahead), yalnızca seçilebilir id’ler; serbest metin yok.
- Rota/mesafe hesapları: harita sağlayıcısı.

## 10) Bildirim Sistemi
- Olay Tetikleyicileri: kayıt/OTP, yeni uygun ilan, teklif eşleşmesi, durum değişiklikleri, şifre sıfırlama.
- Kanallar: e-posta, SMS, push. Kullanıcı tercihlerine göre opt-in/out.

## 11) Ücretli Üyelik ve Sıralama
- Planlar: Free, Pro, Business (taslak). Pro/Business: daha yüksek listeleme önceliği, daha fazla ilan/pinlenmiş ilan.
- Sıralama: `priority_score` + tazelik + mesafe + eşleşme skoru.

## 12) Yol Haritası (Önerilen Sprintler)
- Sprint 0: Proje iskeleti, temel bağımlılıklar, Docker, CI
- Sprint 1: Kimlik & OTP, e-posta/SMS entegrasyonu, i18n temel
- Sprint 2: Adres/konum veri seti ve seçim bileşenleri, harita entegrasyonu
- Sprint 3: Yük ilanı akışı + doğrulama kuralları
- Sprint 4: Araç ilanı akışı + kapasite/lisans
- Sprint 5: Eşleştirme motoru (temel), bildirimler
- Sprint 6: Puanlama/anket, kamuya açık profil/istatistikler
- Sprint 7: Üyelik/monetizasyon ve önceliklendirme
- Sprint 8: Admin paneli, denetimler, raporlama
- Sprint 9: PWA iyileştirmeleri, performans, güvenlik sertleşmesi, load test
- Sprint 10: Beta yayını, geri bildirim, düzeltmeler

## 13) Başlıca API Uçları (Taslak)
- Auth: `POST /auth/register`, `POST /auth/login`, `POST /auth/otp/send`, `POST /auth/otp/verify`, `POST /auth/password/forgot`, `POST /auth/password/reset`
- Users/Orgs: `GET/PUT /me`, `POST /orgs`, `POST /orgs/{id}/users`, `POST /orgs/{id}/transfer-admin`
- Address: `GET /addresses/search`, `GET /countries`, `GET /tr/il`, `GET /tr/il/{id}/ilce`, `GET /tr/ilce/{id}/mahalle`
- Loads: `POST /loads`, `GET /loads`, `GET /loads/{id}`, `POST /loads/{id}/validate-name`
- Vehicles/Offers: `POST /vehicles`, `POST /offers`, `GET /offers`
- Matching: `POST /match`, `GET /matches`, `POST /matches/{id}/accept`, `POST /matches/{id}/complete`
- Ratings: `POST /ratings`, `GET /users/{id}/ratings`, `GET /users/{id}/stats`
- Membership: `POST /membership/subscribe`, `GET /membership`
- Notifications: `GET /notifications`, `POST /notifications/subscribe`

## 14) Test, Kalite ve CI/CD
- Test: unit (service/validator), integration (DB/Repo), e2e (API ve UI), sözleşme testleri.
- Kalite: lint/format, type checking (mypy/pyright), security scans (Bandit, dep check).
- CI: PR tetikli otomatik test, build, container image, staging deploy.

## 15) Ölçeklenebilirlik ve Performans
- Okuma-yoğun uçlar için cache. Sorgu optimizasyonu (indexler), N+1 önleme.
- Asenkron işlemler (OTP/bildirim/eşleştirme önerileri) kuyrukta.
- Yatay ölçeklenebilir API ve işçi süreçleri; stateless podlar.

## 16) Riskler ve Önlemler
- SMS/e-posta sağlayıcı bağımlılığı: en az iki tedarikçi için soyutlama katmanı.
- Coğrafi veri güncelliği: veri güncelleme iş akışları.
- Marka/özel bilgi sızması: isim doğrulama kurallarının sürekli güncellenmesi.
- Kötüye kullanım: hız limiti, anomali tespiti, şikayet/ban mekanizması.

## 17) Kararlar ve Onay Noktaları
- Harita sağlayıcısı seçimi (OSM/Mapbox/Google) – ONAY GEREKİR
- SMS/E-posta sağlayıcıları (yerel maliyet/teslimat kalitesi) – ONAY GEREKİR
- Üyelik planları ve fiyatlandırma – ONAY GEREKİR
- Frontend framework (Next.js öneri) – ONAY GEREKİR

## 18) İlk Uygulama Hedefi (MVP Tanımı)
- Kayıt/giriş + OTP doğrulama + şifre sıfırlama
- TR adres seçimleri + basit harita
- Yük ve araç ilanı oluşturma (validasyonlar dahil)
- Basit eşleştirme listeleri + e-posta bildirimi
- Puanlama akışı (seçilebilir sorular)
- Çok dillilik: TR + EN

---

Onayınızla bir sonraki adımda proje iskeletini (backend/frontend, Docker, temel bağımlılıklar) kuracağım ve veri modeli ayrıntılarını finalize edeceğim.
