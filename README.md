# Sistema RAG - BGE-M3 + ChromaDB + Groq/DeepSeek

Sistema completo de Recuperación Aumentada por Generación (RAG) que utiliza:
- **BGE-M3** para generar embeddings semánticos (1024 dimensiones)
- **ChromaDB** para almacenamiento vectorial con HNSW
- **Groq API** (ultra-rápido, recomendado, Llama 3.3 70B) o **DeepSeek API** como modelo de lenguaje

## 📋 Características

- ✅ Procesamiento de documentos Markdown (.md)
- ✅ Generación de embeddings con BGE-M3
- ✅ Almacenamiento vectorial en ChromaDB (sin configuración, persistencia automática)
- ✅ Búsqueda semántica con similitud coseno y HNSW
- ✅ **Groq API con Llama 3.3 70B** (ultra-rápido, 10-20x más rápido que alternativas)
- ✅ Alternativa DeepSeek API
- ✅ **Chatbot interactivo por consola** con historial de conversación
- ✅ Modo de consultas únicas CLI
- ✅ División opcional de documentos en chunks
- ✅ Manejo robusto de errores

## 🏗️ Estructura del Proyecto

```
LLAMA_BGE_CHATBOT/
│
├── data/
│   ├── docs/              # Archivos .md para ingestion
│   └── chroma/            # Base de datos ChromaDB (auto-generado)
│
├── src/
│   ├── embeddings/
│   │   └── embedder.py    # Generación de embeddings BGE-M3
│   ├── database/
│   │   ├── chroma_vector_store.py  # ChromaDB storage
│   │   └── repository.py  # Operaciones CRUD
│   ├── ingestion/
│   │   └── ingest_docs.py # Carga y preprocesamiento
│   ├── rag/
│   │   ├── retriever.py   # Búsqueda semántica
│   │   └── rag_pipeline.py # Pipeline completo
│   ├── llm/
│   │   ├── groq_client.py      # Cliente Groq API (recomendado)
│   │   └── deepseek_client.py  # Cliente DeepSeek API
│   ├── chatbot/
│   │   └── chatbot.py     # Chatbot con historial
│   ├── chat.py            # Chatbot interactivo de consola
│   └── main.py            # Punto de entrada CLI
│
├── .env.example           # Template de variables de entorno
├── requirements.txt       # Dependencias
├── README.md              # Esta documentación
└── CLAUDE.md              # Guía para Claude Code
```

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
git clone <tu-repo>
cd LLAMA_BGE_CHATBOT
```

### 2. Crear entorno virtual

```bash
# Linux/Mac
python -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copia el archivo `.env.example` a `.env` y configura tu API key:

```bash
cp .env.example .env
```

Edita `.env` con tu API key (solo necesitas una):

```env
# Groq API (ultra-rápido, 14,400 requests/día gratis) - RECOMENDADO
GROQ_API_KEY=tu_groq_api_key_aqui

# DeepSeek API (alternativa más lenta pero buena calidad)
DEEPSEEK_API_KEY=tu_deepseek_api_key_aqui
```

**Obtener API Key de Groq** (Recomendado - Ultra Rápido ⚡):
1. Visita [https://console.groq.com/](https://console.groq.com/)
2. Crea una cuenta gratuita
3. Ve a API Keys
4. Genera una nueva API key
5. Cópiala en el archivo `.env` como `GROQ_API_KEY`

**Obtener API Key de DeepSeek** (Alternativa):
1. Visita [https://platform.deepseek.com/](https://platform.deepseek.com/)
2. Crea una cuenta o inicia sesión
3. Ve a la sección de API Keys
4. Genera una nueva API key
5. Cópiala en el archivo `.env` como `DEEPSEEK_API_KEY`

**Comparación de LLMs:**

| Característica | Groq ⚡ (Recomendado) | DeepSeek |
|----------------|---------|----------|
| **Velocidad** | ~200-500ms | ~1-3 segundos |
| **Gratis/día** | 14,400 requests | Según plan |
| **Modelo** | Llama 3.3 70B | DeepSeek-Chat |
| **Calidad** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

💡 **Recomendación**: Usa **Groq** para velocidad óptima (10-20x más rápido) con tier gratuito generoso.

### 5. Preparar documentos

Coloca tus archivos `.md` en la carpeta `data/docs/`:

```bash
mkdir -p data/docs
# Copia tus archivos .md a data/docs/
```

## 📖 Uso

### Ingestion de Documentos

Procesa los archivos markdown y genera sus embeddings:

```bash
# Ingestion básica
python src/main.py --ingest

# Ingestion dividiendo documentos en chunks
python src/main.py --ingest --chunk

# Forzar re-procesamiento de documentos existentes
python src/main.py --ingest --force

# Usar DeepSeek en lugar de Groq
python src/main.py --ingest --llm-provider deepseek
```

### Consultas

#### Consulta única

```bash
python src/main.py --query "¿Qué es Python?"
```

#### Consulta con fuentes

```bash
python src/main.py --query "¿Cómo funciona el sistema?" --show-sources
```

#### Modo interactivo simple

```bash
python src/main.py
```

### 🤖 Chatbot Interactivo (Recomendado)

Inicia el chatbot interactivo por consola:

```bash
python src/chat.py
```

**✨ Características del Chatbot:**
- 💬 Interfaz de chat por consola limpia e intuitiva
- 🧠 Mantiene historial de los últimos 5 mensajes
- 🔍 Sistema RAG con búsqueda semántica en documentos
- 📚 Muestra fuentes consultadas con scores de similitud
- ⚡ Respuestas ultra-rápidas con Groq (200-500ms)
- 📊 Comandos especiales:
  - `salir` o `exit`: Terminar el chat
  - `limpiar`: Borrar historial de conversación
  - `stats`: Ver estadísticas del sistema

**Ejemplo de uso:**
```
🧑 Tú: ¿Qué información tienes sobre becas?

🤖 Chatbot: [Respuesta basada en documentos...]

📚 Fuentes consultadas:
  1. becas.md (similitud: 0.845)
  2. menciones_honorificas.md (similitud: 0.234)

⚡ Tiempo: 350ms
```

### Opciones avanzadas

```bash
# Recuperar más documentos relevantes
python src/main.py --query "tu pregunta" --top-k 5

# Ajustar temperatura del LLM (0.0 = más determinista, 1.0 = más creativo)
python src/main.py --query "tu pregunta" --temperature 0.5

# Combinación de opciones
python src/main.py --query "tu pregunta" --top-k 5 --temperature 0.7 --show-sources

# Usar DeepSeek en lugar de Groq
python src/main.py --query "tu pregunta" --llm-provider deepseek
python src/chat.py --llm-provider deepseek
```

### Estadísticas

Ver información del sistema:

```bash
python src/main.py --stats
```

### Limpiar base de datos

Eliminar todos los documentos:

```bash
python src/main.py --reset
```

## 🔧 Arquitectura Técnica

### Pipeline de Ingestion

1. **Carga de archivos**: Lee archivos `.md` desde `data/docs/`
2. **Preprocesamiento**: Limpia el texto (espacios, saltos de línea)
3. **Chunking** (opcional): Divide documentos largos en segmentos
4. **Generación de embeddings**: BGE-M3 crea vectores de 1024 dimensiones (float32)
5. **Almacenamiento**: Guarda en ChromaDB con persistencia automática

### Pipeline de Consulta

1. **Embedding de consulta**: Convierte la pregunta en vector (1024-dim)
2. **Búsqueda HNSW**: ChromaDB busca documentos similares con cosine similarity
3. **Ranking**: Ordena por relevancia y selecciona top-k
4. **Generación RAG**: Envía contexto + pregunta a Groq/DeepSeek
5. **Respuesta**: Retorna respuesta basada en contexto

### ChromaDB - Vector Database

**Por qué ChromaDB?**
- ✅ Zero configuración requerida - no necesita servidor
- ✅ Diseñado específicamente para embeddings
- ✅ Algoritmo HNSW (Hierarchical Navigable Small World) para búsqueda rápida
- ✅ Persistencia automática a disco
- ✅ Metadata integrada con vectores
- ✅ Excelente para desarrollo y producción
- ✅ Base de datos embebida - sin procesos externos

**Detalles técnicos:**
- **Ubicación**: `data/chroma/` (creado automáticamente)
- **Colección**: `documents`
- **Métrica**: Cosine similarity
- **Índice**: HNSW
- **Dimensiones**: 1024 (BGE-M3)

## 🧪 Testing de Módulos Individuales

Cada módulo puede ejecutarse de forma independiente para testing:

```bash
# Test de embeddings
python src/embeddings/embedder.py

# Test de ChromaDB
python src/database/chroma_vector_store.py

# Test de ingestion
python src/ingestion/ingest_docs.py

# Test de Groq client
python src/llm/groq_client.py

# Test de DeepSeek client
python src/llm/deepseek_client.py

# Test de retriever
python src/rag/retriever.py

# Test de chatbot
python src/chatbot/chatbot.py
```

## ⚠️ Requisitos del Sistema

- **Python**: 3.8 o superior
- **RAM**: Mínimo 4GB (recomendado 8GB para BGE-M3)
- **Espacio en disco**: ~2GB para el modelo BGE-M3
- **Internet**: Solo para primera descarga del modelo y llamadas API

**No se requiere:**
- ❌ SQL Server
- ❌ ODBC Drivers
- ❌ Configuración de base de datos
- ❌ Servidor externo

## 🐛 Troubleshooting

### Error: "GROQ_API_KEY no está configurada"

- Asegúrate de tener el archivo `.env` en la raíz del proyecto
- Verifica que la API key sea válida
- Copia `.env.example` a `.env` si no existe

### Error: "No hay documentos en la base de datos"

- Ejecuta primero `python src/main.py --ingest`
- Verifica que haya archivos `.md` en `data/docs/`

### El modelo BGE-M3 se descarga muy lento

- El modelo pesa ~2GB, la primera vez tomará tiempo
- Se descarga automáticamente en `~/.cache/huggingface/`
- Solo se descarga una vez

### Errores de memoria con BGE-M3

- Cierra otras aplicaciones
- Reduce el tamaño de los documentos usando `--chunk`

### ChromaDB: Error de persistencia

- Elimina la carpeta `data/chroma/` y vuelve a ejecutar `--ingest`
- Verifica permisos de escritura en `data/`

## 📝 Ejemplo de Uso Completo

```bash
# 1. Configurar entorno
cp .env.example .env
# Editar .env con tu GROQ_API_KEY

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Agregar documentos
echo "# Python\nPython es un lenguaje de programación." > data/docs/python.md
echo "# SQL\nSQL es un lenguaje de consultas." > data/docs/sql.md

# 4. Ingerir documentos
python src/main.py --ingest

# 5. Iniciar chatbot interactivo
python src/chat.py

# O hacer consultas directas
python src/main.py --query "¿Qué es Python?" --show-sources
```

## 🚀 Ventajas de esta Implementación

**Vs SQL Server:**
- ✅ Sin instalación ni configuración de base de datos
- ✅ Búsqueda vectorial nativa (HNSW)
- ✅ Más rápido para similitud de embeddings
- ✅ Persistencia automática

**Groq API:**
- ⚡ 10-20x más rápido que alternativas
- 💰 14,400 requests gratis por día
- 🎯 Modelo Llama 3.3 70B de alta calidad
- 🔄 Fácil cambio a DeepSeek si lo necesitas

**BGE-M3:**
- 🌍 Modelo multilingüe (español, inglés, etc.)
- 📊 1024 dimensiones (buen balance)
- 🎯 Estado del arte en embeddings
- 🆓 Completamente gratuito

## 🤝 Contribuciones

Este es un proyecto de referencia. Siéntete libre de modificarlo según tus necesidades.

## 📄 Licencia

MIT License - Siéntete libre de usar este código.

## 🔗 Enlaces Útiles

- [BGE-M3 en Hugging Face](https://huggingface.co/BAAI/bge-m3)
- [Groq Console](https://console.groq.com/)
- [DeepSeek Platform](https://platform.deepseek.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Documentación de Sentence Transformers](https://www.sbert.net/)
