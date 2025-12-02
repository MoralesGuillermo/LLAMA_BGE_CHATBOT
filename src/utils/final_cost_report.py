"""
Final professional cost report generator.
Updated parameters: 50 documents, 7176 tokens each, 200 queries/day, 5 re-ingestions/month
"""

import os
import tiktoken
from datetime import datetime


class FinalCostReportGenerator:
    """Generates final professional Markdown cost report."""

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
        num_documents: int = 50,
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
        md.append("# 📊 RAG System - Cost Analysis Report")
        md.append("")
        md.append(f"**Report Generated:** {now}")
        md.append("")
        md.append(f"**Configuration:** {num_documents} documents × {avg_tokens_per_doc:,} tokens | {queries_per_day} queries/day | {ingestions_per_month} re-ingestions/month")
        md.append("")
        md.append("---")
        md.append("")

        # Executive Summary
        md.append("## 💰 Executive Summary")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| **💵 Monthly Cost** | **${t['total_monthly_cost']:.4f} USD** |")
        md.append(f"| **📅 Annual Cost** | **${t['total_annual_cost']:.2f} USD** |")
        md.append(f"| **🎯 Cost per Query** | **${pq['total_cost']:.6f} USD** |")
        md.append(f"| **📊 Queries per Month** | **{p['queries_per_month']:,}** |")
        md.append(f"| **🔢 Total Tokens (Monthly)** | **{t['total_tokens']:,}** |")
        md.append("")
        md.append("---")
        md.append("")

        # Per Query Analysis
        md.append("## 🎯 Cost per Query Breakdown")
        md.append("")
        md.append("### Token Usage (Single Query)")
        md.append("")
        md.append("| Component | Tokens | Cost (USD) |")
        md.append("|-----------|--------|------------|")
        md.append(f"| **BGE-M3 Embedding** | {pq['bge_tokens']} | ${pq['bge_cost']:.8f} |")
        md.append(f"| **Groq LLM - System Prompt** | {groq['per_query']['system_tokens']} | - |")
        md.append(f"| **Groq LLM - User Query** | {groq['per_query']['user_query_tokens']} | - |")
        md.append(f"| **Groq LLM - Context ({p['top_k']} docs × {p['avg_tokens_per_doc']:,})** | {groq['per_query']['context_tokens']:,} | - |")
        md.append(f"| **Groq LLM - INPUT Total** | **{groq['per_query']['input_tokens']:,}** | **${groq['per_query']['input_cost']:.6f}** |")
        md.append(f"| **Groq LLM - OUTPUT (Response)** | **{groq['per_query']['output_tokens']}** | **${groq['per_query']['output_cost']:.6f}** |")
        md.append(f"| **TOTAL per Query** | **{pq['total_tokens']:,}** | **${pq['total_cost']:.6f}** |")
        md.append("")

        md.append("### Cost Breakdown per Query")
        md.append("")
        md.append("```")
        md.append(f"BGE-M3 Embedding:    ${pq['bge_cost']:.8f}  ({(pq['bge_cost']/pq['total_cost']*100):.2f}%)")
        md.append(f"Groq LLM Input:      ${groq['per_query']['input_cost']:.6f}  ({(groq['per_query']['input_cost']/pq['total_cost']*100):.2f}%)")
        md.append(f"Groq LLM Output:     ${groq['per_query']['output_cost']:.6f}  ({(groq['per_query']['output_cost']/pq['total_cost']*100):.2f}%)")
        md.append("─" * 50)
        md.append(f"TOTAL:               ${pq['total_cost']:.6f}  (100%)")
        md.append("```")
        md.append("")
        md.append("---")
        md.append("")

        # BGE-M3 Costs
        md.append("## 🔧 BGE-M3 Embedding Model Costs")
        md.append("")
        md.append(f"**API Pricing:** ${bge['price_per_1m']}/1M tokens")
        md.append("")

        md.append("### Subtotal 1: Document Ingestion")
        md.append("")
        md.append(f"Re-processing {num_documents} documents {ingestions_per_month} times per month:")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Documents | {num_documents} |")
        md.append(f"| Tokens per Document | {p['avg_tokens_per_doc']:,} |")
        md.append(f"| Tokens per Ingestion | {bge['ingestion']['tokens_per_run']:,} |")
        md.append(f"| Ingestions per Month | {bge['ingestion']['runs_per_month']} |")
        md.append(f"| **Total Tokens/Month** | **{bge['ingestion']['total_tokens']:,}** |")
        md.append(f"| **Monthly Cost** | **${bge['ingestion']['cost']:.4f}** |")
        md.append("")

        md.append("### Subtotal 2: Query Embeddings")
        md.append("")
        md.append(f"Converting {p['queries_per_month']:,} user queries to embeddings:")
        md.append("")
        md.append("| Metric | Value |")
        md.append("|--------|-------|")
        md.append(f"| Queries per Day | {p['queries_per_day']} |")
        md.append(f"| Queries per Month | {bge['queries']['total_queries']:,} |")
        md.append(f"| Tokens per Query | {bge['queries']['tokens_per_query']} |")
        md.append(f"| **Total Tokens/Month** | **{bge['queries']['total_tokens']:,}** |")
        md.append(f"| **Monthly Cost** | **${bge['queries']['cost']:.4f}** |")
        md.append("")

        md.append("### BGE-M3 Total Summary")
        md.append("")
        md.append("| Component | Tokens | Cost (USD) | % of BGE-M3 |")
        md.append("|-----------|--------|------------|-------------|")
        md.append(f"| Document Ingestion | {bge['ingestion']['total_tokens']:,} | ${bge['ingestion']['cost']:.4f} | {(bge['ingestion']['cost']/bge['total_cost']*100):.1f}% |")
        md.append(f"| Query Embeddings | {bge['queries']['total_tokens']:,} | ${bge['queries']['cost']:.4f} | {(bge['queries']['cost']/bge['total_cost']*100):.1f}% |")
        md.append(f"| **TOTAL BGE-M3** | **{bge['total_tokens']:,}** | **${bge['total_cost']:.4f}** | **100%** |")
        md.append("")
        md.append("---")
        md.append("")

        # Groq LLM Costs
        md.append("## 🚀 Groq LLM Costs (Llama 3.3 70B Versatile)")
        md.append("")
        md.append("### Pricing & Performance")
        md.append("")
        md.append("| Specification | Value |")
        md.append("|---------------|-------|")
        md.append(f"| Input Pricing | **${groq['input_price_per_1m']}/1M tokens** |")
        md.append(f"| Output Pricing | **${groq['output_price_per_1m']}/1M tokens** |")
        md.append("| Context Window | 128k tokens |")
        md.append("| Performance | 394 TPS (Tokens Per Second) |")
        md.append("| Throughput | 1.69M tokens/$1 (input) |")
        md.append("| Throughput | 1.27M tokens/$1 (output) |")
        md.append("")

        md.append("### Monthly Total")
        md.append("")
        md.append("| Metric | Tokens | Cost (USD) | % of Groq |")
        md.append("|--------|--------|------------|-----------|")
        md.append(f"| INPUT Tokens | {groq['monthly']['total_input_tokens']:,} | ${groq['monthly']['input_cost']:.4f} | {(groq['monthly']['input_cost']/groq['monthly']['total_cost']*100):.1f}% |")
        md.append(f"| OUTPUT Tokens | {groq['monthly']['total_output_tokens']:,} | ${groq['monthly']['output_cost']:.4f} | {(groq['monthly']['output_cost']/groq['monthly']['total_cost']*100):.1f}% |")
        md.append(f"| **TOTAL Groq** | **{groq['monthly']['total_tokens']:,}** | **${groq['monthly']['total_cost']:.4f}** | **100%** |")
        md.append("")
        md.append("---")
        md.append("")

        # Monthly Summary
        md.append("## 📊 Complete Monthly Cost Summary")
        md.append("")
        md.append("| Service | Tokens | Cost (USD) | % of Total |")
        md.append("|---------|--------|------------|------------|")
        md.append(f"| BGE-M3 (Ingestion) | {bge['ingestion']['total_tokens']:,} | ${bge['ingestion']['cost']:.4f} | {(bge['ingestion']['cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| BGE-M3 (Queries) | {bge['queries']['total_tokens']:,} | ${bge['queries']['cost']:.4f} | {(bge['queries']['cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| Groq LLM (Input) | {groq['monthly']['total_input_tokens']:,} | ${groq['monthly']['input_cost']:.4f} | {(groq['monthly']['input_cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| Groq LLM (Output) | {groq['monthly']['total_output_tokens']:,} | ${groq['monthly']['output_cost']:.4f} | {(groq['monthly']['output_cost']/t['total_monthly_cost']*100):.2f}% |")
        md.append(f"| **TOTAL MONTHLY** | **{t['total_tokens']:,}** | **${t['total_monthly_cost']:.4f}** | **100%** |")
        md.append("")

        md.append("### Visual Cost Distribution")
        md.append("")
        md.append("```")
        md.append("BGE-M3 API:     █ " + f"{t['bge_percentage']:.2f}%")
        md.append("Groq LLM:       " + "█" * 50 + f" {t['groq_percentage']:.2f}%")
        md.append("```")
        md.append("")
        md.append("---")
        md.append("")

        # Projections
        md.append("## 📈 Cost Projections & Scaling")
        md.append("")
        md.append("### Annual Projection")
        md.append("")
        md.append(f"Based on current usage ({queries_per_day} queries/day):")
        md.append("")
        md.append(f"- **Monthly:** ${t['total_monthly_cost']:.2f}")
        md.append(f"- **Quarterly:** ${t['total_monthly_cost']*3:.2f}")
        md.append(f"- **Annual:** ${t['total_annual_cost']:.2f}")
        md.append("")

        md.append("### Scaling Scenarios")
        md.append("")
        md.append("Impact of different query volumes:")
        md.append("")
        md.append("| Queries/Day | Queries/Month | Monthly Cost | Annual Cost |")
        md.append("|-------------|---------------|--------------|-------------|")

        for qpd in [50, 100, 200, 500, 1000, 2000]:
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
        md.append("## 💡 Cost Optimization Strategies")
        md.append("")

        md.append("### Strategy 1: Use Local BGE-M3 ⭐ Recommended")
        md.append("")
        local_savings_monthly = bge['total_cost']
        local_savings_annual = local_savings_monthly * 12
        new_monthly_cost = t['total_monthly_cost'] - bge['total_cost']
        new_annual_cost = new_monthly_cost * 12

        md.append("Run BGE-M3 embedding model locally instead of using the API:")
        md.append("")
        md.append("| Metric | Current (API) | With Local BGE-M3 | Savings |")
        md.append("|--------|---------------|-------------------|---------|")
        md.append(f"| Monthly | ${t['total_monthly_cost']:.4f} | ${new_monthly_cost:.4f} | ${local_savings_monthly:.4f} |")
        md.append(f"| Annual | ${t['total_annual_cost']:.2f} | ${new_annual_cost:.2f} | ${local_savings_annual:.2f} |")
        md.append("")
        md.append("✅ **BGE-M3 is already running locally in your system - you're saving this money!**")
        md.append("")

        md.append("### Strategy 2: Optimize top_k Parameter")
        md.append("")
        md.append("Reduce the number of documents retrieved per query:")
        md.append("")
        md.append("| top_k | Tokens/Query | Cost/Query | Monthly Cost | Savings |")
        md.append("|-------|--------------|------------|--------------|---------|")

        for k in [1, 2, 3, 4, 5]:
            temp_costs = self.calculate_costs(
                num_documents=num_documents,
                avg_tokens_per_doc=avg_tokens_per_doc,
                ingestions_per_month=ingestions_per_month,
                queries_per_day=queries_per_day,
                top_k=k
            )
            savings = t['total_monthly_cost'] - temp_costs['totals']['total_monthly_cost']
            md.append(f"| {k} | {temp_costs['per_query_total']['groq_total_tokens']:,} | ${temp_costs['per_query_total']['total_cost']:.6f} | ${temp_costs['totals']['total_monthly_cost']:.2f} | ${savings:.2f} |")

        md.append("")
        md.append("💡 **top_k=2** offers the best balance between cost and quality")
        md.append("")

        md.append("### Strategy 3: Implement Query Caching")
        md.append("")
        md.append("Cache responses for frequently asked questions:")
        md.append("")
        md.append("| Cache Hit Rate | Effective Queries | Monthly Cost | Annual Savings |")
        md.append("|----------------|-------------------|--------------|----------------|")

        for cache_rate in [0, 10, 20, 30, 40, 50]:
            effective_queries = p['queries_per_month'] * (100 - cache_rate) / 100
            effective_qpd = effective_queries / 30
            temp_costs = self.calculate_costs(
                num_documents=num_documents,
                avg_tokens_per_doc=avg_tokens_per_doc,
                ingestions_per_month=ingestions_per_month,
                queries_per_day=effective_qpd
            )
            savings = (t['total_monthly_cost'] - temp_costs['totals']['total_monthly_cost']) * 12
            md.append(f"| {cache_rate}% | {int(effective_queries):,} | ${temp_costs['totals']['total_monthly_cost']:.2f} | ${savings:.2f} |")

        md.append("")
        md.append("💡 **30% cache hit rate** could save ~${:.2f}/year".format((t['total_monthly_cost'] - self.calculate_costs(num_documents, avg_tokens_per_doc, ingestions_per_month, queries_per_day * 0.7)['totals']['total_monthly_cost']) * 12))
        md.append("")

        md.append("### Combined Optimization Impact")
        md.append("")
        md.append("Combining multiple strategies:")
        md.append("")
        md.append("| Strategy | Monthly Cost | Annual Cost | Total Savings |")
        md.append("|----------|--------------|-------------|---------------|")
        md.append(f"| Current | ${t['total_monthly_cost']:.2f} | ${t['total_annual_cost']:.2f} | - |")

        # Local BGE-M3
        opt1 = new_monthly_cost
        md.append(f"| + Local BGE-M3 | ${opt1:.2f} | ${opt1*12:.2f} | ${local_savings_annual:.2f} |")

        # + top_k=2
        temp_k2 = self.calculate_costs(num_documents, avg_tokens_per_doc, ingestions_per_month, queries_per_day, top_k=2)
        opt2 = temp_k2['totals']['total_monthly_cost'] - bge['total_cost']
        md.append(f"| + top_k=2 | ${opt2:.2f} | ${opt2*12:.2f} | ${(t['total_monthly_cost']-opt2)*12:.2f} |")

        # + 30% cache
        temp_cache = self.calculate_costs(num_documents, avg_tokens_per_doc, ingestions_per_month, queries_per_day * 0.7, top_k=2)
        opt3 = temp_cache['totals']['total_monthly_cost'] - bge['total_cost']
        md.append(f"| + 30% Cache | ${opt3:.2f} | ${opt3*12:.2f} | ${(t['total_monthly_cost']-opt3)*12:.2f} |")

        md.append("")
        md.append("---")
        md.append("")

        # System Configuration
        md.append("## ⚙️ System Configuration Details")
        md.append("")

        md.append("### Document Corpus")
        md.append("")
        md.append("| Parameter | Value |")
        md.append("|-----------|-------|")
        md.append(f"| Total Documents | {p['num_documents']} |")
        md.append(f"| Average Tokens/Document | {p['avg_tokens_per_doc']:,} |")
        md.append(f"| Total Corpus Size | {p['num_documents'] * p['avg_tokens_per_doc']:,} tokens |")
        md.append(f"| Re-ingestions/Month | {p['ingestions_per_month']} |")
        md.append("")

        md.append("### Query Configuration")
        md.append("")
        md.append("| Parameter | Value |")
        md.append("|-----------|-------|")
        md.append(f"| Queries per Day | {p['queries_per_day']} |")
        md.append(f"| Queries per Month | {p['queries_per_month']:,} |")
        md.append(f"| Days per Month | {p['days_per_month']} |")
        md.append(f"| Documents Retrieved (top_k) | {p['top_k']} |")
        md.append(f"| Avg Query Length | {p['avg_tokens_per_query']} tokens |")
        md.append(f"| Avg Response Length | {p['avg_response_tokens']} tokens |")
        md.append("")

        md.append("### API Pricing")
        md.append("")
        md.append("| Service | Type | Price/1M Tokens |")
        md.append("|---------|------|-----------------|")
        md.append(f"| BGE-M3 API | Embeddings | ${self.bge_m3_price_per_1m} |")
        md.append(f"| Groq Llama 3.3 70B | Input | ${self.groq_input_price_per_1m} |")
        md.append(f"| Groq Llama 3.3 70B | Output | ${self.groq_output_price_per_1m} |")
        md.append("")
        md.append("---")
        md.append("")

        # Notes
        md.append("## 📝 Important Notes")
        md.append("")
        md.append("1. **BGE-M3 Local vs API:**")
        md.append("   - Your current system runs BGE-M3 locally (FREE)")
        md.append("   - These calculations show API costs for comparison")
        md.append("   - Keep using local BGE-M3 to save money!")
        md.append("")
        md.append("2. **Cost Drivers:**")
        md.append(f"   - 99%+ of costs come from Groq LLM API calls")
        md.append(f"   - Each query processes {groq['per_query']['context_tokens']:,} tokens of context")
        md.append("   - Reducing top_k has the biggest cost impact")
        md.append("")
        md.append("3. **Groq Performance:**")
        md.append("   - 394 TPS = Ultra-fast inference")
        md.append("   - Best price/performance in the market")
        md.append("   - 128k context window supports large documents")
        md.append("")
        md.append("4. **Recommendations:**")
        md.append("   - ✅ Keep BGE-M3 running locally")
        md.append("   - ✅ Consider reducing top_k to 2 documents")
        md.append("   - ✅ Implement caching for common questions")
        md.append("   - ✅ Monitor actual usage vs estimates")
        md.append("")
        md.append("---")
        md.append("")
        md.append(f"*Report generated: {now}*")
        md.append("")
        md.append("*All costs are estimates based on current API pricing and may vary with actual usage.*")

        return "\n".join(md)


def main():
    """Generate final professional cost report."""

    generator = FinalCostReportGenerator()

    # Generate report with final parameters
    report = generator.generate_markdown_report(
        num_documents=50,
        avg_tokens_per_doc=7176,
        ingestions_per_month=5,
        queries_per_day=200
    )

    print(report)
    print("\n" + "="*80)
    print("✅ Final report generated successfully!")
    print("="*80 + "\n")

    # Save report
    output_path = "reports/final_cost_report.md"
    os.makedirs("reports", exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"📄 Report saved to: {output_path}")


if __name__ == "__main__":
    main()
