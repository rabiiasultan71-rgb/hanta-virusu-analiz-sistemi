import sqlite3
import pandas as pd
import os

def veritabanini_ml_ve_rehber_icin_hazirla():
    # app.py ile ortak nihai veritabanı ismi
    conn = sqlite3.connect("hanta_sistemi_nihai.db")
    cursor = conn.cursor()
    print("[+] hanta_sistemi_nihai.db bağlantısı kuruldu.")

    # 1. TEDAVİ VE GENİŞLETİLMİŞ UZAKLAŞTIRMA REHBERİ TABLOSU
    cursor.execute("DROP TABLE IF EXISTS tedavi_rehberi")
    cursor.execute("""
    CREATE TABLE tedavi_rehberi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        kategori TEXT,
        baslik TEXT,
        aciklama TEXT,
        kritik_uyari TEXT
    )
    """)

    rehber_verileri = [
        # --- 💊 DOKTOR KONTROLÜNDE ALINABİLECEK İLAÇLAR ---
        ('Tıbbi İlaç', 'Geniş Spektrumlu Antiviral Ribavirin Protokolü', 
         'Hanta virüsünün neden olduğu viral replikasyonu ve organ hasarını minimalize etmek adına, semptomların ilk 4 gününde hekim kararıyla damardan (IV) Ribavirin infüzyonu uygulanır.', 
         '🚨 REÇETE UYARISI: Bu ilaç sadece hastane yatışı verilmiş hastalarda, enfeksiyon adenocarcinoma hastalıkları uzmanı gözetiminde protokol dahilinde açılır. Evde kullanımı yasaktır.'),
        
        ('Tıbbi İlaç', 'İmmün Supresif ve Kortikosteroid Desteği', 
         'Akciğer Sendromu (HPS) evresinde bağışıklık sisteminin akciğer çeperlerine verdiği zararı (Sitokin fırtınasını) engellemek amacıyla hekim kontrolünde kortikosteroid türevleri uygulanabilmektedir.', 
         '⚠️ KLİNİK NOT: Ventilasyon (solunum cihazı) desteği alan hastalarda sıvı-elektrolit takibiyle beraber yoğun bakım hekimlerince yönetilir.'),
        
        ('Tıbbi İlaç', 'Selektif Analjezik Rezistans Yönetimi', 
         'Hastalığın erken evresindeki kırıcı baş ve kas ağrılarında, böbrek filtrasyonunu zedelemeyen parasetamol bazlı hekim onaylı ağrı kesiciler tercih edilmektedir.', 
         '❌ ÖLÜMCÜL RİSK: Aspirin ve türevi non-steroid ilaçlar kanama eğilimini (koagülopati) tetiklediği için kesinlikle yasaktır.'),

        # --- 🌿 İLAÇSIZ ÖNERİLER VE ÇEŞİTLENDİRİLMİŞ UZAKLAŞTIRMA YOLLARI ---
        ('Alternatif Yol', 'Aromatik Esansiyel Yağ Bariyeri (Nane & Kekik & Okaliptüs)', 
         'Farelerin koku reseptörleri mentol, karvakrol ve sineol gibi keskin moleküllere karşı yüksek kaçınma reaksiyonu gösterir. Kiler, depo ve kör noktalara bu yağların damlatılması doğal bir uzaklaştırma kalkanı sağlar.', 
         '💡 UYGULAMA: Saf nane ve okaliptüs yağını pamuklara emdirerek farelerin geçebileceği çatlak ve kapı altı boşluklarına yerleştirin, haftalık tazeleyin.'),
        
        ('Alternatif Yol', 'Yüksek Frekanslı Ultrasonik Dalga Bariyerleri (Mekanik Koruma)', 
         'Zehir veya kimyasal kullanmadan kemirgenleri ortamdan uzaklaştırmak için, 20 kHz üzeri değişken ultrasonik frekans yayan cihazlar kullanılarak taşıyıcıların yaşam alanlarına yuvalanması engellenir.', 
         '💡 AVANTAJI: İnsan ve evcil hayvan sağlığına hiçbir zararı ve kimyasal yan etkisi yoktur, mekanik bir savunma yöntemidir.'),
        
        ('Alternatif Yol', 'Islatılmış Dezenfeksiyon/Temizlik Protokolü (Aerosol Engelleme)', 
         'Virüs, kurumuş fare dışkılarının süpürülürken havaya karışmasıyla (aerosol) bulaşır. Bu yüzden eski depo veya tavan araları temizlenirken asla kuru süpürge vurulmamalıdır. Ortam %10 çamaşır sulu çözeltiyle ıslatılmalı, toz kalkması önlenmeli ve silinmelidir.', 
         '🛡️ MASKELİ SAVUNMA: Temizlik esnasında aerosollerden korunmak için kesinlikle tam korumalı N95 (FFP3) tıbbi maske ve su geçirmez eldiven kullanılmalıdır.')
    ]

    cursor.executemany("INSERT INTO tedavi_rehberi (kategori, baslik, aciklama, kritik_uyari) VALUES (?, ?, ?, ?)", rehber_verileri)
    
    # 2. GEÇMİŞ ANALİZ KAYITLARI TABLOSU (🌟 YENİ TABLO)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analiz_gecmisi (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarih TEXT,
        kullanici_turu TEXT,
        yas INTEGER,
        risk_skoru REAL,
        risk_durumu TEXT,
        detaylar TEXT
    )
    """)
    
    conn.commit()
    conn.close()
    print("[+] Klinik rehber ve Geçmiş Kayıt veritabanı başarıyla hazırlandı.")

if __name__ == "__main__":
    veritabanini_ml_ve_rehber_icin_hazirla()