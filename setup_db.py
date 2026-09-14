
import sqlite3
import json
from foundry_local_sdk import Configuration, FoundryLocalManager
from knowledge_base import DOCUMENTS
import config


def get_embedding_model():
    cfg = Configuration(app_name="local_rag_app")
    FoundryLocalManager.initialize(cfg)
    manager = FoundryLocalManager.instance

    model = manager.catalog.get_model(config.EMBEDDING_MODEL_ALIAS)
    print(f"'{config.EMBEDDING_MODEL_ALIAS}' modeli indiriliyor/yükleniyor...")
    model.download(lambda p: None)
    model.load()
    print("Embedding modeli hazır.")
    return model


def main():
    model = get_embedding_model()
    embedding_client = model.get_embedding_client()

    conn = sqlite3.connect(config.DB_NAME)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS chunks")
    cur.execute("""
        CREATE TABLE chunks (
            id INTEGER PRIMARY KEY,
            title TEXT,
            content TEXT,
            embedding TEXT
        )
    """)

    for i, doc in enumerate(DOCUMENTS):
        print(f"Vektörleştiriliyor ({i+1}/{len(DOCUMENTS)}): {doc['title']}")
        response = embedding_client.generate_embedding(doc["content"])
        vector = response.data[0].embedding
        cur.execute(
            "INSERT INTO chunks (title, content, embedding) VALUES (?, ?, ?)",
            (doc["title"], doc["content"], json.dumps(vector))
        )

    conn.commit()
    conn.close()
    model.unload()
    print(f"\nTamamlandı! {len(DOCUMENTS)} belge '{config.DB_NAME}' dosyasına kaydedildi.")


if __name__ == "__main__":
    main()