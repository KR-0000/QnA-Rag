"""
app.py
Streamlit interface for the Rutgers CS Unofficial Guide RAG system.
Run with: streamlit run app.py
"""

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from generate import ask

st.set_page_config(
    page_title="Rutgers CS Unofficial Guide",
    page_icon="R",
    layout="centered",
)

st.title("Rutgers CS Unofficial Guide")
st.caption(
    "Ask questions about CS courses, professors, and major requirements at Rutgers-NB. "
    "Answers are sourced from real student discussions on r/rutgers."
)

st.divider()

# Example questions sidebar
with st.sidebar:
    st.header("Example questions")
    examples = [
        "What is the minimum score needed to pass CS 112?",
        "Which professor should I take for CS 344 Algorithms?",
        "How hard is systems programming?",
        "What are the easiest CS electives?",
        "Is Sesh a good professor for CS 213?",
        "Which Discrete Math 2 professor is better, Hamidi or Cowan?",
        "What courses are most useful for landing a software engineering job?",
        "How should I prepare for CS 214 over the summer?",
        "What happens if I fail CS 112?",
        "Is CS 344 worth taking as a sophomore?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["prefill"] = ex

# Main input
prefill = st.session_state.pop("prefill", "")

with st.form("query_form", clear_on_submit=False):
    question = st.text_input(
        "Your question",
        value=prefill,
        placeholder="e.g. Who is the best professor for CS 344?",
    )
    submitted = st.form_submit_button("Ask", use_container_width=True)

if submitted and question.strip():
    with st.spinner("Searching and generating answer..."):
        result = ask(question.strip())

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Sources")
    for src in result["sources"]:
        st.markdown(f"- `{src}`")

    with st.expander("Show retrieved chunks"):
        for i, chunk in enumerate(result["chunks"]):
            st.markdown(f"**Chunk {i+1}** — `{chunk['source']}` (RRF score: {chunk['rrf_score']:.4f})")
            st.text(chunk["text"])
            st.divider()

elif submitted and not question.strip():
    st.warning("Please enter a question.")
    