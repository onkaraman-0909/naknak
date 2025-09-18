# İş Akışı (Adım Adım) — Temel Öncelikli Sıralama

Bu belgeyi, önce sağlam temeli kuracak şekilde yeniden düzenledim. Önce veri modelleri ve veritabanı, sonra temel işlevler, en son dış servisler ve UI zenginlikleri gelecek.

## 0) Proje İskeleti ve Geliştirme Ortamı
- Ne yapacağız: Minimal backend iskeleti (FastAPI), veritabanı bağlantı ayarı, göç (migration) altyapısı (Alembic), temel test ve config yapısı. Frontend iskeleti daha sonra (temel API’ler hazır olduğunda) kurulacak.
- Sizden gereken: Yerel geliştirme için onaylı Python sürümü ve PostgreSQL erişimi (lokal/container).
- Çıktılar: Çalışan backend iskeleti, `.env.example`, Docker compose (opsiyonel), temel test iskeleti.
- Kabul kriteri: Uygulama health-check endpoint’i çalışır; DB bağlantısı kurulabilir.

## 1) Alan (Domain) Modeli ve Veritabanı Şeması
- Ne yapacağız: User, Organization, OrgUser, Address, Vehicle, Load, Offer (Araç İlanı), Match, Rating, Membership tablolarını tasarlamak; zorunlu alanlar ve doğrulama kurallarını netleştirmek; ER diyagramı ve Alembic migration’ları oluşturmak.
- Sizden gereken: Vergi no uzunluğu/doğrulama, adres alanlarının zorunlulukları, kategori/birim listeleri için onay.
- Çıktılar: PostgreSQL şeması, migration dosyaları, ER diyagramı, örnek (seed) referans verileri.
- Kabul kriteri: Migration ileri/geri sorunsuz; temel CRUD’lar için repository testleri geçer.

## 2) Yetkilendirme Modeli ve Roller
- Ne yapacağız: Roller ve izinler (admin, user, corporate_admin, corporate_user) ve organizasyon-ilişkili sahiplik kuralları; domain seviyesinde kontrol (servis katmanı) hazırlığı.
- Sizden gereken: Kurumsal admin’in yetki kapsamı ve alt kullanıcı sınırları için onay.
- Çıktılar: Rol/izin matrisi, hizmet (service) katmanında kontrol kancaları, birim testler.
- Kabul kriteri: Örnek senaryolarda rol kontrolleri doğru sonuç verir.

## 3) Temel Kimlik Doğrulama (OTP’siz)
- Ne yapacağız: Kayıt, giriş, şifre hash, JWT (access/refresh), oturum sonlandırma. Bu aşamada OTP yok; yalnızca çekirdek kimlik.
- Sizden gereken: Parola politikası (min uzunluk, karmaşıklık) onayı.
- Çıktılar: `/auth/register`, `/auth/login`, `/auth/logout`, `/auth/refresh` API’leri; birim ve entegrasyon testleri.
- Kabul kriteri: Test kullanıcılarıyla giriş/çıkış akışları çalışır; güvenli parola saklama doğrulanır.

## 4) Adres ve Konum Yönetimi (Çekirdek)
- Ne yapacağız: Türkiye il/ilçe/mahalle ve uluslararası ülke/şehir listeleri için dahili (yerel) veri seti ve ID-temelli seçim. Serbest metin yok. Harita/rota entegrasyonu bu aşamada yok.
- Sizden gereken: Kullanılacak veri kaynaklarının onayı ve güncelleme sıklığı.
- Çıktılar: `GET /addresses/...` uçları, tip-ahead (öneri) desteği için API; seed veri yükleme script’leri.
- Kabul kriteri: Zincir seçimleri (il→ilçe→mahalle, ülke→şehir) sorunsuz çalışır.

## 5) Yük (Load) Akışı — Çekirdek
- Ne yapacağız: Yük ilanı oluşturma; isim doğrulaması (marka/özel bilgi sızıntısı engeli), miktar + birim (KG/TON/LİTRE), çıkış günü, alınacak/bırakılacak konum, kategori (Gıda/Tehlikeli…).
- Sizden gereken: Yasaklı/özel kelime listesine örnekler ve birim/kategori listesi onayı.
- Çıktılar: `/loads` CRUD API’leri, isim doğrulama servisi, birim/kategori enum’ları; entegrasyon testleri.
- Kabul kriteri: Kurallara aykırı isimler reddedilir; geçerli verilerle ilan oluşur ve listelenir.

## 6) Araç ve Teklif (Offer) Akışı — Çekirdek
- Ne yapacağız: Araç kaydı (kapasite ve uygunluklar: gıda/tehlikeli), çıkış/varış konumu ve çıkış tarihiyle teklif (offer) oluşturma.
- Sizden gereken: Kapasite birimleri ve lisans/uygunluk seçeneklerinin listesi.
- Çıktılar: `/vehicles` ve `/offers` CRUD API’leri; doğrulama kuralları; entegrasyon testleri.
- Kabul kriteri: Araç ve teklif akışları kural setine uygun kaydedilir ve listelenir.

