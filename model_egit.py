import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

print("[+] Sentetik Hanta Virüsü klinik veri seti oluşturuluyor...")

# Gerçekçi bir klinik veri seti simüle edelim (1000 Hasta Kaydı)
np.random.seed(42)
n_samples = 1000

yas = np.random.randint(1, 90, n_samples)
bolge_skoru = np.random.choice([15, 35, 40, 50, 55, 60, 85], n_samples) # Bölgelerin nem/risk oranları
maruziyet = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
fever = np.random.choice([0, 1], n_samples, p=[0.2, 0.8])
dyspnea = np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
abdominal = np.random.choice([0, 1], n_samples, p=[0.5, 0.5])
fatigue = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
headache = np.random.choice([0, 1], n_samples, p=[0.3, 0.7])

# Trombosit (Düşük olması riski artırır)
trombosit = np.where(dyspnea == 1, np.random.randint(50, 140, n_samples), np.random.randint(140, 400, n_samples))
# CRP (Yüksek olması riski artırır)
crp = np.where(fever == 1, np.random.uniform(15, 120, n_samples), np.random.uniform(0, 15, n_samples))

# Risk puanı hesaplayıp hedef değişkeni (Pozitif/Negatif) belirleyelim
skor = (bolge_skoru * 0.2) + (maruziyet * 15) + (fever * 20) + (dyspnea * 25) + (abdominal * 10) + (fatigue * 5) + (headache * 5) + (np.where(trombosit < 150, 15, 0)) + (np.where(crp > 5, 10, 0))
y = np.where(skor > 55, 1, 0)

# DataFrame oluşturma
X = pd.DataFrame({
    'yas': yas, 'bolge_skoru': bolge_skoru, 'maruziyet': maruziyet,
    'fever': fever, 'dyspnea': dyspnea, 'abdominal': abdominal,
    'fatigue': fatigue, 'headache': headache, 'trombosit': trombosit, 'crp': crp
})

print("[+] Random Forest Classifier modeli eğitiliyor...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Modeli kaydediyoruz
joblib.dump(model, "hanta_model.joblib")
print("[+] GERÇEK MAKİNE ÖĞRENMESİ MODELİ ('hanta_model.joblib') BAŞARIYLA OLUŞTURULDU!")