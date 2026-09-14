
from rag_utils import find_relevant, generate_answer, get_chat_client
import config


def main():
    print("Modeller yükleniyor, lütfen bekleyin...\n")
    get_chat_client()  # ilk yükleme burada yapılır

    print("Hazır! Devlet yardımları hakkında soru sorabilirsin.")
    print("Çıkmak için 'quit' yaz.\n")

    while True:
        query = input("Soru: ").strip()
        if query.lower() in ("quit", "exit", "çık"):
            break
        if not query:
            continue

        results = find_relevant(query, top_k=2)

        if not results or results[0]["score"] < config.SIMILARITY_THRESHOLD:
            print(f"\nCevap: {config.FALLBACK_MESSAGE}\n")
            continue

        context = "\n\n".join(
            f"[{r['title']}]\n{r['content']}" for r in results
        )

        messages = [
            {"role": "system", "content": f"{config.SYSTEM_PROMPT}\n\nBAĞLAM:\n{context}"},
            {"role": "user", "content": query},
        ]

        answer = generate_answer(messages)
        print(f"\nCevap: {answer}\n")

        used_titles = ", ".join(r["title"] for r in results)
        print(f"(Kaynak: {used_titles}, en yüksek benzerlik: {results[0]['score']:.2f})\n")


if __name__ == "__main__":
    main()