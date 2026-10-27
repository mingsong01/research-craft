# RAG, KGQA, and LLM Checks

Read only for retrieval-augmented generation, knowledge-graph QA, or LLM evaluations.

Separate retrieval from generation. Record retriever configuration, index/corpus version, generator model and version, prompt, decoding, tools, benchmark split, and contamination risk.

Use retrieval metrics for retrieval and task/generation metrics for answers. Retrieval improvement does not by itself establish generation improvement. Analyze oracle retrieval, no-retrieval, and end-to-end variants only when they isolate the research question. Preserve exact model/version and evaluation date when service behavior can change.

Define the evaluation unit and aggregation: query, conversation, document, user, domain, or deployment interval. Freeze corpus snapshot, chunking, embeddings, index settings, reranking, context budget, prompt/template, tool policy, decoding, and stopping behavior. Check benchmark contamination, train/test overlap, near duplicates, answer leakage through metadata, and judge-model familiarity.

Evaluate answer correctness, groundedness/faithfulness, citation precision and recall, abstention, robustness to irrelevant or conflicting context, latency, token/cost budget, and failure modes as the use case requires. Human or model judges need a rubric, blinding/randomization where feasible, calibration examples, and agreement/error analysis. An LLM-as-judge score is another measurement instrument, not ground truth.

For agentic systems, record tool success, invalid calls, recovery behavior, state carryover, termination, safety violations, and task-level completion. Separate model capability from orchestration, tool availability, retrieval quality, and evaluator artifacts.
