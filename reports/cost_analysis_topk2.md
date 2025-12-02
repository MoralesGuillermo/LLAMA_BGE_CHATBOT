# Análisis de Costos - Sistema RAG con Groq y BGE-M3
## Configuración: top_k=2

---

## Resumen Ejecutivo

| Métrica | Valor |
|---------|-------|
| **Costo mensual total** | **$0.0971 USD** |
| **Costo por pregunta** | **$0.00003237 USD** |
| **Volumen mensual** | 3,000 preguntas |
| **Costo embeddings** | $0.0001 USD |
| **Costo LLM** | $0.0970 USD |

---

## 1. Parámetros del Sistema

### 1.1 Volumen de Operaciones
- **Preguntas diarias**: 100
- **Días al mes**: 30
- **Total preguntas/mes**: 3,000

### 1.2 Características de Documentos
- **Número de documentos**: 80
- **Tokens por documento**: 7,176
- **Total tokens corpus**: 573,120 tokens
- **Reingestas mensuales**: 5

### 1.3 Configuración RAG
- **top_k**: 2 documentos recuperados
- **Tokens por contexto**: 14,352 tokens (2 × 7,176)

---

## 2. Modelo de Embeddings: BGE-M3

### 2.1 Pricing
- **Costo**: $0.010 por 1M tokens
- **Costo por token**: $0.00000001

### 2.2 Costos de Ingesta

#### Tokens por Ingesta
```
Tokens totales = 80 documentos × 7,176 tokens/doc
               = 573,120 tokens
```

#### Costo por Ingesta
```
Costo = 573,120 tokens × $0.00000001/token
      = $0.00573120
```

#### Costo Mensual (5 reingestas)
```
Costo mensual = $0.00573120 × 5
              = $0.0286560
```

### 2.3 Costos de Queries

#### Por Query Individual
Cada pregunta del usuario requiere generar un embedding:
```
Tokens promedio/pregunta = ~20 tokens
Costo/query = 20 × $0.00000001
            = $0.0000002
```

#### Mensual (3,000 queries)
```
Total tokens = 3,000 × 20
             = 60,000 tokens

Costo mensual = 60,000 × $0.00000001
              = $0.0006
```

### 2.4 Total BGE-M3

| Concepto | Tokens | Costo USD |
|----------|--------|-----------|
| Ingesta (5×) | 2,865,600 | $0.0287 |
| Queries (3,000×) | 60,000 | $0.0006 |
| **SUBTOTAL EMBEDDINGS** | **2,925,600** | **$0.0293** |

---

## 3. Modelo LLM: Groq Llama 3.3 70B

### 3.1 Pricing
- **Input**: $0.59 por 1M tokens
- **Output**: $0.79 por 1M tokens
- **Velocidad**: 394 TPS (tokens por segundo)

### 3.2 Tokens por Pregunta

#### Input (Prompt + Contexto)
```
Sistema prompt:     ~150 tokens
Instrucciones RAG:  ~50 tokens
Contexto (top_k=2): 14,352 tokens (2 docs × 7,176)
Pregunta usuario:   ~20 tokens
─────────────────────────────────
TOTAL INPUT:        14,572 tokens
```

#### Output (Respuesta)
```
Respuesta promedio: ~200 tokens
```

### 3.3 Costo por Pregunta

#### Input
```
14,572 tokens × ($0.59 / 1,000,000)
= $0.00859748
```

#### Output
```
200 tokens × ($0.79 / 1,000,000)
= $0.000158
```

#### Total por Pregunta
```
$0.00859748 + $0.000158
= $0.00875548 USD/pregunta
```

### 3.4 Costo Mensual (3,000 preguntas)

#### Input Total
```
Tokens: 14,572 × 3,000 = 43,716,000 tokens
Costo:  43,716,000 × ($0.59 / 1,000,000)
      = $25.79244
```

#### Output Total
```
Tokens: 200 × 3,000 = 600,000 tokens
Costo:  600,000 × ($0.79 / 1,000,000)
      = $0.474
```

#### Total LLM Mensual
```
$25.79244 + $0.474 = $26.26644 USD
```

### 3.5 Resumen LLM por Query

| Componente | Tokens | Costo USD |
|------------|--------|-----------|
| Input | 14,572 | $0.00859748 |
| Output | 200 | $0.000158 |
| **Total/pregunta** | **14,772** | **$0.00875548** |

---

## 4. Comparación top_k=2 vs top_k=3

### 4.1 Métricas por Pregunta

