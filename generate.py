"""
generate.py
Generate a grounded answer from retrieved chunks using Groq.
"""

import os
from groq import Groq
from retrieval import retrieve

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GROQ_API_KEY not set. Add it to your .env file."
            )
        _client = Groq(api_key=api_key)
    return _client


SYSTEM_PROMPT = """\
You are a helpful academic advisor for CS majors at Rutgers University-New Brunswick.
You answer questions using ONLY the information provided in the documents below.
Do not use any outside knowledge. Do not speculate.
If the provided documents do not contain enough information to answer the question, \
say exactly: "I don't have enough information on that in my sources."
Be specific and practical. Cite which document(s) your answer comes from at the end \
of your response using the format: Sources: [filename1, filename2]
"""


def _build_context(chunks: list[dict]) -> str:
    parts = []
    for i, chunk in enumerate(chunks):
        parts.append(f"[Document {i+1} - {chunk['source']}]\n{chunk['text']}")
    return "\n\n".join(parts)


def ask(question: str, top_k: int = 5) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.
    Returns dict with keys: answer (str), sources (list[str]), chunks (list[dict])
    """
    chunks = retrieve(question, top_k=top_k)
    context = _build_context(chunks)
    sources = list(dict.fromkeys(c["source"] for c in chunks))  # deduplicated, ordered

    user_message = f"""\
Documents:
{context}

Question: {question}
"""

    client = _get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
        max_tokens=600,
    )

    answer_text = response.choices[0].message.content.strip()

    return {
        "answer": answer_text,
        "sources": sources,
        "chunks": chunks,
    }


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    test_questions = [
        "What is the minimum exam score required to pass CS 112?",
        "Who is the best professor to take for CS 344?",
        "Is CS 213 with Sesh worth taking?",
        "What are the easiest CS electives?",
        "What is the best dining hall on Busch campus?",  # out of scope
    ]

    for q in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {q}")
        result = ask(q)
        print(f"A: {result['answer']}")
        print(f"Sources: {result['sources']}")
        