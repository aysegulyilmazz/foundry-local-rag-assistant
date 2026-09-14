CHAT_MODEL_ALIAS = "phi-3.5-mini"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

DB_NAME = "rag_database.db"

SIMILARITY_THRESHOLD = 0.35

FALLBACK_MESSAGE = "Bu konuda elimdeki belgelerde yeterli bilgi bulamadım. Lütfen sorunuzu farklı şekilde sormayı deneyin."

SYSTEM_PROMPT = """Sen Türkiye'deki devlet yardımları ve sosyal haklar konusunda bilgi veren bir asistansın.
SADECE sana verilen BAĞLAM bilgisini kullanarak cevap ver.
Cevabın EN FAZLA 3-4 cümle olsun. Madde madde listeleme yapma, sade bir paragraf yaz.
Hiçbir cümleyi veya ifadeyi tekrar etme. Bağlamda olmayan bir bilgiyi ASLA uydurma.
Eğer bağlamda cevap yoksa, bunu açıkça belirt."""