
## Kurulum

```bash
git clone https://github.com/aysegulyilmazz/foundry-local-rag-assistant.git
cd foundry-local-rag-assistant
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Foundry Local'ın kurulu olması gerekir: [Microsoft Foundry Local](https://github.com/microsoft/Foundry-Local)

Modelleri indir:
```bash
foundry model load qwen3-embedding-0.6b-cuda-gpu
foundry model load Phi-3.5-mini-instruct-cuda-gpu
```

Bilgi tabanını oluştur (ilk kurulumda tek seferlik):
```bash
python setup_db.py
```

## Kullanım

**Komut satırı:**
```bash
python main.py
```

**Web arayüzü:**
```bash
streamlit run app.py
```

**Testleri çalıştır:**
```bash
pytest test_rag.py -v
```

**Retrieval değerlendirmesi:**
```bash
python evaluate.py
```

## Proje Yapısı

- `config.py` — Model isimleri, eşik değeri, sistem promptu
- `knowledge_base.py` — Devlet yardımları bilgi tabanı (12 belge)
- `setup_db.py` — Belgeleri vektörleştirip SQLite'a kaydeden kurulum betiği
- `embed_text.py` — Metinleri vektöre çeviren yardımcı betik (ayrı process)
- `rag_utils.py` — Çekirdek RAG fonksiyonları (hybrid search, query rewriting, ingestion, loglama)
- `analytics.py` — Log dosyasından kullanım istatistikleri çıkarır
- `main.py` — CLI arayüzü
- `app.py` — Streamlit web arayüzü (sohbet, PDF yükleme, analitik panel)
- `evaluate.py` — Retrieval doğruluğunu ölçen değerlendirme script'i
- `test_rag.py` — pytest birim testleri

## Bilinen Sınırlamalar

- Küçük yerel modeller (özellikle 0.6B parametre) çok genel/meta sorularda ("bu belgede ne anlatılıyor?") zayıf kalabiliyor; spesifik terim içeren sorularda çok daha isabetli.
- Query rewriting kural tabanlı (LLM kullanmıyor), bu yüzden hızlı ve kararlı ama çok karmaşık çok-adımlı sohbetlerde sınırlı kalabilir.