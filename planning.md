# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
The domain is student-generated advice about the CS major at Rutgers University-New Brunswick. This includes course difficulty, professor reputations, study strategies, grading policies, and career advice specific to Rutgers CS courses. This knowledge is valuable because it represents real student experience that is not available through official Rutgers channels. The course catalog describes what a class covers but says nothing about which professor to take, how hard the exams actually are, what students wish they had known, or how to recover from failing a required course. Rate My Professors exists but is shallow and unstructured. The most useful advice lives in Reddit threads where students have extended discussions, share specific details, and correct each other. This RAG system makes that knowledge searchable and answerable in plain language.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
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

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**  500 characters

**Overlap:**  100 characters
 
**Reasoning:**  The documents are structured as topic-organized advice summaries with short to medium-length paragraphs. Each paragraph tends to contain one coherent piece of advice or a description of one professor or policy. A 500-character chunk is large enough to capture a complete thought, such as a full professor description or a complete tip about exam preparation, without diluting the semantic signal by mixing multiple unrelated topics. It is small enough that a query about a specific professor or course will retrieve the specific relevant paragraph rather than a chunk covering five different topics at once.
Overlap of 100 characters prevents splitting a sentence that carries meaningful information across a chunk boundary. Since the key facts in these documents, such as a grading threshold, a professor's curve policy, or a specific course comparison, are often stated in a single sentence, overlap ensures that no important sentence is cleanly severed at both ends.
Chunks smaller than 500 characters would risk producing fragments with too little context to be semantically useful for embedding. Chunks larger than 500 characters would merge advice about different professors or different courses into a single embedding, reducing retrieval precision when a user asks specifically about one course or one professor.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** all-MiniLM-L6-v2 via sentence-transformers (runs locally, no API key required)

**Top-k:** 5

**Production tradeoff reflection:** The all-MiniLM-L6-v2 model is a reasonable choice for this project because the corpus is English-only, small enough that latency is not a concern, and the domain vocabulary (course numbers, professor names, CS concepts) is covered well enough by a general-purpose model. The tradeoff is that it is a smaller model with a 256-token context window per chunk, which means very long chunks would be truncated. For this corpus with 500-character chunks that is not an issue.
For a production deployment serving real students at scale, the tradeoffs to weigh would be: (1) a larger model such as text-embedding-3-large from OpenAI or embed-english-v3.0 from Cohere would produce higher-quality embeddings at the cost of API latency and per-call pricing; (2) a model with a longer context window such as text-embedding-ada-002 would allow larger chunks if the corpus included longer documents like syllabi or handbooks; (3) a model with multilingual support would matter if serving international students, though for Rutgers CS advice in English it is unnecessary; (4) a fine-tuned domain-specific model trained on academic advising text would likely outperform a general-purpose model on jargon like course numbers and professor names, but the fine-tuning cost is only justified at production scale.
Top-k of 5 gives the LLM enough context to produce a complete answer while keeping the prompt short enough that the relevant content is not diluted by loosely related chunks.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What is the minimum exam score required to pass CS 112? | 270 out of 450 points on exams combined |
| 2 | Which professor should I take for CS 344 Algorithms? | Aaron Bernstein or Sepehr Assadi are recommended; avoid Kalantari |
| 3 | How hard is CS 214 Systems Programming compared to CS 211? | Most students say CS 214 is harder than CS 211; difficulty depends heavily on C programming comfort level|
| 4 | What are the easiest CS electives for the Rutgers CS degree? | CS 336 (Databases), CS 210, CS 439; Philosophy Minds Machines and Persons also counts |
| 5 | Is it worth taking CS 213 with Sesh Venugopal? | Recent reviews are negative: brutal exams, AI-reliant teaching, minimal curve; Chang is recommended for easier experience; Sesh was better in older years |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->
 
1. Short chunks from sections that are inherently thin may not carry enough semantic meaning to match a query reliably. For example, the document on Discrete Math II professors has a short section on Michmizos with only two sentences. If a student asks specifically about Michmizos and that chunk does not retrieve, the system cannot answer. This could cause false negatives where the information exists in the corpus but is not surfaced.

2. Professor names and course numbers are not standard vocabulary tokens, which means semantic similarity between a query like "who is good for 344" and a chunk that says "Aaron Bernstein for CS 344" depends on the model recognizing numeric course codes and proper names as meaningful rather than treating them as low-signal tokens. If the embedding model underweights these identifiers, retrieval quality for professor-specific queries will be lower than for concept-based queries.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

<img width="1927" height="4430" alt="Document Chunking and-2026-06-08-231040" src="https://github.com/user-attachments/assets/f77800dc-826f-455b-a9cd-b90b14d71b38" />
     



---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