## 7) Eşleştirme (Matching) — Temel Algoritma
- Ne yapacağız: Zaman, mesafe (adres ID’leri bazlı kabaca), kapasite ve kategori uyumu; ücretli üyelik etkisi olmadan çekirdek sıralama. Rota/harita sağlayıcısı entegrasyonu bu aşamada yapılmaz.
- Sizden gereken: Ağırlıklar için başlangıç parametreleri (mesafe, zaman uyumu, kapasite uyumu).
- Çıktılar: Eşleştirme servisi, `/matches` uçları; senaryo testleri.
- Kabul kriteri: Örnek senaryolarda beklenen eşleşmeler üstte görünür; deterministik sonuçlar alınır.

## 8) Tamamlama, Değişim ve Puanlama — Çekirdek
- Ne yapacağız: Eşleşme kabul/ret/tamamlama akışları; tamamlanan işlemler için 3–4 soruluk, 1–5 puanlı seçmeli anket; profil istatistiklerinin hesaplanması.
- Sizden gereken: Anket soru setinin onayı; istatistiklerde gösterilecek metriklerin listesi.
- Çıktılar: `POST /matches/{id}/accept|reject|complete`, `/ratings`, `/users/{id}/stats` uçları.
- Kabul kriteri: Tamamlanan işlemlerde anket tetiklenir; puanlar ve sayılar doğru görünür.

## 9) Çok Dillilik (i18n) — Temel
- Ne yapacağız: TR ve EN için çeviri dosyaları; backend hata/doğrulama mesajlarının locale desteği. Arapça/Çince daha sonra.
- Sizden gereken: Metinlerin gözden geçirilmesi.
- Çıktılar: `locales/tr.json`, `locales/en.json` ve i18n middleware/yardımcıları.
- Kabul kriteri: Dil değiştirildiğinde API/uyarı mesajları doğru yerelleşir.

## 10) UI/Frontend İskeleti (Temel Ekranlar)
- Ne yapacağız: Giriş/kayıt, yük ilanı formu, araç/teklif formu, eşleştirme listeleri için temel ekranlar. Gelişmiş tasarım ve PWA daha sonra.
- Sizden gereken: Basit ekran taslaklarının onayı.
- Çıktılar: Frontend iskeleti (Next.js önerilir), form ve liste komponentleri; temel i18n entegrasyonu.
- Kabul kriteri: Ana akışlar UI üzerinden uçtan uca çalışır (dış servis yok).

## 11) Dış Servisler — OTP (E-posta/SMS)
- Ne yapacağız: OTP ile e-posta/telefon doğrulama ve şifre sıfırlama entegrasyonu. Sağlayıcı seçimi bu aşamada yapılır.
- Sizden gereken: Sağlayıcı seçimleri ve API anahtarları.
- Çıktılar: `/auth/otp/send`, `/auth/otp/verify`, `/auth/password/forgot|reset` akışları.
- Kabul kriteri: Test ortamında OTP uçtan uca teslim ve doğrulama geçer.

## 12) Dış Servisler — Harita/Rota ve Öneriler
- Ne yapacağız: Seçilen harita sağlayıcısı ile rota/mesafe hesapları; güzergâh üzerindeki ilan önerileri; e-posta/push bildirimleri.
- Sizden gereken: Harita ve bildirim sağlayıcılarının onayı ve anahtarları.
- Çıktılar: Rota tabanlı sıralama iyileştirmeleri, bildirim şablonları ve iş akışları.
- Kabul kriteri: Örnek rotalarda yakın ilanlar önerilir; bildirimler tetiklenir.

## 13) Üyelik ve Sıralama Önceliği
- Ne yapacağız: Free/Pro/Business planları; `priority_score` ile listeleme önceliği.
- Sizden gereken: Plan içerikleri ve fiyat onayı (ödeme entegrasyonu opsiyonel).
- Çıktılar: Üyelik yönetimi uçları ve sıralama algoritmasında öncelik.
- Kabul kriteri: Ücretli üyelik alan kullanıcılar listelerde üst sıralara çıkar.

## 14) PWA ve Mobil Kullanılabilirlik
- Ne yapacağız: Manifest, Service Worker, offline önbellekleme; mobil optimizasyonlar.
- Sizden gereken: Uygulama isim/ikon onayı.
- Çıktılar: PWA kurulabilir uygulama deneyimi.
- Kabul kriteri: Cihazlarda ana ekrana eklenir, temel offline senaryoları çalışır.

## 15) Güvenlik Sertleşmesi ve Uyum
- Ne yapacağız: Rate limit, audit log, anomali tespiti, KVKK/GDPR kontrolleri; bağımsız güvenlik taramaları.
- Sizden gereken: Veri saklama/maskeleme politikası onayı.
- Çıktılar: Güvenlik ayarları ve raporlar.
- Kabul kriteri: Güvenlik testleri ve taramalar hatasız/uygun sonuç verir.

## 16) Testler, İzleme ve CI/CD
- Ne yapacağız: Birim/entegrasyon/e2e test kapsamını genişletme; CI boru hattı; log/izleme (metrics) ayarları.
- Sizden gereken: Staging ortamı/domain (varsa) ve erişimler.
- Çıktılar: Test raporları, otomasyon, temel gözlemleme panoları.
- Kabul kriteri: Ana akışlar yeşil testlerle güvence altında; otomatik dağıtım isteğe bağlı.

---

Notlar
- Her aşama sonunda kısa demo ve onay alınır, değişiklikler bir sonraki sprintte işlenir.
- Dış servis seçimleri (SMS/e-posta/harita) temel akışlar doğrulandıktan sonra yapılır.
- `plan.md` ile uyum korunur; gerektikçe güncellenir.
