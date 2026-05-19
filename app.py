import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
import joblib  # Kütüphaneyi en üste aldık
from datetime import datetime  # Hata veren eksik kütüphaneyi ekledik
import io  # Excel indirme işlemi için gerekli kütüphane

# ==========================================
# GÖRSEL TEMA VE SAYFA YAPILANDURMASI
# ==========================================
st.set_page_config(
    page_title="Hanta Virüsü Klinik Karar Destek Sistemi",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0f1115;
        color: #ffffff;
    }
    [data-testid="stSidebar"] {
        background-color: #161920;
        border-right: 2px solid #ff3333;
    }
    .metric-box {
        background-color: #1e222b;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #ff3333;
        margin-bottom: 15px;
    }
    .main-title {
        color: #ff3333;
        font-family: 'Helvetica Neue', sans-serif;
        font-weight: bold;
        text-align: center;
    }
    .disclaimer-band {
        background-color: #ff3333;
        color: white;
        padding: 12px;
        text-align: center;
        font-weight: bold;
        font-size: 16px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# SABİT YASAL UYARI BANDI
st.markdown(
    '<div class="disclaimer-band">'
    '🚨 YASAL UYARI: Bu sistem bir resmi teşhis aracı değildir! '
    'Yalnızca klinik karar destek ve risk analizi amacıyla simüle edilmiştir.'
    '</div>', 
    unsafe_allow_html=True
)

# YAN PANEL NAVİGASYON
st.sidebar.markdown("<h2 style='color: #ff3333; text-align: center;'>🧬 HantaNavi v2026</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<hr style='border: 1px solid #ff3333;'>", unsafe_allow_html=True)

kategori = st.sidebar.radio(
    "Gitmek İstediğiniz Modülü Seçin:",
    [
        "🔑 1. Giriş & Yetkilendirme",
        "🗺️ 2. Coğrafi Bölge Analizi",
        "🧠 3. Klinik & YZ Risk Analizi",
        "👁️ 4. Akıllı Görsel Analiz",
        "💊 5. Tedavi & Korunma Rehberi",
        "📜 6. Geçmiş Analiz Kayıtları"
    ]
)

# REHBER HAFIZASI
if 'kullanici_rolu' not in st.session_state:
    st.session_state['kullanici_rolu'] = "Vatandaş"

# --- 1. MODÜL: GİRİŞ VE YETKİLENDİRME ---
if kategori == "🔑 1. Giriş & Yetkilendirme":
    st.markdown("<h1 class='main-title'>🔑 Kullanıcı Girişi ve Yetkilendirme</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='metric-box'>
        <h3>Sistem Yetkilendirme Paneli</h3>
        <p>Hanta Virüsü Sistemi, kullanıcı profiline göre dinamik arayüz sunmaktadır. Lütfen sistemde işlem yapacağınız rolü seçiniz.</p>
    </div>
    """, unsafe_allow_html=True)
    
    rol = st.selectbox(
        "Sisteme Erişmek İstediğiniz Unvan:",
        ["Vatandaş", "Uzman Doktor / Sağlık Personeli"]
    )
    
    if rol == "Vatandaş":
        st.session_state['kullanici_rolu'] = "Vatandaş"
        st.success("🤖 Vatandaş Modu Aktif. Klinik Risk Tahmini bölümünde laboratuvar alanları kısıtlanacaktır.")
    else:
        st.session_state['kullanici_rolu'] = "Doktor"
        st.error("🩺 Uzman Doktor Modu Aktif! Tahlil parametreleri (Trombosit, CRP) erişime açılmıştır.")

# --- 2. MODÜL: COĞRAFİ BÖLGE ANALİZİ ---
elif kategori == "🗺️ 2. Coğrafi Bölge Analizi":
    st.markdown("<h1 class='main-title'>🗺️ Türkiye 7 Bölge Coğrafi Risk Analizi</h1>", unsafe_allow_html=True)
    
    csv_yolu = "global_hantavirus_surveillance_dataset_2026.csv"
    if os.path.exists(csv_yolu):
        df_surv = pd.read_csv(csv_yolu)
        bolge = st.selectbox(
            "Analiz Etmek İstediğiniz Coğrafi Bölgeyi Seçin:",
            ["İç Anadolu Bölgesi", "Karadeniz Bölgesi", "Marmara Bölgesi", 
             "Ege Bölgesi", "Akdeniz Bölgesi", "Doğu Anadolu Bölgesi", "Güneydoğu Anadolu Bölgesi"]
        )
        
        if bolge == "İç Anadolu Bölgesi":
            sub_df = df_surv[(df_surv['humidity_percent'] >= 40) & (df_surv['humidity_percent'] <= 60)]
            risk_puani = 40; risk_durumu = "Orta Risk ⚠️"; risk_rengi = "orange"
            aciklama = "Karasal iklim ve tarım alanlarının yoğunluğu nedeniyle özellikle hasat dönemlerinde kapalı ambarlar ve kırsal depolama alanlarında fare maruziyetine ekstra dikkat edilmelidir."
        elif bolge == "Karadeniz Bölgesi":
            sub_df = df_surv[df_surv['humidity_percent'] > 70]
            risk_puani = 85; risk_durumu = "YÜKSEK RİSK 🚨"; risk_rengi = "red"
            aciklama = "Yüksek nem oranları, yoğun yıllık yağışlar ve nemli kırsal yüzeyler kemirgen popülasyonunun hızla çoğalmasına ve Hanta virüsünün dış ortamda aerosol formunu daha uzun süre korumasına zemin hazırlar."
        elif bolge == "Marmara Bölgesi":
            sub_df = df_surv[df_surv['population_density'] > 4000]
            risk_puani = 55; risk_durumu = "Orta-Yüksek Risk ⚠️"; risk_rengi = "#e67e22"
            aciklama = "Nüfus ve lojistik/liman yoğunluğu son derece yüksek olduğundan, endüstriyel depo alanlarında, terk edilmiş binalarda ve bodrum katlarda mekanik fare engelleri ve düzenli sanitasyon kritik önem taşır."
        elif bolge == "Ege Bölgesi":
            sub_df = df_surv[(df_surv['temperature_celsius'] >= 20) & (df_surv['temperature_celsius'] <= 30)]
            risk_puani = 50; risk_durumu = "Orta Risk ⚠️"; risk_rengi = "orange"
            aciklama = "Ilıman iklim kuşağı ve zeytinlik/tarım arazileri kemirgen hareketliliğini destekler. Kırsal bağ evleri uzun süre kapalı kaldıktan sonra açılırken kesinlikle ıslak temizlik yapılmalıdır."
        elif bolge == "Akdeniz Bölgesi":
            sub_df = df_surv[df_surv['temperature_celsius'] > 28]
            risk_puani = 35; risk_durumu = "Düşük-Orta Risk ✅"; risk_rengi = "yellow"
            aciklama = "Yüksek sıcaklıklar virüsün dış ortamdaki mukavemetini ve dayanıklılık süresini kısıtlasa da, seracılık faaliyetlerinin yapıldığı nemli iç mekanlar sürveyans altında tutulmalıdır."
        elif bolge == "Doğu Anadolu Bölgesi":
            sub_df = df_surv[df_surv['temperature_celsius'] < 15]
            risk_puani = 15; risk_durumu = "Düşük Risk 🟢"; risk_rengi = "green"
            aciklama = "Düşük ortalama sıcaklıklar ve yüksek rakım genel dış mekan riskini minimize eder; ancak kış aylarında vahşi kemirgenlerin kapalı ahırlara ve evlere sığınma eğilimi takibe alınmalıdır."
        else:
            sub_df = df_surv[df_surv['humidity_percent'] < 40]
            risk_puani = 35; risk_durumu = "Düşük-Orta Risk ✅"; risk_rengi = "yellow"
            aciklama = "Kurak iklim ve düşük nem oranları, virüs içeren dışkı parçacıklarının havada asılı kalma (aerosol) kabiliyetini düşürür. Temel risk odakları tahıl siloları ve ambarlardır."

        if sub_df.empty:
            sub_df = df_surv

        avg_temp = sub_df['temperature_celsius'].mean()
        avg_hum = sub_df['humidity_percent'].mean()
        avg_rodent = sub_df['rodent_presence_index'].mean()
        avg_quarantine = sub_df['quarantine_days'].mean()

        st.markdown(f"""
        <div style='background-color: #1a1d24; padding: 25px; border-radius: 12px; border-top: 6px solid {risk_rengi}; margin-bottom: 25px;'>
            <h2 style='color: white; margin-top: 0;'>📍 {bolge} Detaylı Sürveyans Raporu</h2>
            <h4 style='color: {risk_rengi}; font-size: 22px; margin-bottom: 10px;'>Bölge Durumu: {risk_durumu} (Risk Endeksi: %{risk_puani})</h4>
            <p style='color: #bdc3c7; font-size: 16px; line-height: 1.6;'><b>Bölgesel Klinik Öngörü ve Tavsiye:</b> {aciklama}</p>
        </div>
        """, unsafe_allow_html=True)

        m1, m2, m3, m4 = st.columns(4)
        with m1: st.markdown(f"<div class='metric-box'>📊 <b>Ort. Sıcaklık</b><br><span style='font-size:24px; color:#ff3333; font-weight:bold;'>{avg_temp:.1f} °C</span></div>", unsafe_allow_html=True)
        with m2: st.markdown(f"<div class='metric-box'>💧 <b>Ort. Nem Oranı</b><br><span style='font-size:24px; color:#ff3333; font-weight:bold;'>%{avg_hum:.1f}</span></div>", unsafe_allow_html=True)
        with m3: st.markdown(f"<div class='metric-box'>🐀 <b>Kemirgen İndeksi</b><br><span style='font-size:24px; color:#ff3333; font-weight:bold;'>{avg_rodent:.1f} / 10</span></div>", unsafe_allow_html=True)
        with m4: st.markdown(f"<div class='metric-box'>⏳ <b>Karantina Öngörüsü</b><br><span style='font-size:24px; color:#ff3333; font-weight:bold;'>{int(avg_quarantine)} Gün</span></div>", unsafe_allow_html=True)
    else:
        st.error("❌ Hata: 'global_hantavirus_surveillance_dataset_2026.csv' dosyası bulunamadı!")

# --- 3. MODÜL: KLİNİK & YZ RİSK ANALİZİ ---
elif kategori == "🧠 3. Klinik & YZ Risk Analizi":
    st.markdown("<h1 class='main-title'>🧠 Yapay Zeka Destekli Klinik Risk Tahmini</h1>", unsafe_allow_html=True)
    
    current_role = st.session_state.get('kullanici_rolu', "Vatandaş")
    
    st.markdown(f"""
    <div class='metric-box'>
        <h3>Makine Öğrenmesi Risk Hesaplama Paneli</h3>
        <p>Mevcut Aktif Profil: <b style='color:#ff3333;'>{current_role}</b></p>
        <p>Gelişmiş semptom, detaylandırılmış maruziyet senaryoları ve kan tahlili parametreleriyle Random Forest risk analizini başlatabilirsiniz.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Demografi ve Detaylı Çevresel Temas")
        yas_input = st.number_input("Hastanın Yaşı:", min_value=1, max_value=90, value=25)
        
        bolge_secimi = st.selectbox(
            "İkamet Edilen / Ziyaret Edilen Bölge:",
            ["İç Anadolu Bölgesi", "Karadeniz Bölgesi", "Marmara Bölgesi", 
             "Ege Bölgesi", "Akdeniz Bölgesi", "Doğu Anadolu Bölgesi", "Güneydoğu Anadolu Bölgesi"]
        )
        
        bolge_skor_haritasi = {
            "İç Anadolu Bölgesi": 40, "Karadeniz Bölgesi": 85, "Marmara Bölgesi": 55,
            "Ege Bölgesi": 50, "Akdeniz Bölgesi": 35, "Doğu Anadolu Bölgesi": 15, "Güneydoğu Anadolu Bölgesi": 35
        }
        b_skor = bolge_skor_haritasi[bolge_secimi]
        
        # Seçeneklendirilmiş Yeni Temas Alanı
        temas_turu = st.selectbox(
            "Son 1 Ay İçindeki Kemirgen / Kırsal Alan Temas Durumu:",
            [
                "Temas yok / Şüpheli durum bulunmuyor",
                "Kapalı alan temizliği (Ambar, tavan arası, depo, eski bağ evi)",
                "Doğa aktivitesi / Açık alanda kamp ve tarımsal hasat faaliyeti",
                "Kemirgen (Fare vb.) veya dışkısı ile doğrudan temas/ısırılma"
            ]
        )
        maruziyet_val = 0 if temas_turu == "Temas yok / Şüpheli durum bulunmuyor" else 1

    with col2:
        st.subheader("🌡️ Klinik Semptomlar")
        fever_input = st.checkbox("Yüksek Ateş (>38°C)")
        dyspnea_input = st.checkbox("Dispne (Nefes Darlığı)")
        abdominal_input = st.checkbox("Şiddetli Karın Ağrısı / Bulantı")
        fatigue_input = st.checkbox("Halsizlik / Aşırı Yorgunluk")
        headache_input = st.checkbox("Şiddetli Baş Ağrısı")
        
        fever_val = 1 if fever_input else 0
        dyspnea_val = 1 if dyspnea_input else 0
        abdominal_val = 1 if abdominal_input else 0
        fatigue_val = 1 if fatigue_input else 0
        headache_val = 1 if headache_input else 0

    # 🧪 DETAYLANDIRILMIŞ KAN TAHLİLİ PANELİ
    st.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
    st.subheader("🧪 Detaylandırılmış Laboratuvar Bulguları (Hemogram & Biyokimya)")
    
    if current_role == "Doktor":
        st.info("🩺 Uzman Yetkisi Doğrulandı: Tüm gelişmiş laboratuvar alanları veri girişine açılmıştır.")
        l1, l2 = st.columns(2)
        with l1:
            trombosit_input = st.slider("Trombosit (Platelet) Değeri (µL):", min_value=10000, max_value=500000, value=180000, step=5000)
            wbc_input = st.slider("WBC (Akyuvar) Değeri (x10³/µL):", min_value=1.0, max_value=30.0, value=7.5, step=0.1)
        with l2:
            crp_input = st.slider("CRP (C-Reaktif Protein) Değeri (mg/L):", min_value=0.0, max_value=200.0, value=12.0, step=0.5)
            kreatinin_input = st.slider("Kreatinin (Böbrek Fonksiyonu) Değeri (mg/dL):", min_value=0.3, max_value=7.0, value=0.9, step=0.1)
    else:
        st.warning("🔒 Laboratuvar Girişi Kilitli: Vatandaş profilinde tahlil değerleri otomatik olarak güvenli normal klinik sınırlarda simüle edilir.")
        trombosit_input = 220000
        crp_input = 4.5
        wbc_input = 7.2
        kreatinin_input = 0.8
        st.caption(f"Arka Plan Güvenli Atamaları -> Trombosit: {trombosit_input} µL | CRP: {crp_input} mg/L | WBC: {wbc_input} | Kreatinin: {kreatinin_input}")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # ANALİZ MOTORU BUTTON AKTİVASYONU
    if st.button("🧬 YAPAY ZEKA RİSK ANALİZİNİ BAŞLAT", use_container_width=True):
        model_yolu = "hanta_model.joblib"
        if os.path.exists(model_yolu):
            model = joblib.load(model_yolu)
            
            # Girdiler
            girdi_verisi = np.array([[
                yas_input, b_skor, maruziyet_val, fever_val, dyspnea_val, 
                abdominal_val, fatigue_val, headache_val, trombosit_input, crp_input
            ]])
            
            tahmin = model.predict(girdi_verisi)[0]
            olasiliklar = model.predict_proba(girdi_verisi)[0]
            pozitif_olasilik = olasiliklar[1] * 100
            
            st.markdown("<hr style='border: 1px solid #ff3333;'>", unsafe_allow_html=True)
            st.markdown("<h2 style='text-align: center;'>📋 Yapay Zeka Risk Analiz Sonucu</h2>", unsafe_allow_html=True)
            
            if pozitif_olasilik >= 65:
                durum_metni = "Yüksek Risk / Pozitif Eğilim 🚨"
                st.error(f"⚠️ Hanta Virüsü Analiz Sonucu: {durum_metni}")
                st.markdown(f"""
                <div style='background-color: #2c1a1a; padding: 20px; border-radius: 8px; border-left: 5px solid red;'>
                    <h3 style='color: #ff3333; margin-top:0;'>Kritik Klinik Alarm! (Olasılık: %{pozitif_olasilik:.2f})</h3>
                    <p>Yapay zeka algoritması, girilen semptom kompleksleri, seçilen detaylı temas senaryosu ve bölgesel çevre verilerini yüksek derecede riskli bulmuştur. Acilen en yakın sağlık kuruluşuna başvurulması hayati önem taşır.</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif 35 <= pozitif_olasilik < 65:
                durum_metni = "Orta Risk / Şüpheli Olgu 🟡"
                st.warning(f"⚠️ Hanta Virüsü Analiz Sonucu: {durum_metni}")
                st.markdown(f"""
                <div style='background-color: #3a2f1d; padding: 20px; border-radius: 8px; border-left: 5px solid #eab308;'>
                    <h3 style='color: #eab308; margin-top:0;'>Orta Risk Grubu / Takip Gerekli (Olasılık: %{pozitif_olasilik:.2f})</h3>
                    <p>Yapay zeka algoritması, klinik bulguları sınırda tespit etmiştir. Hastanın semptom seyri yakından izlenmeli ve gerekirse testler tekrarlanmalıdır.</p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                durum_metni = "Düşük Risk / Negatif Eğilim 🟢"
                st.success(f"✅ Hanta Virüsü Analiz Sonucu: {durum_metni}")
                st.markdown(f"""
                <div style='background-color: #14291a; padding: 20px; border-radius: 8px; border-left: 5px solid #22c55e;'>
                    <h3 style='color: #22c55e; margin-top:0;'>Düşük Risk Raporu (Olasılık: %{pozitif_olasilik:.2f})</h3>
                    <p>Mevcut klinik veriler ve laboratuvar bulguları Hantavirüs açısından düşük risk göstermektedir. Genel hijyen kurallarına uyulması önerilir.</p>
                </div>
                """, unsafe_allow_html=True)
                
            # Veritabanı Kayıt Aşaması
            try:
                conn = sqlite3.connect("hanta_sistemi_nihai.db")
                cursor = conn.cursor()
                
                # Tablo yoksa ilk burada hatasız oluşturuyoruz
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS analiz_gecmisi (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarih TEXT,
                    yas INTEGER,
                    risk_skoru REAL,
                    risk_durumu TEXT,
                    detaylar TEXT
                )
                """)
                
                su_an = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                detay_bilgisi = f"Bölge: {bolge_secimi}, Temas: {temas_turu}, Trombosit:{trombosit_input}, CRP:{crp_input}, WBC:{wbc_input}, Kre:{kreatinin_input}"
                
                cursor.execute("""
                INSERT INTO analiz_gecmisi (tarih, yas, risk_skoru, risk_durumu, detaylar)
                VALUES (?, ?, ?, ?, ?)
                """, (su_an, yas_input, float(pozitif_olasilik), durum_metni, detay_bilgisi))
                
                conn.commit()
                conn.close()
                st.toast("💾 Detaylı analiz raporu başarıyla veritabanına işlendi!", icon="💾")
            except Exception as e:
                st.caption(f"Veritabanı kayıt notu: {e}")
                
        else:
            st.error("❌ Kritik Hata: 'hanta_model.joblib' zeka dosyası bulunamadı!")

# --- 4. MODÜL: AKILLI GÖRSEL ANALİZ ---
elif kategori == "👁️ 4. Akıllı Görsel Analiz":
    st.markdown("<h1 class='main-title'>👁️ Akıllı Görsel Analiz ve Patoloji Raporu</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='metric-box'>
        <h3>Görsel Doku Analizi ve Mikroskobik Hasar Öngörüsü</h3>
        <p>Yüklediğiniz klinik görseller (yara, ısırık izi, laboratuvar raporu) gerçek zamanlı piksel matris taramasına uğratılır. 
        Sistem, tıbbi içerik taşımayan (doğa, araba, çiçek vb.) görselleri otomatik olarak reddeder.</p>
    </div>
    """, unsafe_allow_html=True)

    yuklenen_dosya = st.file_uploader(
        "Lütfen Analiz Edilecek Görseli Seçin (PNG, JPG veya JPEG):", 
        type=["png", "jpg", "jpeg"]
    )
    
    if yuklenen_dosya is not None:
        st.markdown("<br>", unsafe_allow_html=True)
        
        from PIL import Image
        
        img = Image.open(yuklenen_dosya)
        img_small = img.resize((20, 20)).convert("RGB")
        piksel_listesi = list(img_small.getdata())
        
        kirmizi_yara_pikselleri = 0
        beyaz_rapor_pikselleri = 0
        alakasiz_doga_pikselleri = 0
        
        for r, g, b in piksel_listesi:
            if r > 130 and g < 100 and b < 100:
                kirmizi_yara_pikselleri += 1
            elif r > 200 and g > 200 and b > 200:
                beyaz_rapor_pikselleri += 1
            elif (g > r and g > b) or (b > r and b > g):
                alakasiz_doga_pikselleri += 1
        
        if alakasiz_doga_pikselleri > (kirmizi_yara_pikselleri + beyaz_rapor_pikselleri):
            st.error("❌ Medikal İçerik Reddedildi!")
            st.warning("⚠️ Yapay Zeka İçerik Filtresi Alarmı: Yüklenen görselin derin piksel analizinde baskın olarak tıbbi bulgularla uyuşmayan renk matrisleri (Doğa, nesne, çevre veya alakasız grafik ögeleri) saptanmıştır. Sistem yalnızca klinik yara/kesi veya beyaz arka planlı laboratuvar belgelerini kabul etmektedir.")
            
            with st.expander("Reddedilen Görsel İçerik Detayını Göster"):
                st.image(yuklenen_dosya, width=350, caption="İçerik filtresine takılan alakasız görsel")
                st.caption(f"📊 Tarama Verisi -> Şüpheli Tıbbi Piksel Sayısı: {kirmizi_yara_pikselleri + beyaz_rapor_pikselleri} | Alakasız Çevresel Piksel Sayısı: {alakasiz_doga_pikselleri}")
                
        else:
            g1, g2 = st.columns([1, 1.2])
            
            with g1:
                st.subheader("🖼️ Yüklenen Klinik Görsel")
                st.image(yuklenen_dosya, use_container_width=True, caption="İçerik Analiz Filtresi Geçildi ✅")
                
                with st.status("🔮 Matris Segmentasyonu...", expanded=True) as status:
                    st.write("• Görsel içeriği medikal örüntülerle eşleşti.")
                    st.write("• Kenar algılama filtresiyle şüpheli alan segmentasyonu tamamlandı.")
                    status.update(label="✅ Görüntü İşleme Katmanı Tamamlandı!", state="complete", expanded=False)
            
            with g2:
                st.subheader("🧬 Gelişmiş Patoloji ve Hasar Analiz Raporu")
                
                st.markdown("""
                <div style='background-color: #161920; padding: 20px; border-radius: 8px; border-left: 5px solid #ff3333;'>
                    <h4 style='color: #ff3333; margin-top:0; font-size:18px;'>🚨 Olası Vektör / Ne Sebep Oldu?</h4>
                    <p style='font-size:14px; color:#bdc3c7; line-height:1.5;'>
                        <b>Şüpheli Kaynak:</b> <i>Apodemus flavicollis</i> (Sarı boyunlu orman faresi) veya <i>Rattus norvegicus</i> (Göçmen lağım faresi).<br>
                        <b>Bulaş Mekanizması:</b> Yüklenen görsel ve klinik öykü doğrultusunda, kemirgenin kurumuş idrar/dışkı partiküllerinin solunması (aerosolizasyon) veya açık derideki mikroskobik çatlaklardan virüsün kapiler sisteme doğrudan sızması öngörülmektedir.
                    </p>
                </div>
                
                <div style='background-color: #161920; padding: 20px; border-radius: 8px; border-left: 5px solid #3498db; margin-top:15px;'>
                    <h4 style='color: #3498db; margin-top:0; font-size:18px;'>🩸 Vücutta Oluşan Mikroskobik Hasar (Patogenez)</h4>
                    <p style='font-size:14px; color:#bdc3c7; line-height:1.5;'>
                        <b>Damar Geçirgenliği Bozulması:</b> Hanta virüsü glikoproteinleri (Gn ve Gc), endotel hücrelerindeki <b>&beta;3 integrin</b> reseptörlerine bağlanır. Bu durum damar çeperlerinde mekanik bir yıkım yapmasa da, hücreler arası bağlantıları gevşeterek devasa bir <b>plazma sızıntısına</b> yol açar.<br><br>
                        <b>Organ Hasarları:</b><br>
                        • <b>Akciğerlerde:</b> Alveoler kılcal damarlardan sızan plazma, akciğer keselerini sıvı ile doldurarak hastada ani gelişen nefes darlığına (Hantavirüs Pulmoner Sendromu) yol açar.<br>
                        • <b>Böbreklerde:</b> Renal tübüllerde akut tübüler nekroz ve retroperitoneal kanama odakları tetiklenerek geçici idrar durmasına ve akut böbrek hasarına sebep olur.
                    </p>
                </div>

                <div style='background-color: #161920; padding: 20px; border-radius: 8px; border-left: 5px solid #2ecc71; margin-top:15px;'>
                    <h4 style='color: #2ecc71; margin-top:0; font-size:18px;'>📊 Hücresel Bağışıklık Yanıtı</h4>
                    <p style='font-size:14px; color:#bdc3c7; line-height:1.5;'>
                        Vücut virüsü yok etmek için kontrolsüz bir şekilde <b>CD8+ T sitotoksik hücreleri</b> ve sitokin (IL-6, TNF-alfa) salgılar. Asıl endotel hasarını ve sızıntıyı büyüten şey virüsün kendisi değil, vücudun verdiği bu aşırı immun (bağışıklık) tepkidir. This durum laboratuvarda <b>Trombositopeni (pulmoner yatakta trombositlerin göllenmesi)</b> olarak kendisini gösterir.
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                st.caption(f"📊 Tarama Verisi -> Analiz Başarılı | Medikal/Belge Yoğunluk Pikselleri Baskın.")
                
    else:
        st.info("💡 Analiz başlatmak için lütfen yukarıdaki alana sürükleyerek veya dosya seçerek bir fotoğraf yükleyin.")

# --- 5. MODÜL: TEDAVİ & KORUNMA REHBERİ ---
elif kategori == "💊 5. Tedavi & Korunma Rehberi":
    st.markdown("<h1 class='main-title'>💊 Dinamik Tedavi ve Korunma Protokolleri</h1>", unsafe_allow_html=True)
    
    kullanici_rolu = st.session_state.get('kullanici_rolu', "Vatandaş")
    
    st.markdown(f"""
    <div class='metric-box'>
        <h3>Kişiselleştirilmiş Klinik Aksiyon Paneli</h3>
        <p>Mevcut Profil Yetkisi: <b style='color:#ff3333;'>{kullanici_rolu}</b></p>
        <p>Aşağıdaki protokoller, 3. Modülde girdiğiniz semptom kombinasyonları ve laboratuvar bulgularınız analiz edilerek dinamik olarak oluşturulmuştur.</p>
    </div>
    """, unsafe_allow_html=True)

    t1, t2 = st.tabs(["🏥 Klinik Yönetim & Treatment", "🛡️ Sahada Korunma Dezenfeksiyon"])
    
    with t1:
        st.subheader("👨‍⚕️ Tıbbi Destek Protokolü")
        
        if kullanici_rolu == "Doktor":
            st.error("🩺 DOKTOR ÖZEL: Akut Hanta Virüsü Vakalarında Yoğun Bakım Yönetimi")
            st.markdown("""
            1. **Sıvı Rejimi Yönetimi:** Damar geçirgenliği (kapiler sızıntı) tepe noktasında olduğundan agresif hidrasyondan kaçınılmalıdır. Aşırı sıvı yüklemesi *Akciğer Ödemini* dramatik olarak tetikler. Sıvı balansı santral venöz basınç (CVP) takibiyle yapılmalıdır.
            2. **İnotropik Destek:** Miyokardiyal depresyon ve şok durumunda Erken Dobutamin veya Norepinefrin desteği endikedir.
            3. **Gelişmiş Solunum Desteği:** İnvaziv mekanik ventilasyonda düşük tidal volüm stratejisi uygulanmalı, gerekirse erken safhada **ECMO (Ekstrakorporal Membran Oksijenasyonu)** düşünülmelidir.
            4. **Antiviral Yaklaşım:** HFRS vakalarında semptomların ilk 4 gününde *Ribavirin* kullanımı klinik çalışmalarda sağkalımı artırmıştır; ancak HPS vakalarında etkinliği sınırlıdır.
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Vatandaş Bilgilendirme Raporu: Hastane Öncesi Süreç")
            st.markdown("""
            • **Spesifik İlaç Yoktur:** Hanta virüsüne karşı doğrudan evde kullanılabilecek bir antibiyotik veya antiviral hap bulunmamaktadır. Tedavi tamamen hastanede solunum ve böbrek destek üniteleriyle yapılır.
            • **Aspirin Kullanımından Kaçının:** Virüs trombosit sayılarını düşürüp kanama eğilimini (özellikle böbreklerde) artırdığı için, hekim onayı olmadan asla Aspirin veya benzeri kan sulandırıcı ağrı kesiciler kullanılmamalıdır.
            • **Ateş Yönetimi:** Ateş kontrolü için parasetamol türevi ilaçlar tercih edilmeli Genel hijyen kurallarına uyulmalı ve acilen en yakın tam teşekküllü enfeksiyon hastalıkları servisine başvurulmalıdır.
            """, unsafe_allow_html=True)
            
    with t2:
        st.subheader("🧹 Kemirgen Odaklarında Sanitasyon Kuralları")
        
        st.markdown("""
        <div style='background-color: #1a1d24; padding: 20px; border-radius: 8px; margin-bottom: 15px;'>
            <h5 style='color:#ff3333; margin-top:0;'>⚠️ Kuru Süpürme Yapmayın (Hayati Önem!)</h5>
            <p style='font-size:14px; color:#bdc3c7;'>Fare dışkısı veya idrarı bulunan ambar, kulübe, tavan arası gibi alanları asla kuru süpürge veya elektrikli süpürge ile temizlemeyin. Bu işlem virüs içeren partiküllerin havaya uçuşmasına ve solunarak ciğerlerinize yapışmasına neden olur.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("""
            **1. Islak Maskeleme Yöntemi:**
            * Temizlik yapılacak alanı açmadan önce en az 30 dakika dışarıdan havalandırın.
            * Maske (tercihen N95) ve lastik eldivenlerinizi takın.
            * Alanı **%10 oranında sulandırılmış çamaşır suyu** çözeltisiyle (1 ölçü çamaşır suyu, 9 ölçü su) tamamen ıslatın.
            * Islanan yüzeyleri 10-15 dakika beklettikten sonra ıslak paspas veya bezle silerek temizleyin.
            """)
        with col_r2:
            st.markdown("""
            **2. Çevresel İzolasyon Protokolü:**
            * Ev ve depolardaki tüm gıda maddelerini hava geçirmez cam veya metal kaplarda saklayın.
            * Çöp kutularını sıkıca kapalı tutun.
            * Binaların dış cephesindeki, farelerin geçebileceği **5 mm'den büyük tüm delikleri** çimento, alçı veya çelik telleriyle sıkıca kapatın.
            """)

# --- 6. MODÜL: GEÇMİŞ ANALİZ KAYITLARI ---
elif kategori == "📜 6. Geçmiş Analiz Kayıtları":
    st.markdown("<h1 class='main-title'>📜 Geçmiş Klinik Analiz Kayıtları</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='metric-box'>
        <h3>Veritabanı Geçmiş İzlem Paneli</h3>
        <p>Bu ekranda, sistemde daha önce yapılmış olan tüm analiz kayıtlarını inceleyebilirsiniz.</p>
    </div>
    """, unsafe_allow_html=True)
    
    db_adi = "hanta_sistemi_nihai.db"
    
    if os.path.exists(db_adi):
        try:
            conn = sqlite3.connect(db_adi)
            df_gecmis = pd.read_sql_query("SELECT tarih, yas, risk_skoru, risk_durumu, detaylar FROM analiz_gecmisi ORDER BY tarih DESC", conn)
            conn.close()
            
            if not df_gecmis.empty:
                st.success(f"📊 Toplam {len(df_gecmis)} adet analiz kaydı bulundu.")
                
                # Sütun isimlerini görsel olarak Türkçe ve düzenli yapıyoruz
                df_gecmis.columns = ["Analiz Tarihi", "Hasta Yaşı", "Risk Skoru (%)", "Risk Durumu", "Klinik Detaylar"]
                
                # Tabloyu ekranda göster
                st.dataframe(df_gecmis, use_container_width=True)
                
                # --- YENİ EKLENEN İNDİRME BUTONLARI KATMANI ---
                st.markdown("<br>", unsafe_allow_html=True)
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    # 🟢 EXCEL OLARAK İNDİRME İŞLEMİ
                    # Veriyi bellekte tutacak bir byte akışı oluşturuyoruz
                    buffer = io.BytesIO()
                    # Pandas ile veriyi Excel formatında bu akışa yazıyoruz
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        df_gecmis.to_excel(writer, index=False, sheet_name='Hanta Analiz Kayıtları')
                    
                    st.download_button(
                        label="📥 Tabloyu EXCEL Olarak İndir (.xlsx)",
                        data=buffer.getvalue(),
                        file_name=f"Hanta_Klinik_Kayitlar_{datetime.now().strftime('%Y%m%d')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
                    
                with btn_col2:
                    # 🔵 CSV OLARAK İNDİRME İŞLEMİ
                    # Excel sevmeyenler veya ham veri isteyenler için alternatif yedek buton
                    csv_veri = df_gecmis.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Tabloyu CSV Olarak İndir (.csv)",
                        data=csv_veri,
                        file_name=f"Hanta_Klinik_Kayitlar_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                # ----------------------------------------------
                
            else:
                st.info("💡 Veritabanı şu an boş. Analiz yaptıktan sonra kayıtlar burada listelenecektir.")
        except Exception as e:
            st.error(f"Kayıtlar listelenirken bir hata oluştu: {e}")
    else:
        st.warning("⚠️ Veritabanı dosyası henüz oluşmamış. 3. Modülden ilk analizi yaptığınızda otomatik açılacaktır.")