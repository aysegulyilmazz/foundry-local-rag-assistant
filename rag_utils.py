
import sqlite3
import json
import math
import subprocess
import sys
import logging

from foundry_local_sdk import Configuration, FoundryLocalManager

import config




logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.FileHandler("rag_app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


_manager = None
_chat_model = None
_chat_client = None


def get_chat_client():
    global _manager, _chat_model, _chat_client

    if _chat_client is not None:
        return _chat_client

    cfg = Configuration(app_name="local_rag_chat")

    FoundryLocalManager.initialize(cfg)

    _manager = FoundryLocalManager.instance

    _chat_model = _manager.catalog.get_model(
        config.CHAT_MODEL_ALIAS
    )

    _chat_model.download(lambda p: None)
    _chat_model.load()

    _chat_client = _chat_model.get_chat_client()

    _chat_client.settings.temperature = 0.3
    _chat_client.settings.max_tokens = 300
    _chat_client.settings.frequency_penalty = 0.8

    return _chat_client



def cosine_similarity(a, b):
    dot = sum(
        x * y
        for x, y in zip(a, b)
    )

    norm_a = math.sqrt(
        sum(x * x for x in a)
    )

    norm_b = math.sqrt(
        sum(x * x for x in b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)



def keyword_score(query, text):

    query_words = set(
        query.lower()
        .replace("?", "")
        .replace(",", "")
        .replace(".", "")
        .split()
    )

    text_words = set(
        text.lower()
        .replace("?", "")
        .replace(",", "")
        .replace(".", "")
        .split()
    )

    if not query_words:
        return 0.0

    overlap = query_words & text_words

    return len(overlap) / len(query_words)



def embed_texts(texts):


    logger.info(
        "Embedding baslatildi. Metin sayisi: %d",
        len(texts)
    )

    try:
        proc = subprocess.run(
            [sys.executable, "embed_text.py"],
            input=json.dumps(texts),
            capture_output=True,
            text=True,
            check=True,
        )

        vectors = json.loads(
            proc.stdout.strip()
        )

        logger.info(
            "Embedding tamamlandi. Vektor sayisi: %d",
            len(vectors)
        )

        return vectors

    except subprocess.CalledProcessError as e:
        logger.exception(
            "Embedding process hatasi. stderr: %s",
            e.stderr
        )
        raise

    except json.JSONDecodeError:
        logger.exception(
            "Embedding sonucu JSON olarak okunamadi. stdout: %s",
            proc.stdout
        )
        raise


def embed_query(query):


    return embed_texts([query])[0]



def _split_long_paragraph(paragraph, max_chars):
    """
    Tek basina max_chars'i asan paragrafi
    kelime bazli parcalara boler.
    """

    words = paragraph.split()

    pieces = []
    current = ""

    for word in words:

        candidate = (
            f"{current} {word}".strip()
        )

        if len(candidate) <= max_chars:
            current = candidate

        else:
            if current:
                pieces.append(current)

            current = word

    if current:
        pieces.append(current)

    return pieces


def chunk_text(text, max_chars=600):


    paragraphs = [
        p.strip()
        for p in text.split("\n")
        if p.strip()
    ]

    chunks = []
    current = ""

    for paragraph in paragraphs:

        if len(paragraph) > max_chars:

            if current:
                chunks.append(current)
                current = ""

            chunks.extend(
                _split_long_paragraph(
                    paragraph,
                    max_chars
                )
            )

            continue

        candidate = (
            f"{current}\n{paragraph}".strip()
            if current
            else paragraph
        )

        if len(candidate) <= max_chars:
            current = candidate

        else:
            if current:
                chunks.append(current)

            current = paragraph

    if current:
        chunks.append(current)

    return chunks



def ingest_document(title, text):

    logger.info(
        "Belge ekleme baslatildi: %s",
        title
    )

    chunks = chunk_text(text)

    logger.info(
        "Belge chunk'lara ayrildi. Chunk sayisi: %d",
        len(chunks)
    )

    if not chunks:
        logger.warning(
            "Belge bos oldugu icin eklenmedi: %s",
            title
        )
        return 0

    try:
        vectors = embed_texts(chunks)

        conn = sqlite3.connect(
            config.DB_NAME
        )

        cur = conn.cursor()

        for i, (chunk, vector) in enumerate(
            zip(chunks, vectors)
        ):
            chunk_title = (
                f"{title} (parça {i + 1})"
            )

            cur.execute(
                """
                INSERT INTO chunks
                (title, content, embedding)
                VALUES (?, ?, ?)
                """,
                (
                    chunk_title,
                    chunk,
                    json.dumps(vector),
                ),
            )

        conn.commit()
        conn.close()

        logger.info(
            "Belge veritabanina eklendi: %s | %d chunk",
            title,
            len(chunks)
        )

        return len(chunks)

    except Exception:
        logger.exception(
            "Belge eklenirken hata olustu: %s",
            title
        )
        raise



def find_relevant(query, top_k=3):


    logger.info(
        "Arama baslatildi. Query: %s | top_k=%d",
        query,
        top_k
    )

    try:
        query_vector = embed_query(query)

        conn = sqlite3.connect(
            config.DB_NAME
        )

        cur = conn.cursor()

        cur.execute(
            """
            SELECT title, content, embedding
            FROM chunks
            """
        )

        rows = cur.fetchall()

        conn.close()

        logger.info(
            "Veritabanindan %d chunk okundu.",
            len(rows)
        )

        scored = []

        for title, content, embedding_json in rows:

            doc_vector = json.loads(
                embedding_json
            )

            semantic_score = cosine_similarity(
                query_vector,
                doc_vector
            )

            kw_score = keyword_score(
                query,
                title + " " + content
            )

            hybrid_score = (
                0.7 * semantic_score
                + 0.3 * kw_score
            )

            scored.append(
                (
                    hybrid_score,
                    title,
                    content,
                )
            )

        scored.sort(
            key=lambda x: x[0],
            reverse=True
        )

        top_results = scored[:top_k]

        logger.info(
            "Arama tamamlandi. %d sonuc donduruldu.",
            len(top_results)
        )

        for score, title, _ in top_results:
            logger.info(
                "Sonuc | score=%.4f | title=%s",
                score,
                title
            )

        return [
            {
                "title": title,
                "content": content,
                "score": score,
            }
            for score, title, content
            in top_results
        ]

    except Exception:
        logger.exception(
            "Arama sirasinda hata olustu. Query: %s",
            query
        )
        raise



def rewrite_query(query, chat_history):


    query = query.strip()

    if not chat_history:
        return query

    user_messages = [
        msg["content"].strip()
        for msg in chat_history
        if (
            msg.get("role") == "user"
            and msg.get("content", "").strip()
        )
    ]

    if not user_messages:
        return query

    previous_query = user_messages[-1]

    query_lower = query.lower()

    follow_up_markers = (
        "peki",
        "bunun",
        "buna",
        "bunda",
        "bunlar",
        "onun",
        "onda",
        "o zaman",
        "şartları",
        "şartlar",
        "başvuru",
        "ne kadar",
        "nasıl",
        "nereden",
        "kimler",
        "kaç",
    )

    is_short = (
        len(query.split()) <= 7
    )

    looks_like_follow_up = (
        is_short
        or any(
            marker in query_lower
            for marker in follow_up_markers
        )
    )

    if not looks_like_follow_up:

        logger.info(
            "Query rewriting gerekmedi. Query: %s",
            query
        )

        return query

    rewritten = (
        f"{previous_query} {query}"
    )

    logger.info(
        "Query rewriting tamamlandi. "
        "Orijinal query: %s | Yeni query: %s",
        query,
        rewritten
    )

    return rewritten




def generate_answer(messages):


    logger.info(
        "Chat modeli ile cevap uretimi baslatildi."
    )

    try:
        client = get_chat_client()

        result = client.complete_chat(
            messages
        )

        answer = (
            result
            .choices[0]
            .message
            .content
        )

        logger.info(
            "Cevap uretildi. Karakter sayisi: %d",
            len(answer)
        )

        return answer

    except Exception:
        logger.exception(
            "Chat modeli cevap uretirken hata olustu."
        )
        raise


def generate_answer_with_history(
    query,
    context,
    chat_history
):


    logger.info(
        "History ile cevap uretimi baslatildi. "
        "Gecmis mesaj sayisi: %d",
        len(chat_history)
    )

    system_msg = {
        "role": "system",
        "content": (
            f"{config.SYSTEM_PROMPT}\n\n"
            f"BAĞLAM:\n{context}"
        ),
    }

    recent_history = (
        chat_history[-4:]
        if len(chat_history) > 4
        else chat_history
    )

    messages = (
        [system_msg]
        + recent_history
        + [
            {
                "role": "user",
                "content": query,
            }
        ]
    )

    try:
        client = get_chat_client()

        result = client.complete_chat(
            messages
        )

        answer = (
            result
            .choices[0]
            .message
            .content
        )

        logger.info(
            "History destekli cevap uretildi. "
            "Karakter sayisi: %d",
            len(answer)
        )

        return answer

    except Exception:
        logger.exception(
            "History destekli cevap uretirken hata olustu."
        )
        raise