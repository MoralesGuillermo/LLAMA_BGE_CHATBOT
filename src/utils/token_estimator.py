"""
Token estimator for BGE-M3 embedding model.
Estimates token usage for document ingestion and query processing.
"""

import os
from pathlib import Path
from typing import List, Dict
import tiktoken

class BGETokenEstimator:
    """Estimates token usage for BGE-M3 model using tiktoken."""

    def __init__(self):
        # BGE-M3 uses a tokenizer similar to BERT, we'll use cl100k_base as approximation
        # This is a close approximation for multilingual models
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def analyze_documents(self, docs_path: str = "data/docs") -> Dict:
        """
        Analyze existing markdown documents.

        Returns:
            Dict with document statistics
        """
        docs_dir = Path(docs_path)
        if not docs_dir.exists():
            return {"error": "Documents directory not found"}

        md_files = list(docs_dir.glob("*.MD")) + list(docs_dir.glob("*.md"))

        stats = {
            "total_documents": len(md_files),
            "documents": [],
            "total_tokens": 0,
            "total_chars": 0,
            "total_words": 0
        }

        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()

            tokens = self.count_tokens(content)
            words = len(content.split())
            chars = len(content)

            stats["documents"].append({
                "filename": md_file.name,
                "tokens": tokens,
                "words": words,
                "chars": chars
            })

            stats["total_tokens"] += tokens
            stats["total_chars"] += chars
            stats["total_words"] += words

        if len(md_files) > 0:
            stats["avg_tokens_per_doc"] = stats["total_tokens"] / len(md_files)
            stats["avg_words_per_doc"] = stats["total_words"] / len(md_files)
            stats["avg_chars_per_doc"] = stats["total_chars"] / len(md_files)

        return stats

    def estimate_ingestion_tokens(self, num_documents: int, avg_tokens_per_doc: int) -> Dict:
        """
        Estimate tokens for document ingestion (converting docs to embeddings).

        Args:
            num_documents: Number of documents to ingest
            avg_tokens_per_doc: Average tokens per document

        Returns:
            Dict with ingestion estimates
        """
        total_tokens = num_documents * avg_tokens_per_doc

        return {
            "task": "Document Ingestion (BGE-M3 Embeddings)",
            "num_documents": num_documents,
            "avg_tokens_per_doc": avg_tokens_per_doc,
            "total_tokens": total_tokens,
            "description": f"Converting {num_documents} documents to embeddings"
        }

    def estimate_query_tokens(self, num_queries: int, avg_tokens_per_query: int = 15) -> Dict:
        """
        Estimate tokens for query processing (converting queries to embeddings).

        Args:
            num_queries: Number of queries to process
            avg_tokens_per_query: Average tokens per query (default: 15)

        Returns:
            Dict with query estimates
        """
        total_tokens = num_queries * avg_tokens_per_query

        return {
            "task": "Query Processing (BGE-M3 Embeddings)",
            "num_queries": num_queries,
            "avg_tokens_per_query": avg_tokens_per_query,
            "total_tokens": total_tokens,
            "description": f"Converting {num_queries} questions to embeddings"
        }

    def generate_report(self, num_documents: int = 45, num_queries: int = 200) -> str:
        """
        Generate a comprehensive token usage report.

        Args:
            num_documents: Number of documents to estimate (default: 45)
            num_queries: Number of queries to estimate (default: 200)

        Returns:
            Formatted report string
        """
        # Analyze current documents to get average
        current_stats = self.analyze_documents()

        if "error" in current_stats:
            avg_tokens = 500  # Default fallback
        else:
            avg_tokens = int(current_stats.get("avg_tokens_per_doc", 500))

        # Estimate ingestion
        ingestion = self.estimate_ingestion_tokens(num_documents, avg_tokens)

        # Estimate queries
        queries = self.estimate_query_tokens(num_queries)

        # Total
        total_tokens = ingestion["total_tokens"] + queries["total_tokens"]

        # Build report
        report = []
        report.append("=" * 80)
        report.append("TOKEN USAGE ESTIMATION REPORT - BGE-M3 EMBEDDING MODEL")
        report.append("=" * 80)
        report.append("")

        # Current documents analysis
        if "error" not in current_stats:
            report.append("CURRENT DOCUMENTS ANALYSIS:")
            report.append("-" * 80)
            report.append(f"Total documents analyzed: {current_stats['total_documents']}")
            report.append(f"Total tokens (current): {current_stats['total_tokens']:,}")
            report.append(f"Average tokens per document: {int(current_stats['avg_tokens_per_doc']):,}")
            report.append(f"Average words per document: {int(current_stats['avg_words_per_doc']):,}")
            report.append("")

            report.append("Document Details:")
            for doc in current_stats["documents"]:
                report.append(f"  - {doc['filename']}: {doc['tokens']:,} tokens, {doc['words']:,} words")
            report.append("")

        # Ingestion estimation
        report.append("=" * 80)
        report.append("TASK 1: DOCUMENT INGESTION (Converting documents to embeddings)")
        report.append("=" * 80)
        report.append(f"Estimated number of documents: {ingestion['num_documents']}")
        report.append(f"Average tokens per document: {ingestion['avg_tokens_per_doc']:,}")
        report.append(f"TOTAL TOKENS FOR INGESTION: {ingestion['total_tokens']:,}")
        report.append("")

        # Query estimation
        report.append("=" * 80)
        report.append("TASK 2: QUERY PROCESSING (Converting questions to embeddings)")
        report.append("=" * 80)
        report.append(f"Estimated number of queries: {queries['num_queries']}")
        report.append(f"Average tokens per query: {queries['avg_tokens_per_query']}")
        report.append(f"TOTAL TOKENS FOR QUERIES: {queries['total_tokens']:,}")
        report.append("")

        # Summary
        report.append("=" * 80)
        report.append("SUMMARY - TOTAL TOKEN USAGE (BGE-M3)")
        report.append("=" * 80)
        report.append(f"Task 1 - Document Ingestion: {ingestion['total_tokens']:,} tokens")
        report.append(f"Task 2 - Query Processing: {queries['total_tokens']:,} tokens")
        report.append(f"-" * 80)
        report.append(f"GRAND TOTAL: {total_tokens:,} tokens")
        report.append("")
        report.append("NOTE: These are tokens processed by BGE-M3 for creating embeddings.")
        report.append("      This does NOT include tokens sent to the LLM (Groq/DeepSeek).")
        report.append("=" * 80)

        return "\n".join(report)


def main():
    """Main function to run token estimation."""
    estimator = BGETokenEstimator()

    # Generate report with specified parameters
    # 45 documents, 200 queries
    report = estimator.generate_report(num_documents=45, num_queries=200)

    print(report)

    # Save report to file
    output_path = "reports/bge_m3_token_report.txt"
    os.makedirs("reports", exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()
