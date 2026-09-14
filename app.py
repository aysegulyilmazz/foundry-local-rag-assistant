import streamlit as st
import pypdf

from rag_utils import (
    find_relevant,
    generate_answer_with_history,
    rewrite_query,
    ingest_document,
)

import config


st.set_page_config(
    page_title="Devlet Yardımları Asistanı",
    page_icon="🏛️"
)

st.title(
    "🏛️ Devlet Yardımları Asistanı"
)

st.caption(
    "Yerel çalışan, internet gerektirmeyen bir RAG uygulaması "
    "(Foundry Local ile)"
)


with st.sidebar:

    st.subheader(
        "Örnek Sorular"
    )

    example_questions = [
        "Engelli aileme evde bakım için hangi yardımlar var?",
        "KYK bursu nasıl alınır?",
        "İşsizlik ödeneği için kaç gün prim gerekli?",
        "Doğum yardımı ne kadar?",
        "Şehit yakınlarına ne gibi haklar tanınıyor?",
    ]

    for q in example_questions:

        if st.button(
            q,
            use_container_width=True
        ):
            st.session_state.pending_question = q

    st.divider()

    st.subheader(
        "Kendi Belgeni Yükle"
    )

    uploaded_file = st.file_uploader(
        "PDF veya TXT dosyası",
        type=["pdf", "txt"]
    )

    if (
        uploaded_file is not None
        and st.button(
            "Belgeyi İşle ve Ekle"
        )
    ):

        with st.spinner(
            "Belge işleniyor, vektörleştiriliyor..."
        ):

            if uploaded_file.name.lower().endswith(
                ".pdf"
            ):

                reader = pypdf.PdfReader(
                    uploaded_file
                )

                text = "\n".join(
                    page.extract_text() or ""
                    for page in reader.pages
                )

            else:

                text = (
                    uploaded_file
                    .read()
                    .decode("utf-8")
                )

            count = ingest_document(
                uploaded_file.name,
                text
            )

        st.success(
            f"{count} parça eklendi! "
            f"Artık '{uploaded_file.name}' hakkında "
            f"soru sorabilirsin."
        )

    st.divider()

    st.caption(
        f"Model: "
        f"{config.CHAT_MODEL_ALIAS} "
        f"(yerel)"
    )

    st.caption(
        f"Embedding: "
        f"{config.EMBEDDING_MODEL_ALIAS} "
        f"(yerel)"
    )

    st.caption(
        f"Benzerlik eşiği: "
        f"{config.SIMILARITY_THRESHOLD}"
    )

    st.divider()
    st.subheader("📊 Kullanım İstatistikleri")
    from analytics import parse_log_stats
    stats = parse_log_stats()
    col1, col2 = st.columns(2)
    col1.metric("Toplam Arama", stats["total_searches"])
    col2.metric("Ort. Benzerlik", f"{stats['avg_score']:.2f}")
    if stats["top_titles"]:
        st.caption("En çok eşleşen belgeler:")
        for title, count in stats["top_titles"]:
            st.caption(f"• {title}: {count} kez")



if "messages" not in st.session_state:
    st.session_state.messages = []


for msg in st.session_state.messages:

    with st.chat_message(
        msg["role"]
    ):
        st.write(
            msg["content"]
        )



query = st.chat_input(
    "Devlet yardımları hakkında bir soru sor..."
)


# Sidebar'dan örnek soru seçildiyse
if "pending_question" in st.session_state:

    query = (
        st.session_state
        .pending_question
    )

    del st.session_state.pending_question



if query:

    # Yeni soru eklenmeden onceki gecmis
    previous_history = (
        st.session_state
        .messages
        .copy()
    )


    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message(
        "user"
    ):
        st.write(query)


    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Belgeler taranıyor ve cevap hazırlanıyor..."
        ):


            search_query = rewrite_query(
                query,
                previous_history
            )


            results = find_relevant(
                search_query,
                top_k=3
            )


            # Context'e girecek belgeler
            context_results = []




            if (
                not results
                or results[0]["score"]
                < config.SIMILARITY_THRESHOLD
            ):

                answer = (
                    config.FALLBACK_MESSAGE
                )

            else:



                best_score = (
                    results[0]["score"]
                )

                context_results = [
                    r
                    for r in results
                    if (
                        r["score"]
                        >= config.SIMILARITY_THRESHOLD

                        and

                        r["score"]
                        >= best_score - 0.12
                    )
                ]



                context = "\n\n".join(
                    (
                        f"[{r['title']}]\n"
                        f"{r['content']}"
                    )
                    for r in context_results
                )




                answer = (
                    generate_answer_with_history(
                        query,
                        context,
                        previous_history
                    )
                )



            st.write(answer)


            if context_results:

                with st.expander(
                    "📄 Kullanılan kaynaklar"
                ):

                    for r in context_results:

                        st.markdown(
                            f"**{r['title']}** "
                            f"(benzerlik: "
                            f"{r['score']:.2f})"
                        )

                        st.caption(
                            r["content"]
                        )




    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )