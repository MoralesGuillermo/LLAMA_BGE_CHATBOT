# 📊 RAG System - Cost Analysis Report

**Report Generated:** 2025-12-02 07:53:52

**Configuration:** 50 documents × 7,176 tokens | 200 queries/day | 5 re-ingestions/month

---

## 💰 Executive Summary

| Metric | Value |
|--------|-------|
| **💵 Monthly Cost** | **$77.1230 USD** |
| **📅 Annual Cost** | **$925.48 USD** |
| **🎯 Cost per Query** | **$0.012851 USD** |
| **📊 Queries per Month** | **6,000** |
| **🔢 Total Tokens (Monthly)** | **132,264,000** |

---

## 🎯 Cost per Query Breakdown

### Token Usage (Single Query)

| Component | Tokens | Cost (USD) |
|-----------|--------|------------|
| **BGE-M3 Embedding** | 15 | $0.00000015 |
| **Groq LLM - System Prompt** | 37 | - |
| **Groq LLM - User Query** | 15 | - |
| **Groq LLM - Context (3 docs × 7,176)** | 21,528 | - |
| **Groq LLM - INPUT Total** | **21,580** | **$0.012732** |
| **Groq LLM - OUTPUT (Response)** | **150** | **$0.000118** |
| **TOTAL per Query** | **21,745** | **$0.012851** |

### Cost Breakdown per Query

```
BGE-M3 Embedding:    $0.00000015  (0.00%)
Groq LLM Input:      $0.012732  (99.08%)
Groq LLM Output:     $0.000118  (0.92%)
──────────────────────────────────────────────────
TOTAL:               $0.012851  (100%)
```

---

## 🔧 BGE-M3 Embedding Model Costs

**API Pricing:** $0.01/1M tokens

### Subtotal 1: Document Ingestion

Re-processing 50 documents 5 times per month:

| Metric | Value |
|--------|-------|
| Documents | 50 |
| Tokens per Document | 7,176 |
| Tokens per Ingestion | 358,800 |
| Ingestions per Month | 5 |
| **Total Tokens/Month** | **1,794,000** |
| **Monthly Cost** | **$0.0179** |

### Subtotal 2: Query Embeddings

Converting 6,000 user queries to embeddings:

| Metric | Value |
|--------|-------|
| Queries per Day | 200 |
| Queries per Month | 6,000 |
| Tokens per Query | 15 |
| **Total Tokens/Month** | **90,000** |
| **Monthly Cost** | **$0.0009** |

### BGE-M3 Total Summary

| Component | Tokens | Cost (USD) | % of BGE-M3 |
|-----------|--------|------------|-------------|
| Document Ingestion | 1,794,000 | $0.0179 | 95.2% |
| Query Embeddings | 90,000 | $0.0009 | 4.8% |
| **TOTAL BGE-M3** | **1,884,000** | **$0.0188** | **100%** |

---

## 🚀 Groq LLM Costs (Llama 3.3 70B Versatile)

### Pricing & Performance

| Specification | Value |
|---------------|-------|
| Input Pricing | **$0.59/1M tokens** |
| Output Pricing | **$0.79/1M tokens** |
| Context Window | 128k tokens |
| Performance | 394 TPS (Tokens Per Second) |
| Throughput | 1.69M tokens/$1 (input) |
| Throughput | 1.27M tokens/$1 (output) |

### Monthly Total

| Metric | Tokens | Cost (USD) | % of Groq |
|--------|--------|------------|-----------|
| INPUT Tokens | 129,480,000 | $76.3932 | 99.1% |
| OUTPUT Tokens | 900,000 | $0.7110 | 0.9% |
| **TOTAL Groq** | **130,380,000** | **$77.1042** | **100%** |

---

## 📊 Complete Monthly Cost Summary

| Service | Tokens | Cost (USD) | % of Total |
|---------|--------|------------|------------|
| BGE-M3 (Ingestion) | 1,794,000 | $0.0179 | 0.02% |
| BGE-M3 (Queries) | 90,000 | $0.0009 | 0.00% |
| Groq LLM (Input) | 129,480,000 | $76.3932 | 99.05% |
| Groq LLM (Output) | 900,000 | $0.7110 | 0.92% |
| **TOTAL MONTHLY** | **132,264,000** | **$77.1230** | **100%** |

### Visual Cost Distribution

```
BGE-M3 API:     █ 0.02%
Groq LLM:       ██████████████████████████████████████████████████ 99.98%
```

---

## 📈 Cost Projections & Scaling

### Annual Projection

Based on current usage (200 queries/day):

