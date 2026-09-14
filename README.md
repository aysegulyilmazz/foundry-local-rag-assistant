# 🏛️ Foundry Local RAG Assistant

Microsoft Foundry Local kullanılarak geliştirilmiş, tamamen yerel çalışan bir **RAG (Retrieval-Augmented Generation)** uygulamasıdır.

Proje; devlet yardımları hakkında kullanıcı sorularını yerel bilgi tabanında arar, ilgili belgeleri **Hybrid Search** ile bulur ve yerel bir dil modeli kullanarak bağlama dayalı cevap üretir.

Tüm embedding ve LLM işlemleri cihaz üzerinde çalışır. Uygulama çalışırken harici bir yapay zekâ API'sine ihtiyaç duymaz.

---

## 🌟 Öne Çıkan Özellikler

### 🔒 Yerel Çalışma

Embedding ve cevap üretimi **Microsoft Foundry Local** üzerinden cihaz üzerinde gerçekleştirilir.

### 🔎 Hybrid Search

Belge aramasında iki farklı yöntem birlikte kullanılır:

- %70 Semantic Similarity
- %30 Keyword Matching

Bu sayede yalnızca kelime eşleşmesine değil, sorgu ile belgeler arasındaki anlamsal benzerliğe de bakılır.

### 🧠 Query Rewriting

"Peki başvuru şartları ne?" gibi bağlama bağlı takip soruları, önceki kullanıcı sorusu kullanılarak arama için daha anlamlı hale getirilir.

Örneğin:

```text
İlk soru:
Engelli aileme evde bakım için hangi yardımlar var?

Takip sorusu:
Peki başvuru şartları ne?

Arama sorgusu:
Engelli aileme evde bakım için hangi yardımlar var?
Peki başvuru şartları ne?
```

Böylece çok turlu sohbetlerde retrieval sırasında önceki konu kaybolmaz.

### 📄 PDF ve TXT Belge Yükleme

Streamlit arayüzünden kullanıcı kendi:

- PDF
- TXT

dosyasını sisteme yükleyebilir.

Belge otomatik olarak parçalara ayrılır, embedding'leri oluşturulur ve SQLite bilgi tabanına eklenir.

### ✂️ Akıllı Chunking

Belgeler belirli karakter sınırlarına göre parçalara ayrılır.

Tek başına sınırı aşan uzun paragraflar da kelime bazlı olarak daha küçük parçalara bölünür.

### 🛡️ Similarity Threshold

Arama sonucunun benzerlik skoru belirlenen eşik değerinin altındaysa sistem cevap üretmek yerine fallback mesajı döndürür.

Bu mekanizma, bilgi tabanında karşılığı olmayan sorulara modelin tahminde bulunmasını azaltmayı amaçlar.

### 🧹 Context Filtering

Aramada bulunan her belge doğrudan LLM'e gönderilmez.

En yüksek skorlu sonuçtan belirgin biçimde uzak olan belgeler context dışında bırakılarak alakasız belgelerin cevabı kirletmesi azaltılır.

### 💬 Çok Turlu Sohbet

Streamlit arayüzü önceki mesajları saklar.

Böylece kullanıcı aynı konu üzerinde takip soruları sorabilir.

### 📝 Logging

Uygulamadaki temel RAG işlemleri `rag_app.log` dosyasına kaydedilir.

Örneğin:

```text
Arama baslatildi
Embedding baslatildi
Embedding tamamlandi
Arama tamamlandi
Sonuc | score=...
Query rewriting tamamlandi
History destekli cevap uretildi
```

Bu kayıtlar hata ayıklama ve sistem davranışının incelenmesi için kullanılabilir.

### 🧪 Birim Testleri

Projede `pytest` kullanılarak temel RAG fonksiyonları test edilir.

Test edilen bileşenlerden bazıları:

- `cosine_similarity`
- `keyword_score`
- `chunk_text`
- uzun paragraf bölme davranışı
- boş metin davranışı

### 📊 Retrieval Evaluation

`evaluate.py` ile retrieval sisteminin test sorgularında doğru belgeleri bulup bulmadığı değerlendirilebilir.

### 📈 Analitik

`analytics.py`, uygulama loglarından kullanım ve retrieval istatistikleri çıkarmak için kullanılır.

---

## 🏗️ RAG Mimarisi

```text
[ Kullanıcı Sorusu ]
        │
        ▼
[ Query Rewriting ]
        │
        ▼
[ Qwen Embedding Modeli ]
        │
        ▼
[ Query Embedding ]
        │
        ▼
[ SQLite Bilgi Tabanı ]
        │
        ▼
[ Hybrid Search ]
  ├─ %70 Semantic Similarity
  └─ %30 Keyword Matching
        │
        ▼
[ Similarity Threshold ]
        │
        ├── Skor düşük
        │       │
        │       ▼
        │   [ Fallback Mesajı ]
        │
        └── Skor yeterli
                │
                ▼
        [ Context Filtering ]
                │
                ▼
        [ İlgili Belgeler ]
                │
                ▼
        [ Phi-3.5-mini ]
                │
                ▼
        [ Kullanıcı Cevabı ]
```

