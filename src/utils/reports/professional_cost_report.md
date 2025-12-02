# 📊 RAG System - Professional Cost Analysis Report

**Generated:** 2025-12-02 07:45:18

---

## 📌 Executive Summary

| Metric | Value |
|--------|-------|
| **Monthly Cost** | **$77.1410** |
| **Annual Cost** | **$925.69** |
| **Cost per Query** | **$0.012851** |
| **Queries per Month** | **6,000** |
| **Total Tokens (Monthly)** | **134,058,000** |

---

## ⚙️ System Configuration

### Document Corpus

| Parameter | Value |
|-----------|-------|
| Total Documents | 100 |
| Average Tokens per Document | 7,176 |
| Document Re-ingestions per Month | 5 |

### Query Configuration

| Parameter | Value |
|-----------|-------|
| Queries per Day | 200 |
| Queries per Month | 6,000 (30 days) |
| Documents Retrieved per Query (top_k) | 3 |
| Average Query Length | 15 tokens |
| Average Response Length | 150 tokens |

---

## 💰 Cost per Query Analysis

### Token Breakdown (Single Query)

| Component | Tokens | Cost (USD) |
|-----------|--------|------------|
| **BGE-M3 Embedding (User Query)** | 15 | $0.00000015 |
| **Groq LLM - System Prompt** | 37 | - |
| **Groq LLM - User Query** | 15 | - |
| **Groq LLM - Context (3 docs)** | 21,528 | - |
| **Groq LLM - Total INPUT** | 21,580 | $0.012732 |
| **Groq LLM - OUTPUT (Response)** | 150 | $0.000118 |
| **TOTAL per Query** | **21,745** | **$0.012851** |

---

## 🔧 BGE-M3 Embedding Model Costs

**Pricing:** $0.01/1M tokens

### Subtotal 1: Document Ingestion

| Metric | Value |
|--------|-------|
| Tokens per Ingestion | 717,600 |
| Ingestions per Month | 5 |
| **Total Tokens** | **3,588,000** |
| **Cost** | **$0.0359** |

### Subtotal 2: Query Embeddings

| Metric | Value |
|--------|-------|
| Tokens per Query | 15 |
| Total Queries | 6,000 |
| **Total Tokens** | **90,000** |
| **Cost** | **$0.0009** |

### BGE-M3 Total

| Metric | Value |
|--------|-------|
| Ingestion Tokens | 3,588,000 |
| Query Tokens | 90,000 |
| **Total Tokens** | **3,678,000** |
| **Total Cost** | **$0.0368** |

---

## 🚀 Groq LLM Costs (Llama 3.3 70B Versatile)

**Input Pricing:** $0.59/1M tokens

**Output Pricing:** $0.79/1M tokens

**Performance:** 394 TPS (Tokens Per Second)

### Monthly Total

| Metric | Tokens | Cost (USD) |
|--------|--------|------------|
| INPUT Tokens | 129,480,000 | $76.3932 |
| OUTPUT Tokens | 900,000 | $0.7110 |
| **TOTAL** | **130,380,000** | **$77.1042** |

---

## 📊 Monthly Cost Summary

| Service | Tokens | Cost (USD) | % of Total |
|---------|--------|------------|------------|
| BGE-M3 Embeddings (Ingestion) | 3,588,000 | $0.0359 | 0.05% |
| BGE-M3 Embeddings (Queries) | 90,000 | $0.0009 | 0.00% |
| Groq LLM (Input) | 129,480,000 | $76.3932 | 99.03% |
| Groq LLM (Output) | 900,000 | $0.7110 | 0.92% |
| **TOTAL** | **134,058,000** | **$77.1410** | **100%** |

---

## 📈 Cost Projections

### Annual Projection

**Total Annual Cost:** $925.69

### Scaling Scenarios

| Queries/Day | Queries/Month | Monthly Cost | Annual Cost |
|-------------|---------------|--------------|-------------|
| 100 | 3,000 | $38.59 | $463.06 |
| 200 | 6,000 | $77.14 | $925.69 |
| 500 | 15,000 | $192.80 | $2313.58 |
| 1,000 | 30,000 | $385.56 | $4626.74 |
| 2,000 | 60,000 | $771.09 | $9253.04 |
| 5,000 | 150,000 | $1927.66 | $23131.96 |

---

## 💡 Cost Optimization Recommendations

### Option 1: Use Local BGE-M3 (Recommended)

| Metric | Current (API) | With Local BGE-M3 | Savings |
|--------|---------------|-------------------|---------|
| Monthly Cost | $77.1410 | $77.1042 | $0.0368 |
| Annual Cost | $925.69 | $925.25 | $0.44 |

✅ **Running BGE-M3 locally eliminates embedding API costs entirely.**

### Option 2: Reduce top_k Parameter

Reducing the number of documents retrieved per query:

| top_k | Monthly Cost | Savings vs Current |
|-------|--------------|-------------------|
| 1 | $26.3349 | $50.8061 |
| 2 | $51.7379 | $25.4030 |
| 3 | $77.1410 | $0.0000 |
| 4 | $102.5440 | $-25.4030 |
| 5 | $127.9471 | $-50.8061 |

### Option 3: Implement Query Caching

Common queries can be cached to avoid repeated LLM calls:

| Cache Hit Rate | Effective Queries | Monthly Cost | Savings |
|----------------|-------------------|--------------|---------|
| 0% | 6,000 | $77.1410 | $0.0000 |
| 10% | 5,400 | $69.4305 | $7.7105 |
| 20% | 4,800 | $61.7200 | $15.4210 |
| 30% | 4,200 | $54.0094 | $23.1315 |
| 40% | 3,600 | $46.2989 | $30.8420 |
| 50% | 3,000 | $38.5884 | $38.5525 |

---

## 🔍 Technical Details

### Pricing Structure

| Service | Type | Price | Unit |
|---------|------|-------|------|
| BGE-M3 API | Embeddings | $0.01 | per 1M tokens |
| Groq Llama 3.3 70B | Input | $0.59 | per 1M tokens |
| Groq Llama 3.3 70B | Output | $0.79 | per 1M tokens |

### Model Specifications

**BGE-M3 Embedding Model:**
- Dimension: 1024
- Max Input Length: 8192 tokens
- Multilingual support

**Groq Llama 3.3 70B Versatile:**
- Context Window: 128k tokens
- Performance: 394 TPS (Tokens Per Second)
- Ultra-fast inference
- Excellent for production RAG systems

---

## 📝 Notes

- All costs are estimates based on current API pricing
- Actual costs may vary based on real usage patterns
- BGE-M3 can be run locally (FREE) instead of using API
- Groq offers the fastest and most cost-effective LLM inference
- Consider implementing caching for frequently asked questions
- Monitor actual token usage to refine estimates

---

*Report generated on 2025-12-02 07:45:18*