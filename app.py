import streamlit as st
from embed import google_client, query_db, LLM_MODEL

st.title("AI RAG Knowledge Base --BobYang")
st.write("Ask questions about childhood cancer research")

question = st.text_input("Enter your question:", placeholder="e.g., What are the common treatments for childhood cancer?")

if st.button("Get Answer") and question:
    with st.spinner("Searching knowledge base and generating response..."):
        # Query the vector database for relevant chunks
        chunks = query_db(question)

        # Build the prompt with context
        prompt = "Please answer user's question according to context\n"
        prompt += f"Question: {question}\n"
        prompt += "Context:\n"
        for c in chunks:
            prompt += f"{c}\n"
            prompt += "-------------\n"

        # Generate response using LLM
        result = google_client.models.generate_content(
            model=LLM_MODEL,
            contents=prompt
        )

        st.subheader("Answer:")
        st.write(result.text)

        with st.expander("View retrieved context chunks"):
            for i, c in enumerate(chunks, 1):
                st.markdown(f"**Chunk {i}:**")
                st.text(c)
                st.divider()
