"""
Token estimator for Groq LLM (Llama 3.3 70B).
Estimates token usage for RAG queries sent to the LLM.
"""

import os
import tiktoken
from typing import Dict


class GroqTokenEstimator:
    """Estimates token usage for Groq LLM API calls."""

    def __init__(self):
        # Llama models use similar tokenization to GPT models
        # cl100k_base is a good approximation
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def estimate_rag_query_tokens(
        self,
        num_queries: int = 200,
        avg_query_length: int = 15,
        top_k: int = 3,
        avg_doc_tokens: int = 897,
        avg_response_tokens: int = 150
    ) -> Dict:
        """
        Estimate tokens for RAG query processing.

        In a RAG query, tokens are used for:
        1. System prompt (instructions to the LLM)
        2. User query
        3. Retrieved context documents (top_k documents)
        4. LLM response (output tokens)

        Args:
            num_queries: Number of queries to process
            avg_query_length: Average tokens per user query
            top_k: Number of documents retrieved per query
            avg_doc_tokens: Average tokens per document
            avg_response_tokens: Average tokens in LLM response

        Returns:
            Dict with token estimates
        """

        # Typical system prompt for RAG
        system_prompt = """You are a helpful assistant. Answer the question based ONLY on the provided context.
If the context doesn't contain the answer, say you don't know. Do not use external knowledge."""

        system_tokens = self.count_tokens(system_prompt)

        # Tokens per query
        input_tokens_per_query = (
            system_tokens +  # System prompt
            avg_query_length +  # User question
            (top_k * avg_doc_tokens)  # Retrieved context documents
        )

        output_tokens_per_query = avg_response_tokens

        total_tokens_per_query = input_tokens_per_query + output_tokens_per_query

        # Total for all queries
        total_input_tokens = input_tokens_per_query * num_queries
        total_output_tokens = output_tokens_per_query * num_queries
        total_tokens = total_tokens_per_query * num_queries

        return {
            "task": "RAG Query Processing (Groq LLM - Llama 3.3 70B)",
            "num_queries": num_queries,
            "top_k_documents": top_k,
            "tokens_per_query": {
                "system_prompt": system_tokens,
                "user_query": avg_query_length,
                "context_documents": top_k * avg_doc_tokens,
                "llm_response": avg_response_tokens,
                "total_input": input_tokens_per_query,
                "total_output": output_tokens_per_query,
                "total": total_tokens_per_query
            },
            "total_tokens": {
                "input": total_input_tokens,
                "output": total_output_tokens,
                "total": total_tokens
            }
        }

    def generate_report(
        self,
        num_queries: int = 200,
        top_k: int = 3,
        avg_doc_tokens: int = 897
    ) -> str:
        """
        Generate a comprehensive token usage report for Groq LLM.

        Args:
            num_queries: Number of queries to estimate
            top_k: Number of documents retrieved per query
            avg_doc_tokens: Average tokens per document

        Returns:
            Formatted report string
        """

        # Estimate RAG queries
        rag_estimate = self.estimate_rag_query_tokens(
            num_queries=num_queries,
            top_k=top_k,
            avg_doc_tokens=avg_doc_tokens
        )

        # Build report
        report = []
        report.append("=" * 80)
        report.append("TOKEN USAGE ESTIMATION REPORT - GROQ LLM (Llama 3.3 70B)")
        report.append("=" * 80)
        report.append("")

        # Query structure breakdown
        report.append("RAG QUERY STRUCTURE (per query):")
        report.append("-" * 80)
        report.append(f"System prompt: {rag_estimate['tokens_per_query']['system_prompt']:,} tokens")
        report.append(f"User query: {rag_estimate['tokens_per_query']['user_query']:,} tokens")
        report.append(f"Context documents ({top_k} docs × {avg_doc_tokens} tokens): {rag_estimate['tokens_per_query']['context_documents']:,} tokens")
        report.append(f"LLM response: {rag_estimate['tokens_per_query']['llm_response']:,} tokens")
        report.append(f"-" * 80)
        report.append(f"Total input tokens per query: {rag_estimate['tokens_per_query']['total_input']:,} tokens")
        report.append(f"Total output tokens per query: {rag_estimate['tokens_per_query']['total_output']:,} tokens")
        report.append(f"TOTAL tokens per query: {rag_estimate['tokens_per_query']['total']:,} tokens")
        report.append("")

        # Total for all queries
        report.append("=" * 80)
        report.append(f"TOTAL TOKEN USAGE FOR {num_queries} QUERIES")
        report.append("=" * 80)
        report.append(f"Total INPUT tokens: {rag_estimate['total_tokens']['input']:,} tokens")
        report.append(f"Total OUTPUT tokens: {rag_estimate['total_tokens']['output']:,} tokens")
        report.append(f"-" * 80)
        report.append(f"GRAND TOTAL: {rag_estimate['total_tokens']['total']:,} tokens")
        report.append("")

        # Pricing estimate (Groq pricing as of 2024)
        report.append("=" * 80)
        report.append("ESTIMATED COST (Groq Llama 3.3 70B Pricing)")
        report.append("=" * 80)
        # Groq pricing for Llama 3.3 70B (approximate)
        input_cost_per_1m = 0.59  # $0.59 per 1M input tokens
        output_cost_per_1m = 0.79  # $0.79 per 1M output tokens

        input_cost = (rag_estimate['total_tokens']['input'] / 1_000_000) * input_cost_per_1m
        output_cost = (rag_estimate['total_tokens']['output'] / 1_000_000) * output_cost_per_1m
        total_cost = input_cost + output_cost

        report.append(f"Input tokens cost: ${input_cost:.4f} ({rag_estimate['total_tokens']['input']:,} tokens @ ${input_cost_per_1m}/1M)")
        report.append(f"Output tokens cost: ${output_cost:.4f} ({rag_estimate['total_tokens']['output']:,} tokens @ ${output_cost_per_1m}/1M)")
        report.append(f"-" * 80)
        report.append(f"TOTAL ESTIMATED COST: ${total_cost:.4f}")
        report.append("")

        # Notes
        report.append("=" * 80)
        report.append("NOTES:")
        report.append("=" * 80)
        report.append("1. These estimates are for LLM API calls only (Groq)")
        report.append("2. This does NOT include BGE-M3 embedding tokens (see separate report)")
        report.append("3. Actual token counts may vary based on:")
        report.append("   - Actual query complexity")
        report.append("   - Actual document content retrieved")
        report.append("   - Actual response length")
        report.append("4. Groq pricing is extremely competitive and subject to change")
        report.append("5. Groq is significantly faster than other LLM providers")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main function to run Groq token estimation."""
    estimator = GroqTokenEstimator()

    # Generate report with specified parameters
    # 200 queries, top_k=3, avg_doc_tokens=897
    report = estimator.generate_report(
        num_queries=200,
        top_k=3,
        avg_doc_tokens=897
    )

    print(report)

    # Save report to file
    output_path = "reports/groq_llm_token_report.txt"
    os.makedirs("reports", exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
