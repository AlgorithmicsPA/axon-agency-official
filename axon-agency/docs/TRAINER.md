# AXON Agency - Entrenador IA (RAG + Evaluación)

## Descripción General

El módulo de entrenamiento de agentes permite crear, entrenar y evaluar agentes IA utilizando RAG (Retrieval-Augmented Generation) con embeddings y búsqueda vectorial.

## Arquitectura

### Backend (FastAPI)
- **Embeddings**: OpenAI text-embedding-3-large (fallback: sentence-transformers)
- **Vector Store**: FAISS (fallback: numpy)
- **Base de Datos**: SQLite con SQLModel
- **Jobs**: Background tasks con FastAPI

### Modelos de Datos
- `RagSource` - Fuentes de conocimiento (PDF, URL, Markdown, Text)
- `RagChunk` - Chunks de texto indexados
- `AgentMemory` - Memoria de largo plazo de agentes
- `TrainingJob` - Jobs de entrenamiento
- `EvalDataset` - Conjuntos de datos de evaluación
- `EvalRun` - Ejecuciones de evaluación
- `EvalMetric` - Métricas de evaluación

## Endpoints API

### RAG - Gestión de Fuentes

**Subir Documento**
```bash
POST /api/rag/sources/upload
Content-Type: multipart/form-data

corpus_id: opcional (se genera automáticamente)
file: PDF, Markdown, Text, o ZIP (máx 50MB)
```

**Indexar URL**
```bash
POST /api/rag/sources/url
{
  "url": "https://example.com/doc",
  "corpus_id": "opcional"
}
```

**Consultar RAG**
```bash
POST /api/rag/query
{
  "query": "¿Cuál es el objetivo?",
  "corpus_id": "mi_corpus",
  "k": 10
}
```

### Memoria de Agentes

**Guardar Memoria**
```bash
POST /api/agents/memory/save
{
  "agent_id": "agent_123",
  "note": "El usuario prefiere respuestas concisas",
  "is_pinned": true,
  "importance": 8
}
```

**Listar Memorias**
```bash
GET /api/agents/memory/list?agent_id=agent_123
```

### Entrenamiento

**Iniciar Entrenamiento**
```bash
POST /api/agents/train/start
{
  "agent_id": "agent_123",
  "corpus_id": "corpus_abc"
}
```

**Estado**
```bash
GET /api/agents/train/status?job_id=train_xyz
```

### Evaluación

**Crear Dataset**
```bash
POST /api/eval/datasets/create
Content-Type: multipart/form-data
file: CSV o JSON
```

**Ejecutar Evaluación**
```bash
POST /api/eval/run
{
  "dataset_id": "dataset_123",
  "agent_id": "agent_abc"
}
```

**Ver Resultados**
```bash
GET /api/eval/run/{run_id}
```

## Smoke Tests

```bash
# Token
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/dev/token | jq -r .access_token)

# Subir PDF
curl -X POST http://localhost:8080/api/rag/sources/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@doc.pdf"

# Query
curl -X POST http://localhost:8080/api/rag/query \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"test", "k":5}'
```

## Variables de Entorno

```bash
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-large
STORAGE_ROOT=./storage
```
