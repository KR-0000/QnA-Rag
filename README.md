# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

This system covers student-generated advice about the CS major at Rutgers University-New Brunswick. Specifically, it answers questions about course difficulty, professor reputations, grading policies, study strategies, and career relevance of specific courses. This knowledge is valuable because it reflects real student experience that official channels do not provide. The Rutgers course catalog describes what a class covers but says nothing about which professor to take, how hard exams actually are, or how to recover from failing a required course. Rate My Professors exists but is shallow and unstructured. The most actionable advice lives in Reddit threads where students have extended discussions, share specific details, and correct each other. This system makes that knowledge searchable and answerable in plain language

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->
| # | Source | Thread | URL or file path |
|---|--------|-------------|-----------------|
| 1 | r/rutgers | CS 112 grading requirements, failing, and retake policy | documents/cs112_grading_and_retakes.txt |
| 2 | r/rutgers | CS 112 study tips, resources, and how to get an A | documents/cs112_study_tips.txt |
| 3 | r/rutgers | CS 213 Software Methodology professors and course overview | documents/cs213_software_methodology.txt |
| 4 | r/rutgers | CS 214 Systems Programming difficulty and preparation advice | documents/cs214_systems_programming.txt |
| 5 | r/rutgers | CS 344 Algorithms course, professors, and advice | documents/cs344_algorithms.txt |
| 6 | r/rutgers | CS career advice and which courses best prepare for jobs | documents/cs_career_advice.txt |
| 7 | r/rutgers | Easy and useful CS electives for the BS degree | documents/cs_electives.txt |
| 8 | r/rutgers | Best CS professors at Rutgers-NB | documents/cs_professors.txt |
| 9 | r/rutgers | Required CS courses ranked by difficulty | documents/cs_required_courses_difficulty.txt |
| 10 | r/rutgers | Discrete Math I and II professors and advice | documents/discrete_math.txt |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** The documents are structured as topic-organized advice summaries with short to medium paragraphs. Each paragraph contains one coherent piece of advice, one professor description, or one policy detail. A 500-character chunk is large enough to capture a complete thought without diluting the semantic signal by merging multiple unrelated topics into one embedding. It is small enough that a query about a specific professor or course retrieves the specific relevant paragraph rather than a chunk covering five different topics at once. Overlap of 100 characters prevents a key sentence from being cleanly severed at a chunk boundary. Since facts like a grading threshold or a professor's curve policy are often stated in a single sentence, overlap ensures that no important sentence loses both its beginning and end across two separate chunks.

**Final chunk count:** 115 chunks across 10 documents

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** all-MiniLM-L6-v2 via sentence-transformers, running locally

**Production tradeoff reflection:** all-MiniLM-L6-v2 is a good fit for this project because the corpus is English-only, small enough that latency is not a concern, and it runs locally with no API key or rate limits. The tradeoff is a 256-token context window per chunk, which means very long chunks would be silently truncated, and it is a general-purpose model not fine-tuned on academic advising text. For a production deployment serving real students at scale, the main tradeoffs to weigh would be: a larger model such as text-embedding-3-large from OpenAI or embed-english-v3.0 from Cohere would produce higher-quality embeddings at the cost of API latency and per-call pricing; a model with a longer context window would allow larger chunks if the corpus included longer documents like syllabi or handbooks; a fine-tuned domain-specific model trained on academic advising text would likely handle jargon like course numbers and professor names better than a general-purpose model, but fine-tuning cost is only justified at production scale.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:** The system prompt explicitly instructs the model: "You are a helpful academic advisor for CS majors at Rutgers University-New Brunswick. You answer questions using ONLY the information provided in the documents below. Do not use any outside knowledge. Do not speculate. If the provided documents do not contain enough information to answer the question, say exactly: 'I don't have enough information on that in my sources.'" Retrieved chunks are passed to the model formatted as numbered document blocks with their source filename labeled on each block, so the model has explicit context for attribution.

**How source attribution is surfaced in the response:** Source filenames are extracted programmatically from the retrieved chunk metadata and displayed separately in the UI under a Sources heading, independent of the model's generated text. This guarantees attribution even if the model does not mention sources in its answer. The interface also provides an expandable section showing all retrieved chunks with their RRF scores so users can inspect the raw evidence behind any answer.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the minimum exam score required to pass CS 112? | 270 out of 450 points on exams | "Students must accumulate at least 270 out of 450 possible exam points, roughly 60% on exams." | Relevant | Accurate |
| 2 | Which professor should I take for CS 344 Algorithms? | Bernstein or Assadi recommended; avoid Kalantari | Recommended Cowan, noted Kalantari to avoid and Levin as difficult. Did not mention Bernstein or Assadi. | Relevant | Partially accurate |
| 3 | How hard is CS 214 Systems Programming compared to CS 211? | Most students say CS 214 is harder; depends on C comfort level | "CS 214 is considered harder than CS 211 by most students, though a few find it comparable." | Relevant | Accurate |
| 4 | What are the easiest CS electives for the Rutgers CS degree? | CS 336, CS 210, CS 439, Philosophy Minds Machines Persons | Stated the list was not explicitly provided in documents, despite the information existing in the corpus. | Partially relevant | Inaccurate |
| 5 | Is it worth taking CS 213 with Sesh Venugopal? | Recent reviews are negative; Chang is recommended; Sesh was better in older years | "Recent student reports suggest his teaching quality has significantly declined. Go in prepared for difficult exams and vague project specs." | Relevant | Accurate |

**Retrieval quality:** Relevant  
**Response accuracy:** mostly accurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** "What are the easiest CS electives for the Rutgers CS degree?"

**What the system returned:** The model stated that the easiest electives were not explicitly listed in the documents, even though the document cs_electives.txt contains a section titled "EASIEST CS ELECTIVES (by student consensus)" followed by detailed entries for CS 336, CS 210, CS 439, and others.

**Root cause (tied to a specific pipeline stage):**  This is a chunking and retrieval failure working together. The section header "EASIEST CS ELECTIVES (by student consensus):" was split into its own chunk at the boundary, separated from the actual elective descriptions that follow it. Chunk 1 retrieved for this query contained only the header line and the document metadata, with no actual elective names. The model received a chunk that announced a list was coming but did not contain the list itself. Because the overlap of 100 characters was not large enough to bridge the header and the first substantive entry, the model correctly concluded the retrieved context lacked the answer, but the answer did exist in an adjacent chunk that ranked slightly lower.

**What you would change to fix it:** Increasing chunk overlap from 100 to 200 characters would make it more likely that the header and at least the first entry of the list appear in the same chunk. Alternatively, using a paragraph-aware splitter that keeps section headers attached to their first paragraph would prevent this class of boundary split entirely.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:** Writing the chunking strategy section of planning.md before writing any code forced a concrete decision about chunk size before seeing what the output would look like. Having a specific number (500 characters, 100 overlap) to implement meant the ingestion script had clear parameters from the start rather than requiring trial-and-error tuning mid-implementation. When the failure case in evaluation turned out to be a chunk boundary problem, it was possible to trace it back to an explicit decision in the spec rather than a vague implementation choice.

**One way your implementation diverged from the spec, and why:** The spec described metadata filtering as a potential stretch feature but it was not implemented. With only 10 documents covering a small number of topics, filtering by source or date would have added interface complexity without meaningfully improving answer quality. A user asking about CS 112 already gets results exclusively from CS 112 documents because the retrieval is semantically precise at this corpus size. Metadata filtering becomes useful when the corpus is large enough that off-topic documents regularly appear in results, which was not the case here.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* The Domain section, Documents section, and Chunking Strategy section from planning.md, along with the architecture diagram showing the five pipeline stages and the tools assigned to each.
- *What it produced:* A complete ingest.py script that loaded .txt files, attached source filenames as metadata, and chunked using RecursiveCharacterTextSplitter with the specified parameters. It also produced retrieval.py with ChromaDB semantic search and BM25 hybrid search fused via Reciprocal Rank Fusion.
- *What I changed or overrode:* The initial import paths used langchain.text_splitter and langchain.schema, which are no longer valid in current LangChain versions. These were corrected to langchain_text_splitters and langchain_core.documents. The requirements.txt was also updated to include langchain-text-splitters and langchain-core as explicit dependencies since the generated version had omitted them.

**Instance 2**

- *What I gave the AI:* The grounding requirement (answer only from retrieved context, no outside knowledge), the desired output format (answer text plus source filenames displayed separately), and the Streamlit interface layout description.
- *What it produced:* A generate.py with a system prompt enforcing grounding and an app.py Streamlit interface with a sidebar of example questions, a text input, and answer and sources display sections.
- *What I changed or overrode:* The initial system prompt instructed the model to append a "Sources: [filename]" line at the end of its generated answer, which caused sources to appear twice in the UI since the interface also displays sources programmatically from chunk metadata. The system prompt was updated to remove this instruction and rely entirely on the programmatic attribution, eliminating the duplication.
