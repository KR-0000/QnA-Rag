# The Unofficial Guide — Project 1
---

## Domain

This system covers student-generated advice about the CS major at Rutgers University-New Brunswick. Specifically, it answers questions about course difficulty, professor reputations, grading policies, study strategies, and career relevance of specific courses. This knowledge is valuable because it reflects real student experience that official channels do not provide. The Rutgers course catalog describes what a class covers but says nothing about which professor to take, how hard exams actually are, or how to recover from failing a required course. Rate My Professors exists, but it is shallow and unstructured (requiring manual extraction of reviews for each professor). The most actionable advice lives in Reddit threads where students have extended discussions, share specific details, and correct each other. This system makes that knowledge searchable and answerable in plain language.

---

## Document Sources

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

**Chunk size:** 500 characters

**Overlap:** 100 characters

**Why these choices fit your documents:** The documents are structured as topic-organized advice summaries with short to medium paragraphs. Each paragraph contains one coherent piece of advice, one professor description, or one policy detail. A 500-character chunk is large enough to capture a complete thought without diluting the semantic signal by merging multiple unrelated topics into one embedding. It is small enough that a query about a specific professor or course retrieves the specific relevant paragraph rather than a chunk covering five different topics at once. Overlap of 100 characters prevents a key sentence from being cleanly severed at a chunk boundary. Since facts like a grading threshold or a professor's curve policy are often stated in a single sentence, overlap ensures that no important sentence loses both its beginning and end across two separate chunks.

**Final chunk count:** 115 chunks across 10 documents

---

## Sample Chunks

The following 5 chunks are representative examples from the corpus after chunking. Each is self-contained and carries enough context to match a relevant query.

**Chunk 1** — `cs112_grading_and_retakes.txt`
> CS 112 has a mandatory minimum exam score requirement: students must accumulate at least 270 out of 450 possible exam points to pass the class. This is roughly 60% on exams. If you do not meet this threshold, you fail the class regardless of your assignment grades. There is no curve in CS 112. The grading cutoffs are published on the CS 112 course website.

**Chunk 2** — `cs344_algorithms.txt`
> Sepehr Assadi: Highly recommended. Students describe learning a lot from him and that he makes the material accessible. Aaron Bernstein: Well-regarded. Generous curves and assignment policies. Usually 3 out of 4 homework problems are easy to medium difficulty, with one hard problem and sometimes extra credit. Take-home exams are non-cumulative.

**Chunk 3** — `cs_professors.txt`
> Charles (Wes) Cowan: Teaches Discrete II and AI-related courses. Described by many students as their favorite CS professor at Rutgers. Excellent lecturer who makes the material engaging and fun. Cares deeply about students. Generous curves. Homework is tedious and difficult but the learning is rewarding. Midterms are harder than some other professors but curved fairly.

**Chunk 4** — `cs214_systems_programming.txt`
> CS 214 is considered harder than CS 211 (Computer Architecture) by most students, though a few say it felt comparable or easier. The primary reason it is hard is the size and complexity of the projects combined with often vague writeups and disorganized course administration.

**Chunk 5** — `cs_electives.txt`
> CS 336 (Principles of Information and Data Management / Databases): Consistently described as one of the easier electives. Also considered highly useful for careers involving data. Has a significant group project where students typically build web apps. SQL knowledge is valuable for data science, data analytics, and many software engineering roles.

---

## Embedding Model

**Model used:** all-MiniLM-L6-v2 via sentence-transformers, running locally

**Production tradeoff reflection:** all-MiniLM-L6-v2 is a good fit for this project because the corpus is English-only, small enough that latency is not a concern, and it runs locally with no API key or rate limits. The tradeoff is a 256-token context window per chunk, which means very long chunks would be silently truncated, and it is a general-purpose model not fine-tuned on academic advising text. For a production deployment serving real students at scale, the main tradeoffs to weigh would be: a larger model such as text-embedding-3-large from OpenAI or embed-english-v3.0 from Cohere would produce higher-quality embeddings at the cost of API latency and per-call pricing; a model with a longer context window would allow larger chunks if the corpus included longer documents like syllabi or handbooks; a fine-tuned domain-specific model trained on academic advising text would likely handle jargon like course numbers and professor names better than a general-purpose model, but fine-tuning cost is only justified at production scale.

---

## Grounded Generation

**System prompt grounding instruction:** The system prompt explicitly instructs the model: "You are a helpful academic advisor for CS majors at Rutgers University-New Brunswick. You answer questions using ONLY the information provided in the documents below. Do not use any outside knowledge. Do not speculate. If the provided documents do not contain enough information to answer the question, say exactly: 'I don't have enough information on that in my sources.'" Retrieved chunks are passed to the model formatted as numbered document blocks with their source filename labeled on each block, so the model has explicit context for attribution.

**How source attribution is surfaced in the response:** Source filenames are extracted programmatically from the retrieved chunk metadata and displayed separately in the UI under a Sources heading, independent of the model's generated text. This guarantees attribution even if the model does not mention sources in its answer. The interface also provides an expandable section showing all retrieved chunks with their RRF scores so users can inspect the raw evidence behind any answer.

---

## Example Responses

**Example 1 — In-scope query with source attribution**

Query: *What is the minimum score needed to pass CS 112?*

> To pass CS 112, students must accumulate at least 270 out of 450 possible exam points. This is roughly 60% on exams. If you do not meet this threshold, you fail the class regardless of your assignment grades. There is no curve in CS 112.

Sources: `cs112_grading_and_retakes.txt`, `cs_required_courses_difficulty.txt`

---

**Example 2 — In-scope query with source attribution**

Query: *Is Sesh a good professor for CS 213?*

> Historically, Sesh was the choice if you wanted to genuinely learn in CS 213. However, recent student reports suggest his teaching quality has significantly declined. If you must take Sesh, go in prepared for difficult exams and vague project specs. Chang is the clear choice if your priority is GPA or reduced stress.

Sources: `cs213_software_methodology.txt`, `cs344_algorithms.txt`, `cs_required_courses_difficulty.txt`

---

**Example 3 — Out-of-scope query showing refusal**

Query: *What is the best dining hall on Busch campus?*

> I don't have enough information on that in my sources.

Sources: `cs112_grading_and_retakes.txt`, `cs_required_courses_difficulty.txt`, `cs344_algorithms.txt`

The system correctly declined to answer a question outside its domain rather than generating a plausible-sounding response from general knowledge. The sources listed are the closest semantic matches found but none contained relevant content, so the model returned the refusal response as instructed.

---

## Retrieval Test Results

**Query 1:** "What is the minimum score needed to pass CS 112?"

| Rank | Source | Distance | Snippet |
|------|--------|----------|---------|
| 1 | cs112_grading_and_retakes.txt | 0.2619 | "CS 112 has a mandatory minimum exam score requirement: students must accumulate at least 270 out of 450 possible exam points..." |
| 2 | cs112_grading_and_retakes.txt | 0.3755 | "Assignment averages in CS 112 tend to be very high (around 95%) because many students use AI tools..." |
| 3 | cs_required_courses_difficulty.txt | 0.4061 | "CS 112 (Data Structures): 7-8. Concepts are not always intrinsically hard but the exam structure is demanding and the minimum score requirement..." |

Retrieval worked well here. The first chunk contains the precise 270/450 threshold. The third chunk reinforces context about the minimum score requirement in a difficulty rating context. All three results are directly relevant to the query.

---

**Query 2:** "Which professor should I take for CS 344?"

| Rank | Source | Distance | Snippet |
|------|--------|----------|---------|
| 1 | cs344_algorithms.txt | 0.3320 | "Students are generally advised not to delay taking CS 344. It is a required course and getting it out of the way earlier..." |
| 2 | cs344_algorithms.txt | 0.3860 | "Taking algorithms as a sophomore is uncommon but possible..." |
| 3 | cs_professors.txt | 0.3979 | "Teaches Discrete II and AI-related courses. Described by many students as their favorite CS professor at Rutgers..." |

The top two chunks are from the correct document but focus on scheduling rather than professor comparisons. The chunk containing the Bernstein, Assadi, and Kalantari descriptions ranked lower than the scheduling-focused chunks, which is why the generated answer named Cowan but missed Bernstein and Assadi. The relevant professor list exists in the corpus but did not rank in the top 3 for this query.

---

**Query 3:** "What are the easiest CS electives?"

| Rank | Source | Distance | Snippet |
|------|--------|----------|---------|
| 1 | cs_electives.txt | 0.3014 | "EASIEST CS ELECTIVES (by student consensus):" |
| 2 | cs_electives.txt | 0.3258 | "MOST USEFUL CS ELECTIVES (by student consensus for software engineering careers)..." |
| 3 | cs112_grading_and_retakes.txt | 0.3966 | "CS 112 is widely considered one of the harder required courses..." |

The top result is the correct document but retrieves only the section header, not the list beneath it. This is the documented failure case: the 500-character chunking boundary fell between the header and its content, so the model received a chunk that announced a list was coming without the list itself.

---

## Hybrid Search Comparison

The system uses Reciprocal Rank Fusion (RRF) to combine semantic (ChromaDB cosine similarity) and keyword (BM25) results. The following comparison shows top-3 results from each method on three queries.

**Query 1: "What is the minimum score needed to pass CS 112?"**

| Rank | Semantic only | BM25 only | Hybrid (RRF) |
|------|--------------|-----------|--------------|
| 1 | cs112_grading_and_retakes.txt (0.2619) | cs112_grading_and_retakes.txt (15.46) | cs112_grading_and_retakes.txt (0.0328) |
| 2 | cs112_grading_and_retakes.txt (0.3755) | cs_required_courses_difficulty.txt (10.83) | cs_required_courses_difficulty.txt (0.0320) |
| 3 | cs_required_courses_difficulty.txt (0.4061) | cs213_software_methodology.txt (7.65) | cs112_grading_and_retakes.txt (0.0301) |

Both methods agreed on rank 1. BM25 introduced an off-topic result at rank 3 (cs213_software_methodology.txt) because the word "score" appears incidentally in that document. Hybrid replaced it with a second relevant cs112 chunk, improving overall result quality.

**Query 2: "Which professor should I take for CS 344?"**

| Rank | Semantic only | BM25 only | Hybrid (RRF) |
|------|--------------|-----------|--------------|
| 1 | cs344_algorithms.txt (0.3320) | cs_career_advice.txt (7.81) | cs344_algorithms.txt (0.0306) |
| 2 | cs344_algorithms.txt (0.3860) | discrete_math.txt (6.65) | cs213_software_methodology.txt (0.0306) |
| 3 | cs_professors.txt (0.3979) | discrete_math.txt (6.41) | cs344_algorithms.txt (0.0164) |

BM25 performed poorly here, returning career advice and discrete math documents that contain the word "professor" but are unrelated to CS 344. Semantic search correctly focused on the algorithms document. Hybrid preserved the semantic results at the top while filtering out BM25 noise, demonstrating the value of fusion for queries containing proper names and course numbers.

**Query 3: "What are the easiest CS electives?"**

| Rank | Semantic only | BM25 only | Hybrid (RRF) |
|------|--------------|-----------|--------------|
| 1 | cs_electives.txt (0.3014) | cs_electives.txt (9.42) | cs_electives.txt (0.0328) |
| 2 | cs_electives.txt (0.3258) | cs213_software_methodology.txt (5.66) | cs_career_advice.txt (0.0301) |
| 3 | cs112_grading_and_retakes.txt (0.3966) | cs_required_courses_difficulty.txt (5.49) | cs_electives.txt (0.0161) |

Both methods agreed on rank 1. Semantic search returned an off-topic cs112 chunk at rank 3. Hybrid promoted a more relevant career advice chunk instead. Overall hybrid produced the cleanest result set across all three queries by consistently demoting results that only one method surfaced.

---

## Sample Interaction Transcript

**Query:** What happens if I fail CS 112?

**Answer:**
> If you fail CS 112, you will receive an F on your transcript permanently. However, if you retake the class and earn a better grade, the F will no longer be factored into your GPA. In SAS, there is a limit of approximately 3 grade replacements total. The F remains visible on the transcript even after the grade replacement. Students who are freshmen and fail are encouraged to retake the course. To advance in the CS major, you need a C or better in CS 112.

**Sources:** `cs112_grading_and_retakes.txt`, `cs_required_courses_difficulty.txt`

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the minimum exam score required to pass CS 112? | 270 out of 450 points on exams | "Students must accumulate at least 270 out of 450 possible exam points, roughly 60% on exams." | Relevant | Accurate |
| 2 | Which professor should I take for CS 344 Algorithms? | Bernstein or Assadi recommended; avoid Kalantari | Recommended Cowan, noted Kalantari to avoid and Levin as difficult. Did not mention Bernstein or Assadi. | Relevant | Partially accurate |
| 3 | How hard is CS 214 Systems Programming compared to CS 211? | Most students say CS 214 is harder; depends on C comfort level | "CS 214 is considered harder than CS 211 by most students, though a few find it comparable." | Relevant | Accurate |
| 4 | What are the easiest CS electives for the Rutgers CS degree? | CS 336, CS 210, CS 439, Philosophy Minds Machines Persons | Stated the list was not explicitly provided in documents, despite the information existing in the corpus. | Partially relevant | Inaccurate |
| 5 | Is it worth taking CS 213 with Sesh Venugopal? | Recent reviews are negative; Chang is recommended; Sesh was better in older years | "Recent student reports suggest his teaching quality has significantly declined. Go in prepared for difficult exams and vague project specs." | Relevant | Accurate |

---

## Failure Case Analysis

**Question that failed:** "What are the easiest CS electives for the Rutgers CS degree?"

**What the system returned:** The model stated that the easiest electives were not explicitly listed in the documents, even though cs_electives.txt contains a section titled "EASIEST CS ELECTIVES (by student consensus)" followed by detailed entries for CS 336, CS 210, CS 439, and others.

**Root cause (tied to a specific pipeline stage):** This is a chunking and retrieval failure working together. The section header "EASIEST CS ELECTIVES (by student consensus):" was split into its own chunk at the boundary, separated from the actual elective descriptions that follow it. The top retrieved chunk contained only the header line and document metadata with no actual elective names. The model received a chunk that announced a list was coming but did not contain the list itself. Because the overlap of 100 characters was not large enough to bridge the header and the first substantive entry, the model correctly concluded the retrieved context lacked the answer, but the answer existed in an adjacent chunk that ranked slightly lower.

**What you would change to fix it:** Increasing chunk overlap from 100 to 200 characters would make it more likely that the header and at least the first entry of the list appear together in the same chunk. Alternatively, using a paragraph-aware splitter that keeps section headers attached to their first paragraph would prevent this class of boundary split entirely.

---

## Spec Reflection

**One way the spec helped you during implementation:** Writing the chunking strategy section of planning.md before writing any code forced a concrete decision about chunk size before seeing what the output would look like. Having a specific number (500 characters, 100 overlap) to implement meant the ingestion script had clear parameters from the start rather than requiring trial-and-error tuning mid-implementation. When the failure case in evaluation turned out to be a chunk boundary problem, it was possible to trace it back to an explicit decision in the spec rather than a vague implementation choice.

**One way your implementation diverged from the spec, and why:** The spec described metadata filtering as a potential stretch feature but it was not implemented. With only 10 documents covering a small number of topics, filtering by source or date would have added interface complexity without meaningfully improving answer quality. A user asking about CS 112 already gets results exclusively from CS 112 documents because the retrieval is semantically precise at this corpus size. Metadata filtering becomes useful when the corpus is large enough that off-topic documents regularly appear in results, which was not the case here.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The Domain section, Documents section, and Chunking Strategy section from planning.md, along with the architecture diagram showing the five pipeline stages and the tools assigned to each.
- *What it produced:* A complete ingest.py script that loaded .txt files, attached source filenames as metadata, and chunked using RecursiveCharacterTextSplitter with the specified parameters. It also produced retrieval.py with ChromaDB semantic search and BM25 hybrid search fused via Reciprocal Rank Fusion.
- *What I changed or overrode:* The initial import paths used langchain.text_splitter and langchain.schema, which are no longer valid in current LangChain versions. These were corrected to langchain_text_splitters and langchain_core.documents. The requirements.txt was also updated to include langchain-text-splitters and langchain-core as explicit dependencies since the generated version had omitted them.

**Instance 2**

- *What I gave the AI:* The grounding requirement (answer only from retrieved context, no outside knowledge), the desired output format (answer text plus source filenames displayed separately), and the Streamlit interface layout description.
- *What it produced:* A generate.py with a system prompt enforcing grounding and an app.py Streamlit interface with a sidebar of example questions, a text input, and answer and sources display sections.
- *What I changed or overrode:* The initial system prompt instructed the model to append a "Sources: [filename]" line at the end of its generated answer, which caused sources to appear twice in the UI since the interface also displays sources programmatically from chunk metadata. The system prompt was updated to remove this instruction and rely entirely on the programmatic attribution, eliminating the duplication.