| Métrica | top_k=2 | top_k=3 | Diferencia |
|---------|---------|---------|------------|
| **Tokens contexto** | 14,352 | 21,528 | -7,176 (-33%) |
| **Tokens input total** | 14,572 | 21,748 | -7,176 (-33%) |
| **Costo LLM/pregunta** | $0.00875548 | $0.01283152 | -$0.00407604 (-32%) |
| **Tiempo respuesta (est.)** | ~37ms | ~55ms | -18ms (-33%) |

### 4.2 Métricas Mensuales (3,000 queries)

| Métrica | top_k=2 | top_k=3 | Ahorro |
|---------|---------|---------|--------|
| **Tokens LLM input** | 43,716,000 | 65,244,000 | 21,528,000 (-33%) |
| **Costo LLM** | $26.26644 | $38.49612 | $12.22968 (-32%) |
| **Costo total** | $26.2957 | $38.5254 | $12.2297 (-32%) |

---

## 5. Costo Total del Sistema

### 5.1 Desglose Mensual

| Componente | Detalle | Tokens | Costo USD | % Total |
|------------|---------|--------|-----------|---------|
| **Embeddings - Ingesta** | 5 reingestas × 573,120 | 2,865,600 | $0.0287 | 0.11% |
| **Embeddings - Queries** | 3,000 × 20 | 60,000 | $0.0006 | 0.002% |
| **LLM - Input** | 3,000 × 14,572 | 43,716,000 | $25.7924 | 98.19% |
| **LLM - Output** | 3,000 × 200 | 600,000 | $0.4740 | 1.80% |
| **TOTAL MENSUAL** | | **47,241,600** | **$26.2957** | **100%** |

### 5.2 Costo por Pregunta

```
Costo total/mes ÷ 3,000 preguntas
= $26.2957 ÷ 3,000
= $0.00876523 USD/pregunta
```

#### Desglose por Pregunta
- **Embedding query**: $0.0000002 (0.002%)
- **LLM input**: $0.00859748 (98.08%)
- **LLM output**: $0.000158 (1.80%)
- **Embedding ingesta (prorrateado)**: $0.00000956 (0.11%)

---

## 6. Proyecciones y Escalabilidad

### 6.1 Escalado de Volumen

| Preguntas/mes | Costo Embeddings | Costo LLM | Costo Total | $/pregunta |
|---------------|------------------|-----------|-------------|------------|
| 3,000 | $0.0293 | $26.2664 | $26.2957 | $0.00877 |
| 10,000 | $0.0306 | $87.5548 | $87.5854 | $0.00876 |
| 30,000 | $0.0346 | $262.6644 | $262.6990 | $0.00876 |
| 100,000 | $0.0486 | $875.5480 | $875.5966 | $0.00876 |

**Nota**: Costo embeddings incluye 5 reingestas + queries del volumen

### 6.2 Escalado de Documentos (3,000 queries/mes, top_k=2)

| Documentos | Tokens Corpus | Tokens/Query | Costo/Query | Costo Mensual |
|------------|---------------|--------------|-------------|---------------|
| 40 | 287,040 | 7,506 | $0.00451 | $13.53 |
| 80 | 574,080 | 14,792 | $0.00877 | $26.30 |
| 160 | 1,148,160 | 29,364 | $0.01732 | $51.96 |
| 320 | 2,296,320 | 58,508 | $0.03453 | $103.59 |

**⚠️ Nota crítica**: Con documentos grandes (7,176 tokens), top_k=2 ya consume ~14.5K tokens. Considerar:
- **Chunking**: Dividir documentos grandes en chunks de 512-1024 tokens
- **top_k mayor**: Con chunks pequeños se puede usar top_k=5-10 sin explotar el contexto
- **Modelo context window**: Llama 3.3 soporta 128K tokens

---

## 7. Optimizaciones Recomendadas

### 7.1 Reducción de Costos

1. **Implementar chunking inteligente** (ALTA PRIORIDAD)
   - Dividir documentos de 7,176 tokens en chunks de 512-1024 tokens
   - Beneficio: Permite usar top_k mayor sin consumir todo el contexto
   - Ahorro estimado: 50-70% en tokens de input

2. **Caché de respuestas frecuentes**
   - Almacenar respuestas a preguntas comunes
   - Ahorro: ~20-30% en queries repetidas

3. **Ajuste dinámico de top_k**
   - top_k=1 para preguntas simples
   - top_k=2-3 para preguntas complejas
   - Ahorro: 15-25%

4. **Batch processing de reingestas**
   - Reducir de 5 a 2-3 reingestas/mes
   - Ahorro: $0.01-0.02/mes (mínimo)

