"""
Monthly cost calculator for RAG system.
Calculates costs with BGE-M3 API and Groq LLM.
"""

import os
import tiktoken


class MonthlyCostCalculator:
    """Calculates monthly operational costs for RAG system."""

    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")

        # Pricing (per 1M tokens)
        self.bge_m3_price_per_1m = 0.010  # $0.010 per 1M tokens (API)
        self.groq_input_price_per_1m = 0.59  # $0.59 per 1M input tokens
        self.groq_output_price_per_1m = 0.79  # $0.79 per 1M output tokens

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def calculate_monthly_costs(
        self,
        num_documents: int = 50,
        avg_tokens_per_doc: int = 1794,  # 897 * 2 (double the info)
        ingestions_per_month: int = 4,
        queries_per_month: int = 200,
        avg_tokens_per_query: int = 15,
        top_k: int = 3,
        avg_response_tokens: int = 150
    ) -> dict:
        """
        Calculate monthly costs for RAG system.

        Args:
            num_documents: Number of documents in the system
            avg_tokens_per_doc: Average tokens per document
            ingestions_per_month: Number of times documents are re-ingested per month
            queries_per_month: Number of user queries per month
            avg_tokens_per_query: Average tokens per query
            top_k: Number of documents retrieved per query
            avg_response_tokens: Average tokens in LLM response

        Returns:
            Dictionary with cost breakdown
        """

        # ==================== BGE-M3 API COSTS ====================

        # Document ingestion tokens (per ingestion)
        doc_ingestion_tokens_per_run = num_documents * avg_tokens_per_doc

        # Total document ingestion tokens per month
        total_doc_ingestion_tokens = doc_ingestion_tokens_per_run * ingestions_per_month

        # Query embedding tokens per month
        total_query_embedding_tokens = queries_per_month * avg_tokens_per_query

        # Total BGE-M3 tokens
        total_bge_tokens = total_doc_ingestion_tokens + total_query_embedding_tokens

        # BGE-M3 cost
        bge_m3_cost = (total_bge_tokens / 1_000_000) * self.bge_m3_price_per_1m

        # ==================== GROQ LLM COSTS ====================

        # System prompt tokens
        system_prompt = """You are a helpful assistant. Answer the question based ONLY on the provided context.
If the context doesn't contain the answer, say you don't know. Do not use external knowledge."""
        system_tokens = self.count_tokens(system_prompt)

        # Tokens per query
        input_tokens_per_query = (
            system_tokens +
            avg_tokens_per_query +
            (top_k * avg_tokens_per_doc)
        )

        output_tokens_per_query = avg_response_tokens

        # Total Groq tokens per month
        total_groq_input_tokens = input_tokens_per_query * queries_per_month
        total_groq_output_tokens = output_tokens_per_query * queries_per_month

        # Groq costs
        groq_input_cost = (total_groq_input_tokens / 1_000_000) * self.groq_input_price_per_1m
        groq_output_cost = (total_groq_output_tokens / 1_000_000) * self.groq_output_price_per_1m
        groq_total_cost = groq_input_cost + groq_output_cost

        # ==================== TOTAL COSTS ====================

        total_monthly_cost = bge_m3_cost + groq_total_cost

        return {
            "parameters": {
                "num_documents": num_documents,
                "avg_tokens_per_doc": avg_tokens_per_doc,
                "ingestions_per_month": ingestions_per_month,
                "queries_per_month": queries_per_month,
                "avg_tokens_per_query": avg_tokens_per_query,
                "top_k": top_k,
                "avg_response_tokens": avg_response_tokens
            },
            "bge_m3": {
                "doc_ingestion_tokens_per_run": doc_ingestion_tokens_per_run,
                "total_doc_ingestion_tokens": total_doc_ingestion_tokens,
                "total_query_embedding_tokens": total_query_embedding_tokens,
                "total_tokens": total_bge_tokens,
                "cost": bge_m3_cost,
                "price_per_1m": self.bge_m3_price_per_1m
            },
            "groq": {
                "system_tokens": system_tokens,
                "input_tokens_per_query": input_tokens_per_query,
                "output_tokens_per_query": output_tokens_per_query,
                "total_input_tokens": total_groq_input_tokens,
                "total_output_tokens": total_groq_output_tokens,
                "total_tokens": total_groq_input_tokens + total_groq_output_tokens,
                "input_cost": groq_input_cost,
                "output_cost": groq_output_cost,
                "total_cost": groq_total_cost,
                "input_price_per_1m": self.groq_input_price_per_1m,
                "output_price_per_1m": self.groq_output_price_per_1m
            },
            "total": {
                "total_tokens": total_bge_tokens + total_groq_input_tokens + total_groq_output_tokens,
                "total_cost": total_monthly_cost,
                "bge_percentage": (bge_m3_cost / total_monthly_cost * 100) if total_monthly_cost > 0 else 0,
                "groq_percentage": (groq_total_cost / total_monthly_cost * 100) if total_monthly_cost > 0 else 0
            }
        }

    def generate_monthly_report(
        self,
        num_documents: int = 50,
        avg_tokens_per_doc: int = 1794,
        ingestions_per_month: int = 4,
        queries_per_month: int = 200
    ) -> str:
        """Generate a formatted monthly cost report."""

        costs = self.calculate_monthly_costs(
            num_documents=num_documents,
            avg_tokens_per_doc=avg_tokens_per_doc,
            ingestions_per_month=ingestions_per_month,
            queries_per_month=queries_per_month
        )

        report = []
        report.append("╔" + "=" * 78 + "╗")
        report.append("║" + " " * 23 + "MONTHLY COST REPORT - RAG SYSTEM" + " " * 23 + "║")
        report.append("╚" + "=" * 78 + "╝")
        report.append("")

        # Scenario
        report.append("┌" + "─" * 78 + "┐")
        report.append("│ MONTHLY SCENARIO                                                           │")
        report.append("├" + "─" * 78 + "┤")
        report.append(f"│ • Documents in system: {num_documents}                                                    │")
        report.append(f"│ • Average tokens per document: {avg_tokens_per_doc:,} (double the original size)            │")
        report.append(f"│ • Document ingestions per month: {ingestions_per_month}                                           │")
        report.append(f"│ • User queries per month: {queries_per_month}                                                │")
        report.append(f"│ • Documents retrieved per query (top_k): {costs['parameters']['top_k']}                              │")
        report.append("└" + "─" * 78 + "┘")
        report.append("")

        # BGE-M3 Section
        report.append("╔" + "=" * 78 + "╗")
        report.append("║ PART 1: BGE-M3 EMBEDDING API COSTS                                         ║")
        report.append("╚" + "=" * 78 + "╝")
        report.append("")
        report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
        report.append("│ Document Ingestion (Re-processing documents)                               │")
        report.append("├─────────────────────────────────────────────────────────────────────────────┤")
        report.append(f"│   Tokens per ingestion: {costs['bge_m3']['doc_ingestion_tokens_per_run']:>10,}                                   │")
        report.append(f"│   Ingestions per month: {ingestions_per_month:>10}                                       │")
        report.append(f"│   Total tokens/month: {costs['bge_m3']['total_doc_ingestion_tokens']:>10,}                                     │")
        report.append("└─────────────────────────────────────────────────────────────────────────────┘")
        report.append("")
        report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
        report.append("│ Query Embeddings (Converting user questions)                               │")
        report.append("├─────────────────────────────────────────────────────────────────────────────┤")
        report.append(f"│   Queries per month: {queries_per_month:>10}                                           │")
        report.append(f"│   Tokens per query: {costs['parameters']['avg_tokens_per_query']:>10}                                            │")
        report.append(f"│   Total tokens/month: {costs['bge_m3']['total_query_embedding_tokens']:>10,}                                      │")
        report.append("└─────────────────────────────────────────────────────────────────────────────┘")
        report.append("")
        report.append("╔═════════════════════════════════════════════════════════════════════════════╗")
        report.append(f"║ BGE-M3 Total Tokens: {costs['bge_m3']['total_tokens']:>10,}                                         ║")
        report.append(f"║ BGE-M3 Monthly Cost: ${costs['bge_m3']['cost']:>10.4f} (@ ${costs['bge_m3']['price_per_1m']}/1M tokens)               ║")
        report.append("╚═════════════════════════════════════════════════════════════════════════════╝")
        report.append("")
        report.append("")

        # Groq Section
        report.append("╔" + "=" * 78 + "╗")
        report.append("║ PART 2: GROQ LLM API COSTS (Llama 3.3 70B)                                 ║")
        report.append("╚" + "=" * 78 + "╝")
        report.append("")
        report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
        report.append("│ Per Query Breakdown:                                                       │")
        report.append("├─────────────────────────────────────────────────────────────────────────────┤")
        report.append(f"│   System prompt: {costs['groq']['system_tokens']:>5} tokens                                             │")
        report.append(f"│   User query: {costs['parameters']['avg_tokens_per_query']:>5} tokens                                                │")
        report.append(f"│   Context ({costs['parameters']['top_k']} docs × {avg_tokens_per_doc:,}): {costs['parameters']['top_k'] * avg_tokens_per_doc:>6,} tokens                              │")
        report.append(f"│   LLM response: {costs['parameters']['avg_response_tokens']:>5} tokens                                              │")
        report.append("│   ─────────────────────────────────                                         │")
        report.append(f"│   INPUT per query: {costs['groq']['input_tokens_per_query']:>6,} tokens                                      │")
        report.append(f"│   OUTPUT per query: {costs['groq']['output_tokens_per_query']:>5} tokens                                      │")
        report.append("└─────────────────────────────────────────────────────────────────────────────┘")
        report.append("")
        report.append("┌─────────────────────────────────────────────────────────────────────────────┐")
        report.append(f"│ Monthly Total ({queries_per_month} queries):                                              │")
        report.append("├─────────────────────────────────────────────────────────────────────────────┤")
        report.append(f"│   INPUT tokens: {costs['groq']['total_input_tokens']:>10,}                                            │")
        report.append(f"│   OUTPUT tokens: {costs['groq']['total_output_tokens']:>10,}                                            │")
        report.append("└─────────────────────────────────────────────────────────────────────────────┘")
        report.append("")
        report.append("╔═════════════════════════════════════════════════════════════════════════════╗")
        report.append(f"║ Groq INPUT Cost: ${costs['groq']['input_cost']:>10.4f} (@ ${costs['groq']['input_price_per_1m']}/1M tokens)              ║")
        report.append(f"║ Groq OUTPUT Cost: ${costs['groq']['output_cost']:>10.4f} (@ ${costs['groq']['output_price_per_1m']}/1M tokens)              ║")
        report.append(f"║ Groq Total Cost: ${costs['groq']['total_cost']:>10.4f}                                                ║")
        report.append("╚═════════════════════════════════════════════════════════════════════════════╝")
        report.append("")
        report.append("")

        # Grand Total
        report.append("╔" + "═" * 78 + "╗")
        report.append("║" + " " * 78 + "║")
        report.append("║" + " " * 25 + "MONTHLY COST SUMMARY" + " " * 33 + "║")
        report.append("║" + " " * 78 + "║")
        report.append("╠" + "═" * 78 + "╣")
        report.append(f"║  BGE-M3 API (embeddings):              ${costs['bge_m3']['cost']:>10.4f}  ({costs['total']['bge_percentage']:>5.2f}%)       ║")
        report.append(f"║  Groq LLM API (responses):             ${costs['groq']['total_cost']:>10.4f}  ({costs['total']['groq_percentage']:>5.2f}%)       ║")
        report.append("║  " + "─" * 74 + "  ║")
        report.append(f"║  TOTAL MONTHLY COST:                   ${costs['total']['total_cost']:>10.4f}                    ║")
        report.append("║" + " " * 78 + "║")
        report.append("╚" + "═" * 78 + "╝")
        report.append("")

        # Annual projection
        annual_cost = costs['total']['total_cost'] * 12
        report.append("┌" + "─" * 78 + "┐")
        report.append("│ ANNUAL PROJECTION                                                          │")
        report.append("├" + "─" * 78 + "┤")
        report.append(f"│ Estimated annual cost: ${annual_cost:>10.2f}                                           │")
        report.append("└" + "─" * 78 + "┘")
        report.append("")

        # Cost breakdown
        report.append("┌" + "─" * 78 + "┐")
        report.append("│ COST BREAKDOWN BY ACTIVITY                                                 │")
        report.append("├" + "─" * 78 + "┤")

        cost_per_ingestion = (costs['bge_m3']['doc_ingestion_tokens_per_run'] / 1_000_000) * costs['bge_m3']['price_per_1m']
        cost_per_query = (
            (costs['groq']['input_tokens_per_query'] / 1_000_000) * costs['groq']['input_price_per_1m'] +
            (costs['groq']['output_tokens_per_query'] / 1_000_000) * costs['groq']['output_price_per_1m'] +
            (costs['parameters']['avg_tokens_per_query'] / 1_000_000) * costs['bge_m3']['price_per_1m']
        )

        report.append(f"│ Cost per document ingestion: ${cost_per_ingestion:>10.6f}                                  │")
        report.append(f"│ Cost per user query: ${cost_per_query:>10.6f}                                          │")
        report.append("└" + "─" * 78 + "┘")
        report.append("")

        # Important notes
        report.append("┌" + "─" * 78 + "┐")
        report.append("│ IMPORTANT NOTES:                                                           │")
        report.append("├" + "─" * 78 + "┤")
        report.append("│                                                                            │")
        report.append("│ 1. BGE-M3 API vs LOCAL:                                                    │")
        report.append(f"│    • Using BGE-M3 API: ${costs['bge_m3']['cost']:.4f}/month                                         │")
        report.append("│    • Using BGE-M3 LOCAL: $0.00/month (FREE)                               │")
        report.append("│    • Recommendation: Run BGE-M3 locally to save money!                    │")
        report.append("│                                                                            │")
        report.append("│ 2. Document updates cost:                                                  │")
        report.append(f"│    • {ingestions_per_month} re-ingestions/month = ${cost_per_ingestion * ingestions_per_month:.4f} (BGE-M3 API)                    │")
        report.append("│    • With local BGE-M3: $0.00 (FREE)                                      │")
        report.append("│                                                                            │")
        report.append("│ 3. Scaling queries:                                                        │")
        report.append(f"│    • Current: {queries_per_month} queries/month = ${costs['groq']['total_cost']:.4f}                              │")
        report.append(f"│    • 1,000 queries/month = ${cost_per_query * 1000:.4f}                                    │")
        report.append(f"│    • 10,000 queries/month = ${cost_per_query * 10000:.2f}                                   │")
        report.append("│                                                                            │")
        report.append("│ 4. Cost optimization tips:                                                 │")
        report.append("│    • Use local BGE-M3 to eliminate embedding API costs                    │")
        report.append("│    • Reduce top_k to lower Groq input tokens                              │")
        report.append("│    • Cache common queries to avoid repeated LLM calls                     │")
        report.append("│    • Groq is already the cheapest/fastest LLM option                      │")
        report.append("│                                                                            │")
        report.append("└" + "─" * 78 + "┘")

        return "\n".join(report)


def main():
    """Main function to generate monthly cost report."""

    calculator = MonthlyCostCalculator()

    # Generate report with specified parameters
    report = calculator.generate_monthly_report(
        num_documents=50,
        avg_tokens_per_doc=1794,  # 897 * 2 (double the info)
        ingestions_per_month=4,
        queries_per_month=200
    )

    print(report)

    # Save report
    output_path = "reports/monthly_cost_report.txt"
    os.makedirs("reports", exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n\nMonthly cost report saved to: {output_path}")


if __name__ == "__main__":
    main()
