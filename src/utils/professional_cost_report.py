"""
Professional cost report generator in Markdown format.
Detailed cost analysis for RAG system at scale.
"""

import os
import tiktoken
from datetime import datetime


class ProfessionalCostReportGenerator:
    """Generates professional Markdown cost reports."""

    def __init__(self):
        self.encoding = tiktoken.get_encoding("cl100k_base")

        # Pricing (per 1M tokens)
        self.bge_m3_price_per_1m = 0.010  # $0.010 per 1M tokens
        self.groq_input_price_per_1m = 0.59  # $0.59 per 1M input tokens
        self.groq_output_price_per_1m = 0.79  # $0.79 per 1M output tokens

    def count_tokens(self, text: str) -> int:
        """Count tokens in a text string."""
        return len(self.encoding.encode(text))

    def calculate_costs(
        self,
        num_documents: int,
        avg_tokens_per_doc: int,
        ingestions_per_month: int,
        queries_per_day: int,
        days_per_month: int = 30,
        avg_tokens_per_query: int = 15,
        top_k: int = 3,
        avg_response_tokens: int = 150
    ) -> dict:
        """Calculate detailed costs."""

        queries_per_month = queries_per_day * days_per_month

        # System prompt
        system_prompt = """You are a helpful assistant. Answer the question based ONLY on the provided context.
If the context doesn't contain the answer, say you don't know. Do not use external knowledge."""
        system_tokens = self.count_tokens(system_prompt)

        # ==================== BGE-M3 COSTS ====================

        # Document ingestion
        doc_ingestion_tokens_per_run = num_documents * avg_tokens_per_doc
        total_doc_ingestion_tokens = doc_ingestion_tokens_per_run * ingestions_per_month
        doc_ingestion_cost = (total_doc_ingestion_tokens / 1_000_000) * self.bge_m3_price_per_1m

        # Query embeddings
        total_query_embedding_tokens = queries_per_month * avg_tokens_per_query
        query_embedding_cost = (total_query_embedding_tokens / 1_000_000) * self.bge_m3_price_per_1m

        # Total BGE-M3
        total_bge_tokens = total_doc_ingestion_tokens + total_query_embedding_tokens
        total_bge_cost = doc_ingestion_cost + query_embedding_cost

        # ==================== GROQ LLM COSTS ====================

        # Per query
        input_tokens_per_query = system_tokens + avg_tokens_per_query + (top_k * avg_tokens_per_doc)
        output_tokens_per_query = avg_response_tokens
        total_tokens_per_query = input_tokens_per_query + output_tokens_per_query

        # Monthly totals
        total_groq_input_tokens = input_tokens_per_query * queries_per_month
        total_groq_output_tokens = output_tokens_per_query * queries_per_month
        total_groq_tokens = total_groq_input_tokens + total_groq_output_tokens

        # Groq costs
        groq_input_cost = (total_groq_input_tokens / 1_000_000) * self.groq_input_price_per_1m
        groq_output_cost = (total_groq_output_tokens / 1_000_000) * self.groq_output_price_per_1m
        groq_total_cost = groq_input_cost + groq_output_cost

        # Per query cost
        cost_per_query_groq_input = (input_tokens_per_query / 1_000_000) * self.groq_input_price_per_1m
        cost_per_query_groq_output = (output_tokens_per_query / 1_000_000) * self.groq_output_price_per_1m
        cost_per_query_bge = (avg_tokens_per_query / 1_000_000) * self.bge_m3_price_per_1m
        cost_per_query_total = cost_per_query_groq_input + cost_per_query_groq_output + cost_per_query_bge

        # ==================== TOTALS ====================

        total_monthly_cost = total_bge_cost + groq_total_cost
        total_tokens = total_bge_tokens + total_groq_tokens

        return {
            "params": {
                "num_documents": num_documents,
                "avg_tokens_per_doc": avg_tokens_per_doc,
                "ingestions_per_month": ingestions_per_month,
                "queries_per_day": queries_per_day,
                "queries_per_month": queries_per_month,
                "days_per_month": days_per_month,
                "avg_tokens_per_query": avg_tokens_per_query,
                "top_k": top_k,
                "avg_response_tokens": avg_response_tokens,
                "system_tokens": system_tokens
            },
            "bge_m3": {
                "ingestion": {
                    "tokens_per_run": doc_ingestion_tokens_per_run,
                    "runs_per_month": ingestions_per_month,
                    "total_tokens": total_doc_ingestion_tokens,
                    "cost": doc_ingestion_cost
                },
                "queries": {
                    "tokens_per_query": avg_tokens_per_query,
                    "total_queries": queries_per_month,
                    "total_tokens": total_query_embedding_tokens,
                    "cost": query_embedding_cost
                },
                "total_tokens": total_bge_tokens,
                "total_cost": total_bge_cost,
                "price_per_1m": self.bge_m3_price_per_1m
            },
            "groq": {
                "per_query": {
                    "system_tokens": system_tokens,
                    "user_query_tokens": avg_tokens_per_query,
                    "context_tokens": top_k * avg_tokens_per_doc,
                    "input_tokens": input_tokens_per_query,
                    "output_tokens": output_tokens_per_query,
                    "total_tokens": total_tokens_per_query,
                    "input_cost": cost_per_query_groq_input,
                    "output_cost": cost_per_query_groq_output,
                    "total_cost": cost_per_query_groq_input + cost_per_query_groq_output
                },
                "monthly": {
                    "total_input_tokens": total_groq_input_tokens,
                    "total_output_tokens": total_groq_output_tokens,
                    "total_tokens": total_groq_tokens,
                    "input_cost": groq_input_cost,
                    "output_cost": groq_output_cost,
                    "total_cost": groq_total_cost
                },
                "input_price_per_1m": self.groq_input_price_per_1m,
                "output_price_per_1m": self.groq_output_price_per_1m
            },
            "per_query_total": {
                "bge_tokens": avg_tokens_per_query,
                "bge_cost": cost_per_query_bge,
                "groq_input_tokens": input_tokens_per_query,
                "groq_output_tokens": output_tokens_per_query,
                "groq_total_tokens": total_tokens_per_query,
                "groq_cost": cost_per_query_groq_input + cost_per_query_groq_output,
                "total_tokens": avg_tokens_per_query + total_tokens_per_query,
                "total_cost": cost_per_query_total
            },
            "totals": {
                "total_tokens": total_tokens,
                "total_monthly_cost": total_monthly_cost,
                "total_annual_cost": total_monthly_cost * 12,
                "bge_percentage": (total_bge_cost / total_monthly_cost * 100) if total_monthly_cost > 0 else 0,
                "groq_percentage": (groq_total_cost / total_monthly_cost * 100) if total_monthly_cost > 0 else 0
            }
        }

    def generate_markdown_report(
        self,
        num_documents: int = 100,
        avg_tokens_per_doc: int = 7176,
        ingestions_per_month: int = 5,
        queries_per_day: int = 200
    ) -> str:
        """Generate professional Markdown report."""

        costs = self.calculate_costs(
            num_documents=num_documents,
            avg_tokens_per_doc=avg_tokens_per_doc,
            ingestions_per_month=ingestions_per_month,
            queries_per_day=queries_per_day
        )

        p = costs["params"]
        bge = costs["bge_m3"]
        groq = costs["groq"]
        pq = costs["per_query_total"]
        t = costs["totals"]

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        md = []

        # Header
        md.append("# 📊 RAG System - Professional Cost Analysis Report")
        md.append("")
        md.append(f"**Generated:** {now}")
        md.append("")
        md.append("---")
        md.append("")

        # Executive Summary
        md.append("## 📌 Executive Summary")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| **Monthly Cost** | **${t['total_monthly_cost']:.4f}** |")
        md.append(f"| **Annual Cost** | **${t['total_annual_cost']:.2f}** |")
        md.append(f"| **Cost per Query** | **${pq['total_cost']:.6f}** |")
        md.append(f"| **Queries per Month** | **{p['queries_per_month']:,}** |")
        md.append(f"| **Total Tokens (Monthly)** | **{t['total_tokens']:,}** |")
        md.append("")
        md.append("---")
        md.append("")

        # System Configuration
        md.append("## ⚙️ System Configuration")
        md.append("")
        md.append("### Document Corpus")
        md.append("")
        md.append("| Parameter | Value |")
        md.append("|-----------|-------|")
        md.append(f"| Total Documents | {p['num_documents']} |")
        md.append(f"| Average Tokens per Document | {p['avg_tokens_per_doc']:,} |")
        md.append(f"| Document Re-ingestions per Month | {p['ingestions_per_month']} |")
        md.append("")

        md.append("### Query Configuration")
        md.append("")
        md.append("| Parameter | Value |")
        md.append("|-----------|-------|")
        md.append(f"| Queries per Day | {p['queries_per_day']} |")
        md.append(f"| Queries per Month | {p['queries_per_month']:,} ({p['days_per_month']} days) |")
        md.append(f"| Documents Retrieved per Query (top_k) | {p['top_k']} |")
        md.append(f"| Average Query Length | {p['avg_tokens_per_query']} tokens |")
        md.append(f"| Average Response Length | {p['avg_response_tokens']} tokens |")
        md.append("")
        md.append("---")
        md.append("")

        # Per Query Cost Analysis
        md.append("## 💰 Cost per Query Analysis")
        md.append("")
        md.append("### Token Breakdown (Single Query)")
        md.append("")
        md.append("| Component | Tokens | Cost (USD) |")
        md.append("|-----------|--------|------------|")
        md.append(f"| **BGE-M3 Embedding (User Query)** | {pq['bge_tokens']} | ${pq['bge_cost']:.8f} |")
        md.append(f"| **Groq LLM - System Prompt** | {groq['per_query']['system_tokens']} | - |")
        md.append(f"| **Groq LLM - User Query** | {groq['per_query']['user_query_tokens']} | - |")
        md.append(f"| **Groq LLM - Context ({p['top_k']} docs)** | {groq['per_query']['context_tokens']:,} | - |")
        md.append(f"| **Groq LLM - Total INPUT** | {groq['per_query']['input_tokens']:,} | ${groq['per_query']['input_cost']:.6f} |")
        md.append(f"| **Groq LLM - OUTPUT (Response)** | {groq['per_query']['output_tokens']} | ${groq['per_query']['output_cost']:.6f} |")
        md.append(f"| **TOTAL per Query** | **{pq['total_tokens']:,}** | **${pq['total_cost']:.6f}** |")
        md.append("")
        md.append("---")
        md.append("")

        # BGE-M3 Costs
        md.append("## 🔧 BGE-M3 Embedding Model Costs")
        md.append("")
        md.append(f"**Pricing:** ${bge['price_per_1m']}/1M tokens")
        md.append("")

        md.append("### Subtotal 1: Document Ingestion")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Tokens per Ingestion | {bge['ingestion']['tokens_per_run']:,} |")
        md.append(f"| Ingestions per Month | {bge['ingestion']['runs_per_month']} |")
        md.append(f"| **Total Tokens** | **{bge['ingestion']['total_tokens']:,}** |")
        md.append(f"| **Cost** | **${bge['ingestion']['cost']:.4f}** |")
        md.append("")

        md.append("### Subtotal 2: Query Embeddings")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Tokens per Query | {bge['queries']['tokens_per_query']} |")
        md.append(f"| Total Queries | {bge['queries']['total_queries']:,} |")
        md.append(f"| **Total Tokens** | **{bge['queries']['total_tokens']:,}** |")
        md.append(f"| **Cost** | **${bge['queries']['cost']:.4f}** |")
        md.append("")

        md.append("### BGE-M3 Total")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Ingestion Tokens | {bge['ingestion']['total_tokens']:,} |")
        md.append(f"| Query Tokens | {bge['queries']['total_tokens']:,} |")
        md.append(f"| **Total Tokens** | **{bge['total_tokens']:,}** |")
        md.append(f"| **Total Cost** | **${bge['total_cost']:.4f}** |")
        md.append("")
        md.append("---")
        md.append("")

        # Groq LLM Costs
        md.append("## 🚀 Groq LLM Costs (Llama 3.3 70B Versatile)")
        md.append("")
        md.append(f"**Input Pricing:** ${groq['input_price_per_1m']}/1M tokens")
        md.append("")
        md.append(f"**Output Pricing:** ${groq['output_price_per_1m']}/1M tokens")
        md.append("")
        md.append(f"**Performance:** 394 TPS (Tokens Per Second)")
        md.append("")

        md.append("### Monthly Total")
        md.append("")
        md.append("| Metric | Tokens | Cost (USD) |")
        md.append("|--------|--------|------------|")
        md.append(f"| INPUT Tokens | {groq['monthly']['total_input_tokens']:,} | ${groq['monthly']['input_cost']:.4f} |")
        md.append(f"| OUTPUT Tokens | {groq['monthly']['total_output_tokens']:,} | ${groq['monthly']['output_cost']:.4f} |")
        md.append(f"| **TOTAL** | **{groq['monthly']['total_tokens']:,}** | **${groq['monthly']['total_cost']:.4f}** |")
        md.append("")
        md.append("---")
        md.append("")

        # Summary
        md.append("## 📊 Monthly Cost Summary")
        md.append("")
        md.append("| Service | Tokens | Cost (USD) | % of Total |")
        md.append("|---------|--------|------------|------------|")
        md.append(f"| BGE-M3 Embeddings (Ingestion) | {bge['ingestion']['total_tokens']:,} | ${bge['ingestion']['cost']:.4f} | {(bge['ingestion']['cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| BGE-M3 Embeddings (Queries) | {bge['queries']['total_tokens']:,} | ${bge['queries']['cost']:.4f} | {(bge['queries']['cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| Groq LLM (Input) | {groq['monthly']['total_input_tokens']:,} | ${groq['monthly']['input_cost']:.4f} | {(groq['monthly']['input_cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| Groq LLM (Output) | {groq['monthly']['total_output_tokens']:,} | ${groq['monthly']['output_cost']:.4f} | {(groq['monthly']['output_cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| **TOTAL** | **{t['total_tokens']:,}** | **${t['total_monthly_cost']:.4f}** | **100%** |")
        md.append("")
        md.append("---")
        md.append("")

        # Projections
        md.append("## 📈 Cost Projections")
        md.append("")
        md.append("### Annual Projection")
        md.append("")
        md.append(f"**Total Annual Cost:** ${t['total_annual_cost']:.2f}")
        md.append("")

        md.append("### Scaling Scenarios")
        md.append("")
        md.append("| Queries/Day | Queries/Month | Monthly Cost | Annual Cost |")
        md.append("|-------------|---------------|--------------|-------------|")

        for qpd in [100, 200, 500, 1000, 2000, 5000]:
            temp_costs = self.calculate_costs(
                num_documents=num_documents,
                avg_tokens_per_doc=avg_tokens_per_doc,
                ingestions_per_month=ingestions_per_month,
                queries_per_day=qpd
            )
            md.append(f"| {qpd:,} | {qpd*30:,} | ${temp_costs['totals']['total_monthly_cost']:.2f} | ${temp_costs['totals']['total_annual_cost']:.2f} |")

        md.append("")
        md.append("---")
        md.append("")

        # Optimization
        md.append("## 💡 Cost Optimization Recommendations")
        md.append("")
        md.append("### Option 1: Use Local BGE-M3 (Recommended)")
        md.append("")
        local_savings_monthly = bge['total_cost']
        local_savings_annual = local_savings_monthly * 12
        new_monthly_cost = t['total_monthly_cost'] - bge['total_cost']
        new_annual_cost = new_monthly_cost * 12

        md.append("| Metric | Current (API) | With Local BGE-M3 | Savings |")
        md.append("|--------|---------------|-------------------|---------|")
        md.append(f"| Monthly Cost | ${t['total_monthly_cost']:.4f} | ${new_monthly_cost:.4f} | ${local_savings_monthly:.4f} |")
        md.append(f"| Annual Cost | ${t['total_annual_cost']:.2f} | ${new_annual_cost:.2f} | ${local_savings_annual:.2f} |")
        md.append("")
        md.append("✅ **Running BGE-M3 locally eliminates embedding API costs entirely.**")
        md.append("")

        md.append("### Option 2: Reduce top_k Parameter")
        md.append("")
        md.append("Reducing the number of documents retrieved per query:")
        md.append("")
        md.append("| top_k | Monthly Cost | Savings vs Current |")
        md.append("|-------|--------------|-------------------|")

        for k in [1, 2, 3, 4, 5]:
            temp_costs = self.calculate_costs(
                num_documents=num_documents,
                avg_tokens_per_doc=avg_tokens_per_doc,
                ingestions_per_month=ingestions_per_month,
                queries_per_day=queries_per_day,
                top_k=k
            )
            savings = t['total_monthly_cost'] - temp_costs['totals']['total_monthly_cost']
            md.append(f"| {k} | ${temp_costs['totals']['total_monthly_cost']:.4f} | ${savings:.4f} |")

        md.append("")

        md.append("### Option 3: Implement Query Caching")
        md.append("")
        md.append("Common queries can be cached to avoid repeated LLM calls:")
        md.append("")
        md.append("| Cache Hit Rate | Effective Queries | Monthly Cost | Savings |")
        md.append("|----------------|-------------------|--------------|---------|")

        for cache_rate in [0, 10, 20, 30, 40, 50]:
            effective_queries = p['queries_per_month'] * (100 - cache_rate) / 100
            effective_qpd = effective_queries / 30
            temp_costs = self.calculate_costs(
                num_documents=num_documents,
                avg_tokens_per_doc=avg_tokens_per_doc,
                ingestions_per_month=ingestions_per_month,
                queries_per_day=effective_qpd
            )
            savings = t['total_monthly_cost'] - temp_costs['totals']['total_monthly_cost']
            md.append(f"| {cache_rate}% | {int(effective_queries):,} | ${temp_costs['totals']['total_monthly_cost']:.4f} | ${savings:.4f} |")

        md.append("")
        md.append("---")
        md.append("")

        # Technical Details
        md.append("## 🔍 Technical Details")
        md.append("")
        md.append("### Pricing Structure")
        md.append("")
        md.append("| Service | Type | Price | Unit |")
        md.append("|---------|------|-------|------|")
        md.append(f"| BGE-M3 API | Embeddings | ${self.bge_m3_price_per_1m} | per 1M tokens |")
        md.append(f"| Groq Llama 3.3 70B | Input | ${self.groq_input_price_per_1m} | per 1M tokens |")
        md.append(f"| Groq Llama 3.3 70B | Output | ${self.groq_output_price_per_1m} | per 1M tokens |")
        md.append("")

        md.append("### Model Specifications")
        md.append("")
        md.append("**BGE-M3 Embedding Model:**")
        md.append("- Dimension: 1024")
        md.append("- Max Input Length: 8192 tokens")
        md.append("- Multilingual support")
        md.append("")
        md.append("**Groq Llama 3.3 70B Versatile:**")
        md.append("- Context Window: 128k tokens")
        md.append("- Performance: 394 TPS (Tokens Per Second)")
        md.append("- Ultra-fast inference")
        md.append("- Excellent for production RAG systems")
        md.append("")
        md.append("---")
        md.append("")

        # Footer
        md.append("## 📝 Notes")
        md.append("")
        md.append("- All costs are estimates based on current API pricing")
        md.append("- Actual costs may vary based on real usage patterns")
        md.append("- BGE-M3 can be run locally (FREE) instead of using API")
        md.append("- Groq offers the fastest and most cost-effective LLM inference")
        md.append("- Consider implementing caching for frequently asked questions")
        md.append("- Monitor actual token usage to refine estimates")
        md.append("")
        md.append("---")
        md.append("")
        md.append(f"*Report generated on {now}*")

        return "\n".join(md)


def main():
    """Generate professional cost report."""

    generator = ProfessionalCostReportGenerator()

    # Generate report with new parameters
    report = generator.generate_markdown_report(
        num_documents=100,
        avg_tokens_per_doc=7176,  # Quadruple the original (897 * 8 ≈ 7176)
        ingestions_per_month=5,
        queries_per_day=200
    )

    print(report)
    print("\n" + "="*80)
    print("Report generated successfully!")
    print("="*80 + "\n")

    # Save report
    output_path = "reports/professional_cost_report.md"
    os.makedirs("reports", exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Professional report saved to: {output_path}")


if __name__ == "__main__":
    main()