### 7.2 Mejoras de Calidad (sin impacto de costo significativo)

1. **Reranking**: Implementar reranker ligero post-retrieval
2. **Filtrado por score**: Solo incluir docs con similarity > 0.7
3. **Compresión de contexto**: Resumir documentos largos antes de enviar al LLM

---

## 8. Análisis Comparativo de Modelos

### 8.1 Alternativas de LLM (costo por 3,000 queries con top_k=2)

| Provider | Modelo | Input/1M | Output/1M | Costo Mensual | vs Groq |
|----------|--------|----------|-----------|---------------|---------|
| **Groq** | Llama 3.3 70B | $0.59 | $0.79 | $26.27 | Baseline |
| OpenAI | GPT-4o mini | $0.15 | $0.60 | $6.92 | -73.7% 💰 |
| OpenAI | GPT-4o | $2.50 | $10.00 | $114.93 | +337% |
| Anthropic | Claude 3.5 Haiku | $0.80 | $4.00 | $37.26 | +41.8% |
| DeepSeek | DeepSeek-V3 | $0.27 | $1.10 | $12.43 | -52.7% 💰 |

**Recomendación**: Considerar GPT-4o mini o DeepSeek-V3 para reducir costos significativamente.

### 8.2 Alternativas de Embeddings

| Modelo | Dimensiones | Costo/1M | Calidad | Costo Mensual (queries) |
|--------|-------------|----------|---------|-------------------------|
| **BGE-M3** | 1024 | $0.010 | Excelente | $0.0006 |
| text-embedding-3-small | 1536 | $0.020 | Muy buena | $0.0012 |
| text-embedding-3-large | 3072 | $0.130 | Excelente | $0.0078 |
| Voyage AI | 1024 | $0.100 | Excelente | $0.0060 |

**Recomendación**: BGE-M3 es excelente relación costo-calidad. No cambiar.

---

## 9. Conclusiones y Recomendaciones

### 9.1 Hallazgos Principales

1. ✅ **Embeddings son negligibles**: $0.0293/mes (0.11% del total)
2. ⚠️ **LLM input domina costos**: 98.19% del gasto total
3. 🎯 **top_k=2 ahorra 32%** vs top_k=3 ($12.23/mes con 3K queries)
4. 📈 **Costo por pregunta es estable**: ~$0.00876 independiente del volumen

### 9.2 Acciones Recomendadas

#### Inmediatas (esta semana)
1. ✅ **Mantener top_k=2** - Balance óptimo costo/calidad con docs grandes
2. 🔧 **Implementar logging de costos** - Tracking en tiempo real
3. 📊 **Analizar queries reales** - Identificar patrones de preguntas repetidas

#### Corto plazo (este mes)
1. 🔪 **Implementar chunking** - Dividir documentos en 512-1024 tokens
   - Prioridad ALTA si se quiere escalar
   - Permitirá usar top_k=5-10 sin explotar contexto
2. 💾 **Sistema de caché** - Para preguntas frecuentes
3. 🧪 **Probar GPT-4o mini** - Podría reducir costos 73% con calidad similar

#### Mediano plazo (próximos 3 meses)
1. 🤖 **Router inteligente** - Seleccionar modelo según complejidad
2. 📉 **Reducir reingestas** - De 5 a 2-3/mes si es posible
3. 🔄 **Implementar reranking** - Mejorar relevancia sin incrementar top_k

### 9.3 Resumen de Decisión: top_k=2

**Ventajas**:
- Ahorro del 32% vs top_k=3
- Respuestas más rápidas (~37ms vs ~55ms)
- Menor "ruido" en el contexto
- Adecuado para documentos grandes (7K tokens)

**Desventajas**:
- Menor recall si info está en múltiples docs
- Más sensible a calidad del retriever

**Veredicto**: ✅ **Óptimo para la configuración actual** (docs de 7K tokens). Cuando se implemente chunking, reevaluar incrementando a top_k=5.

---

## 10. Métricas de Monitoreo

### KPIs a Trackear

| Métrica | Target | Alerta |
|---------|--------|--------|
| Costo/pregunta | < $0.01 | > $0.015 |
| Tokens input promedio | < 15,000 | > 20,000 |
| Similarity score promedio | > 0.75 | < 0.60 |
| Cache hit rate | > 20% | < 10% |
| Latencia respuesta | < 500ms | > 1000ms |

---

**Generado**: 2025-12-02
**Configuración**: top_k=2, docs 7,176 tokens, 3,000 queries/mes
**Próxima revisión**: Después de implementar chunking