- **Monthly:** $77.12
- **Quarterly:** $231.37
- **Annual:** $925.48

### Scaling Scenarios

Impact of different query volumes:

| Queries/Day | Queries/Month | Monthly Cost | Annual Cost |
|-------------|---------------|--------------|-------------|
| 50 | 1,500 | $19.29 | $231.53 |
| 100 | 3,000 | $38.57 | $462.85 |
| 200 | 6,000 | $77.12 | $925.48 |
| 500 | 15,000 | $192.78 | $2313.37 |
| 1,000 | 30,000 | $385.54 | $4626.52 |
| 2,000 | 60,000 | $771.07 | $9252.83 |

---

## 💡 Cost Optimization Strategies

### Strategy 1: Use Local BGE-M3 ⭐ Recommended

Run BGE-M3 embedding model locally instead of using the API:

| Metric | Current (API) | With Local BGE-M3 | Savings |
|--------|---------------|-------------------|---------|
| Monthly | $77.1230 | $77.1042 | $0.0188 |
| Annual | $925.48 | $925.25 | $0.23 |

✅ **BGE-M3 is already running locally in your system - you're saving this money!**

### Strategy 2: Optimize top_k Parameter

Reduce the number of documents retrieved per query:

| top_k | Tokens/Query | Cost/Query | Monthly Cost | Savings |
|-------|--------------|------------|--------------|---------|
| 1 | 7,378 | $0.004383 | $26.32 | $50.81 |
| 2 | 14,554 | $0.008617 | $51.72 | $25.40 |
| 3 | 21,730 | $0.012851 | $77.12 | $0.00 |
| 4 | 28,906 | $0.017085 | $102.53 | $-25.40 |
| 5 | 36,082 | $0.021319 | $127.93 | $-50.81 |

💡 **top_k=2** offers the best balance between cost and quality

### Strategy 3: Implement Query Caching

Cache responses for frequently asked questions:

| Cache Hit Rate | Effective Queries | Monthly Cost | Annual Savings |
|----------------|-------------------|--------------|----------------|
| 0% | 6,000 | $77.12 | $0.00 |
| 10% | 5,400 | $69.41 | $92.53 |
| 20% | 4,800 | $61.70 | $185.05 |
| 30% | 4,200 | $53.99 | $277.58 |
| 40% | 3,600 | $46.28 | $370.10 |
| 50% | 3,000 | $38.57 | $462.63 |

💡 **30% cache hit rate** could save ~$277.58/year

### Combined Optimization Impact

Combining multiple strategies:

| Strategy | Monthly Cost | Annual Cost | Total Savings |
|----------|--------------|-------------|---------------|
| Current | $77.12 | $925.48 | - |
| + Local BGE-M3 | $77.10 | $925.25 | $0.23 |
| + top_k=2 | $51.70 | $620.41 | $305.06 |
| + 30% Cache | $36.19 | $434.29 | $491.19 |

---

## ⚙️ System Configuration Details

### Document Corpus

| Parameter | Value |
|-----------|-------|
| Total Documents | 50 |
| Average Tokens/Document | 7,176 |
| Total Corpus Size | 358,800 tokens |
| Re-ingestions/Month | 5 |

### Query Configuration

| Parameter | Value |
|-----------|-------|
| Queries per Day | 200 |
| Queries per Month | 6,000 |
| Days per Month | 30 |
| Documents Retrieved (top_k) | 3 |
| Avg Query Length | 15 tokens |
| Avg Response Length | 150 tokens |

### API Pricing

| Service | Type | Price/1M Tokens |
|---------|------|-----------------|
| BGE-M3 API | Embeddings | $0.01 |
| Groq Llama 3.3 70B | Input | $0.59 |
| Groq Llama 3.3 70B | Output | $0.79 |

---

## 📝 Important Notes

1. **BGE-M3 Local vs API:**
   - Your current system runs BGE-M3 locally (FREE)
   - These calculations show API costs for comparison
   - Keep using local BGE-M3 to save money!

2. **Cost Drivers:**
   - 99%+ of costs come from Groq LLM API calls
   - Each query processes 21,528 tokens of context
   - Reducing top_k has the biggest cost impact

3. **Groq Performance:**
   - 394 TPS = Ultra-fast inference
   - Best price/performance in the market
   - 128k context window supports large documents

4. **Recommendations:**
   - ✅ Keep BGE-M3 running locally
   - ✅ Consider reducing top_k to 2 documents
   - ✅ Implement caching for common questions
   - ✅ Monitor actual usage vs estimates

---

*Report generated: 2025-12-02 07:53:52*

*All costs are estimates based on current API pricing and may vary with actual usage.*