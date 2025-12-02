"""
Consolidated token usage report generator.
Combines BGE-M3 and Groq LLM token estimates.
"""

import os
from token_estimator import BGETokenEstimator
from groq_token_estimator import GroqTokenEstimator


def generate_consolidated_report(
    num_documents: int = 45,
    num_queries: int = 200,
    top_k: int = 3
) -> str:
    """
    Generate a consolidated report combining BGE-M3 and Groq estimates.

    Args:
        num_documents: Number of documents to ingest
        num_queries: Number of queries to process
        top_k: Number of documents retrieved per query

    Returns:
        Formatted consolidated report
    """

    # Initialize estimators
    bge_estimator = BGETokenEstimator()
    groq_estimator = GroqTokenEstimator()

    # Get current document stats
    current_stats = bge_estimator.analyze_documents()
    avg_doc_tokens = int(current_stats.get("avg_tokens_per_doc", 897))

    # BGE-M3 estimates
    bge_ingestion = bge_estimator.estimate_ingestion_tokens(num_documents, avg_doc_tokens)
    bge_queries = bge_estimator.estimate_query_tokens(num_queries)
    bge_total = bge_ingestion["total_tokens"] + bge_queries["total_tokens"]

    # Groq estimates
    groq_estimate = groq_estimator.estimate_rag_query_tokens(
        num_queries=num_queries,
        top_k=top_k,
        avg_doc_tokens=avg_doc_tokens
    )

    # Build consolidated report
    report = []
    report.append("╔" + "=" * 78 + "╗")
    report.append("║" + " " * 20 + "CONSOLIDATED TOKEN USAGE REPORT" + " " * 27 + "║")
    report.append("║" + " " * 78 + "║")
    report.append("║" + " " * 15 + "BGE-M3 Embeddings + Groq LLM (Llama 3.3 70B)" + " " * 19 + "║")
    report.append("╚" + "=" * 78 + "╝")
    report.append("")

    # Scenario description
    report.append("┌" + "─" * 78 + "┐")
    report.append("│ SCENARIO                                                                   │")
    report.append("├" + "─" * 78 + "┤")
    report.append(f"│ • Documents to ingest: {num_documents:>3}                                                    │")
    report.append(f"│ • Average tokens per document: {avg_doc_tokens:>4}                                           │")
    report.append(f"│ • Number of user queries: {num_queries:>3}                                                  │")
    report.append(f"│ • Documents retrieved per query (top_k): {top_k}                                      │")
    report.append("└" + "─" * 78 + "┘")
    report.append("")

    # BGE-M3 Section
    report.append("╔" + "=" * 78 + "╗")
    report.append("║ PART 1: BGE-M3 EMBEDDING MODEL (Creating vector embeddings)               ║")
    report.append("╚" + "=" * 78 + "╝")
    report.append("")
    report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
    report.append("│ Task 1: Document Ingestion (Convert 45 docs to embeddings)                 │")
    report.append("├─────────────────────────────────────────────────────────────────────────────┤")
    report.append(f"│   Documents: {num_documents:>3}                                                               │")
    report.append(f"│   Tokens per document: {avg_doc_tokens:>4}                                                    │")
    report.append(f"│   TOTAL TOKENS: {bge_ingestion['total_tokens']:>10,}                                                │")
    report.append("└─────────────────────────────────────────────────────────────────────────────┘")
    report.append("")
    report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
    report.append("│ Task 2: Query Processing (Convert 200 questions to embeddings)             │")
    report.append("├─────────────────────────────────────────────────────────────────────────────┤")
    report.append(f"│   Queries: {num_queries:>3}                                                               │")
    report.append(f"│   Tokens per query: ~{bge_queries['avg_tokens_per_query']:>2}                                                   │")
    report.append(f"│   TOTAL TOKENS: {bge_queries['total_tokens']:>10,}                                                 │")
    report.append("└─────────────────────────────────────────────────────────────────────────────┘")
    report.append("")
    report.append("╔═════════════════════════════════════════════════════════════════════════════╗")
    report.append(f"║ BGE-M3 SUBTOTAL: {bge_total:>10,} tokens                                            ║")
    report.append("╚═════════════════════════════════════════════════════════════════════════════╝")
    report.append("")
    report.append("")

    # Groq Section
    report.append("╔" + "=" * 78 + "╗")
    report.append("║ PART 2: GROQ LLM (Llama 3.3 70B) - Generating answers                     ║")
    report.append("╚" + "=" * 78 + "╝")
    report.append("")
    report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
    report.append("│ Breakdown per RAG Query:                                                   │")
    report.append("├─────────────────────────────────────────────────────────────────────────────┤")
    report.append(f"│   System prompt: {groq_estimate['tokens_per_query']['system_prompt']:>5} tokens                                             │")
    report.append(f"│   User query: {groq_estimate['tokens_per_query']['user_query']:>5} tokens                                                │")
    report.append(f"│   Context ({top_k} documents): {groq_estimate['tokens_per_query']['context_documents']:>6} tokens                                     │")
    report.append(f"│   LLM response: {groq_estimate['tokens_per_query']['llm_response']:>5} tokens                                              │")
    report.append("│                                                                             │")
    report.append(f"│   INPUT tokens per query: {groq_estimate['tokens_per_query']['total_input']:>6} tokens                                 │")
    report.append(f"│   OUTPUT tokens per query: {groq_estimate['tokens_per_query']['total_output']:>5} tokens                                 │")
    report.append(f"│   ───────────────────────────────────────────────                           │")
    report.append(f"│   TOTAL per query: {groq_estimate['tokens_per_query']['total']:>6} tokens                                       │")
    report.append("└─────────────────────────────────────────────────────────────────────────────┘")
    report.append("")
    report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
    report.append(f"│ Total for {num_queries} queries:                                                      │")
    report.append("├─────────────────────────────────────────────────────────────────────────────┤")
    report.append(f"│   INPUT tokens: {groq_estimate['total_tokens']['input']:>10,}                                            │")
    report.append(f"│   OUTPUT tokens: {groq_estimate['total_tokens']['output']:>10,}                                            │")
    report.append("└─────────────────────────────────────────────────────────────────────────────┘")
    report.append("")
    report.append("╔═════════════════════════════════════════════════════════════════════════════╗")
    report.append(f"║ GROQ LLM SUBTOTAL: {groq_estimate['total_tokens']['total']:>10,} tokens                                      ║")
    report.append("╚═════════════════════════════════════════════════════════════════════════════╝")
    report.append("")
    report.append("")

    # Cost estimate
    input_cost_per_1m = 0.59
    output_cost_per_1m = 0.79
    input_cost = (groq_estimate['total_tokens']['input'] / 1_000_000) * input_cost_per_1m
    output_cost = (groq_estimate['total_tokens']['output'] / 1_000_000) * output_cost_per_1m
    total_cost = input_cost + output_cost

    report.append("╔" + "=" * 78 + "╗")
    report.append("║ COST ESTIMATE (Groq LLM only)                                              ║")
    report.append("╚" + "=" * 78 + "╝")
    report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
    report.append(f"│   Input tokens: ${input_cost:>7.4f}  ({groq_estimate['total_tokens']['input']:>10,} tokens @ ${input_cost_per_1m}/1M)       │")
    report.append(f"│   Output tokens: ${output_cost:>7.4f}  ({groq_estimate['total_tokens']['output']:>10,} tokens @ ${output_cost_per_1m}/1M)       │")
    report.append("│   ──────────────────────────────                                            │")
    report.append(f"│   TOTAL COST: ${total_cost:>7.4f}                                                       │")
    report.append("└─────────────────────────────────────────────────────────────────────────────┘")
    report.append("")
    report.append("NOTE: BGE-M3 embeddings are FREE (running locally), no API costs!")
    report.append("")
    report.append("")

    # Grand totals
    grand_total = bge_total + groq_estimate['total_tokens']['total']

    report.append("╔" + "═" * 78 + "╗")
    report.append("║" + " " * 78 + "║")
    report.append("║" + " " * 26 + "GRAND TOTAL SUMMARY" + " " * 33 + "║")
    report.append("║" + " " * 78 + "║")
    report.append("╠" + "═" * 78 + "╣")
    report.append(f"║  BGE-M3 Embeddings (ingestion + queries):  {bge_total:>10,} tokens            ║")
    report.append(f"║  Groq LLM (200 RAG queries):               {groq_estimate['total_tokens']['total']:>10,} tokens            ║")
    report.append("║  " + "─" * 74 + "  ║")
    report.append(f"║  TOTAL TOKENS:                             {grand_total:>10,} tokens            ║")
    report.append("║" + " " * 78 + "║")
    report.append("╚" + "═" * 78 + "╝")
    report.append("")

    # Important notes
    report.append("┌" + "─" * 78 + "┐")
    report.append("│ IMPORTANT NOTES:                                                           │")
    report.append("├" + "─" * 78 + "┤")
    report.append("│                                                                            │")
    report.append("│ 1. BGE-M3 embeddings run LOCALLY (no API costs)                           │")
    report.append("│    • Only pay for Groq LLM API calls                                      │")
    report.append("│    • Estimated cost for 200 queries: ~$0.35                               │")
    report.append("│                                                                            │")
    report.append("│ 2. Token breakdown:                                                        │")
    report.append("│    • BGE-M3 tokens: For creating vector embeddings                        │")
    report.append("│    • Groq LLM tokens: For generating natural language responses           │")
    report.append("│                                                                            │")
    report.append("│ 3. Actual usage may vary based on:                                        │")
    report.append("│    • Real document content and length                                     │")
    report.append("│    • User query complexity                                                │")
    report.append("│    • Number of documents retrieved (top_k parameter)                      │")
    report.append("│    • LLM response length                                                  │")
    report.append("│                                                                            │")
    report.append("│ 4. Groq is significantly faster and cheaper than alternatives:            │")
    report.append("│    • Ultra-fast inference speed                                           │")
    report.append("│    • Competitive pricing                                                  │")
    report.append("│    • Excellent for production RAG systems                                 │")
    report.append("│                                                                            │")
    report.append("└" + "─" * 78 + "┘")

    return "\n".join(report)


def main():
    """Main function to generate consolidated report."""

    # Generate consolidated report
    report = generate_consolidated_report(
        num_documents=45,
        num_queries=200,
        top_k=3
    )

    print(report)

    # Save report
    output_path = "reports/consolidated_token_report.txt"
    os.makedirs("reports", exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n\nConsolidated report saved to: {output_path}")


if __name__ == "__main__":
    main()