---

## 📁 Proje Yapısı

```text
foundry-local-rag-assistant/
│
├── app.py
│   └── Streamlit web arayüzü
│
├── main.py
│   └── Komut satırı (CLI) arayüzü
│
├── config.py
│   └── Model isimleri, eşik değeri ve sistem promptu
│
├── rag_utils.py
│   └── RAG çekirdeği
│       ├── cosine similarity
│       ├── keyword scoring
│       ├── hybrid search
│       ├── query rewriting
│       ├── chunking
│       ├── document ingestion
│       ├── answer generation
│       └── logging
│
├── embed_text.py
│   └── Metinleri embedding vektörlerine dönüştürür
│
├── knowledge_base.py
│   └── Devlet yardımları bilgi tabanı
│
├── setup_db.py
│   └── Bilgi tabanını SQLite veritabanına aktarır
│
├── evaluate.py
│   └── Retrieval performansını değerlendirir
│
├── analytics.py
│   └── Loglardan kullanım istatistikleri çıkarır
│
├── test_rag.py
│   └── Pytest birim testleri
│
├── requirements.txt
│   └── Python bağımlılıkları
│
├── .gitignore
│   └── Git dışında bırakılan dosyalar
│
└── README.md
    └── Proje dokümantasyonu
```

`rag_database.db`, `.venv`, log dosyaları ve diğer yerel çalışma çıktılarının GitHub deposuna eklenmemesi önerilir.

---

## ⚙️ Kurulum

### 1. Projeyi klonlayın

```bash
git clone https://github.com/aysegulyilmazz/foundry-local-rag-assistant.git
cd foundry-local-rag-assistant
```

### 2. Sanal ortam oluşturun

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Bağımlılıkları yükleyin

```bash
pip install -r requirements.txt
```

---

## 🤖 Foundry Local

Projeyi çalıştırmak için **Microsoft Foundry Local** kurulu olmalıdır.

Foundry Local kurulumundan sonra projede kullanılan modelleri yükleyin:

```bash
foundry model load qwen3-embedding-0.6b-cuda-gpu
foundry model load Phi-3.5-mini-instruct-cuda-gpu
```

---

## 🗄️ Bilgi Tabanını Oluşturma

İlk kurulumda:

```bash
python setup_db.py
```

Bu işlem bilgi tabanındaki belgeleri embedding vektörlerine dönüştürerek SQLite veritabanına kaydeder.

Bu komutun her uygulama başlangıcında tekrar çalıştırılması gerekmez.

---

## ▶️ Kullanım

### Web Arayüzü

Streamlit uygulamasını başlatmak için:

```bash
streamlit run app.py
```

Tarayıcı üzerinden sohbet arayüzüne erişebilir, örnek soruları kullanabilir ve kendi PDF/TXT belgelerinizi sisteme ekleyebilirsiniz.

### Komut Satırı

CLI sürümünü çalıştırmak için:

```bash
python main.py
```

---

## 🧪 Testler

Birim testlerini çalıştırmak için:

```bash
pytest test_rag.py -v
```

Örnek başarılı çıktı:

```text
9 passed
```

Testler geliştirme sırasında gerçek bir chunking probleminin tespit edilmesini sağlamıştır: tek başına maksimum chunk uzunluğunu aşan paragrafların bölünmediği durum testler sayesinde bulunmuş ve düzeltilmiştir.

---

## 📊 Retrieval Değerlendirmesi

Retrieval sistemini değerlendirmek için:

```bash
python evaluate.py
```

Bu script, test sorgularında sistemin beklenen belgeleri retrieval sonuçlarında bulup bulamadığını ölçmek için kullanılabilir.

---

## 📝 Loglama

Uygulama çalışırken RAG işlemleri:

```text
rag_app.log
```

dosyasına kaydedilir.

Loglar sayesinde:

- sorgular,
- embedding işlemleri,
- retrieval sonuçları,
- similarity skorları,
- query rewriting işlemleri,
- cevap üretim aşamaları

takip edilebilir.

---

## 🧰 Kullanılan Teknolojiler

- Python
- Microsoft Foundry Local
- Phi-3.5-mini
- Qwen3 Embedding
- Streamlit
- SQLite
- PyPDF
- pytest

---

## 🎯 Projenin Amacı

Bu projenin amacı yalnızca çalışan bir chatbot geliştirmek değil; tamamen yerel çalışan bir RAG sisteminin temel mühendislik bileşenlerini uygulamaktır.

Projede:

**Retrieval → Filtering → Context → Generation**

akışının yanında test, logging, değerlendirme, belge ingestion ve çok turlu sorgu yönetimi gibi gerçek uygulamalarda ihtiyaç duyulan bileşenler de ele alınmıştır.