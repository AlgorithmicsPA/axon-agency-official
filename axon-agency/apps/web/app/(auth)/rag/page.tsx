"use client";

import { useRef, useState } from "react";
import { useToast } from "@/components/Toast";
import { useApiClient } from "@/lib/api";

export default function RAGTrainerDashboard() {
  const { showToast } = useToast();
  const api = useApiClient();

  // Usar useApiClient para consistencia con el resto de la app
  async function apiFetch<T>(path: string, opts?: RequestInit): Promise<T> {
    // useApiClient ya maneja la base URL y headers
    if (opts?.method === "GET" || !opts?.method) {
      return api.get<T>(path);
    } else if (opts.method === "POST") {
      const body = opts.body ? JSON.parse(opts.body as string) : undefined;
      return api.post<T>(path, body);
    } else if (opts.method === "DELETE") {
      return api.del<T>(path);
    }
    throw new Error(`Método ${opts.method} no soportado`);
  }

  function Section({
    title,
    description,
    children,
  }: {
    title: string;
    description?: string;
    children: React.ReactNode;
  }) {
    return (
      <div className="bg-card rounded-xl border border-border p-6">
        <h2 className="text-xl font-semibold mb-1 text-cyan-400">{title}</h2>
        {description && (
          <p className="text-sm text-muted-foreground mb-4">{description}</p>
        )}
        {children}
      </div>
    );
  }

  function Pill({ children }: { children: React.ReactNode }) {
    return (
      <span className="px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400 text-xs font-medium">
        {children}
      </span>
    );
  }

  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  async function handleUpload() {
    const file = fileInputRef.current?.files?.[0];
    if (!file) {
      showToast("Selecciona un archivo (PDF, MD o TXT)", "info");
      return;
    }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const json = await apiFetch<any>("/rag/sources/upload", {
        method: "POST",
        body: formData,
      });
      setUploadResult(json);
    } catch (e: any) {
      showToast(`Error subiendo archivo: ${e.message}`, "error");
    } finally {
      setUploading(false);
    }
  }

  const [urlInput, setUrlInput] = useState("");
  const [urlLoading, setUrlLoading] = useState(false);
  const [urlResult, setUrlResult] = useState<any>(null);

  async function handleUrlIngest() {
    if (!urlInput.trim()) {
      showToast("Ingresa una URL", "info");
      return;
    }
    setUrlLoading(true);
    try {
      const json = await apiFetch<any>("/rag/sources/url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput.trim() }),
      });
      setUrlResult(json);
    } catch (e: any) {
      showToast(`Error procesando URL: ${e.message}`, "error");
    } finally {
      setUrlLoading(false);
    }
  }

  const [question, setQuestion] = useState("");
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<any>(null);
  const [topK, setTopK] = useState(5);

  async function handleQuery() {
    if (!question.trim()) {
      showToast("Escribe una pregunta", "info");
      return;
    }
    setQueryLoading(true);
    try {
      const json = await apiFetch<any>("/rag/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: question.trim(), top_k: topK }),
      });
      setQueryResult(json);
    } catch (e: any) {
      showToast(`Error en consulta RAG: ${e.message}`, "error");
    } finally {
      setQueryLoading(false);
    }
  }

  const [memText, setMemText] = useState("");
  const [memSaveLoading, setMemSaveLoading] = useState(false);
  const [memSaveResult, setMemSaveResult] = useState<any>(null);

  async function handleSaveMemory() {
    if (!memText.trim()) {
      showToast("Escribe algo para guardar en memoria", "info");
      return;
    }
    setMemSaveLoading(true);
    try {
      const json = await apiFetch<any>("/agents/memory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: memText.trim() }),
      });
      setMemSaveResult(json);
    } catch (e: any) {
      showToast(`Error guardando memoria: ${e.message}`, "error");
    } finally {
      setMemSaveLoading(false);
    }
  }

  const [memSearch, setMemSearch] = useState("");
  const [memSearchLoading, setMemSearchLoading] = useState(false);
  const [memSearchResult, setMemSearchResult] = useState<any>(null);

  async function handleSearchMemory() {
    if (!memSearch.trim()) {
      showToast("Escribe el término de búsqueda", "info");
      return;
    }
    setMemSearchLoading(true);
    try {
      const q = new URLSearchParams({ q: memSearch.trim() }).toString();
      const json = await apiFetch<any>(`/agents/memory/search?${q}`);
      setMemSearchResult(json);
    } catch (e: any) {
      showToast(`Error buscando en memoria: ${e.message}`, "error");
    } finally {
      setMemSearchLoading(false);
    }
  }

  const [datasetName, setDatasetName] = useState("");
  const [datasetItems, setDatasetItems] = useState(
    '[\n  {\n    "input": "¿Qué es Algorithmics AI?",\n    "expected": "Una agencia de IA para escuelas y notarías"\n  }\n]'
  );
  const [datasetLoading, setDatasetLoading] = useState(false);
  const [datasetResult, setDatasetResult] = useState<any>(null);

  async function handleCreateDataset() {
    if (!datasetName.trim()) {
      showToast("Ponle un nombre al dataset", "info");
      return;
    }
    setDatasetLoading(true);
    try {
      let items: any[] = [];
      try {
        items = JSON.parse(datasetItems);
      } catch (e) {
        showToast("JSON inválido en items del dataset", "error");
        return;
      }
      const json = await apiFetch<any>("/eval/datasets", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: datasetName.trim(), items }),
      });
      setDatasetResult(json);
    } catch (e: any) {
      showToast(`Error creando dataset: ${e.message}`, "error");
    } finally {
      setDatasetLoading(false);
    }
  }

  const [trainConfig, setTrainConfig] = useState(
    '{\n  "strategy": "sft",\n  "epochs": 1\n}'
  );
  const [trainLoading, setTrainLoading] = useState(false);
  const [trainResult, setTrainResult] = useState<any>(null);

  async function handleTrain() {
    setTrainLoading(true);
    try {
      let cfg: any = {};
      try {
        cfg = JSON.parse(trainConfig);
      } catch (e) {
        showToast("JSON inválido en configuración de entrenamiento", "error");
        return;
      }
      const json = await apiFetch<any>("/agents/train", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(cfg),
      });
      setTrainResult(json);
    } catch (e: any) {
      showToast(`Error lanzando entrenamiento: ${e.message}`, "error");
    } finally {
      setTrainLoading(false);
    }
  }

  const [evalDatasetId, setEvalDatasetId] = useState("");
  const [evalConfig, setEvalConfig] = useState(
    '{\n  "metrics": ["accuracy", "bleu"]\n}'
  );
  const [evalLoading, setEvalLoading] = useState(false);
  const [evalResult, setEvalResult] = useState<any>(null);

  async function handleEval() {
    if (!evalDatasetId.trim()) {
      showToast("Proporciona el ID del dataset a evaluar", "info");
      return;
    }
    setEvalLoading(true);
    try {
      let cfg: any = {};
      try {
        cfg = JSON.parse(evalConfig);
      } catch (e) {
        showToast("JSON inválido en configuración de evaluación", "error");
        return;
      }
      const json = await apiFetch<any>("/eval/runs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ dataset_id: evalDatasetId.trim(), ...cfg }),
      });
      setEvalResult(json);
    } catch (e: any) {
      showToast(`Error ejecutando evaluación: ${e.message}`, "error");
    } finally {
      setEvalLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold mb-2">
            <span className="text-cyan-400">RAG</span> / Training Dashboard
          </h1>
          <p className="text-sm text-muted-foreground">
            Sistema de conocimiento, memoria y entrenamiento de agentes
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Pill>Backend :8080</Pill>
          <Pill>FAISS + Numpy</Pill>
        </div>
      </div>

      <Section
        title="Fuentes (RagSource)"
        description="Sube documentos o ingiere páginas web para generar embeddings."
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Subir archivo</h3>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.md,.txt"
              className="block w-full text-sm file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-cyan-500/20 file:text-cyan-400 hover:file:bg-cyan-500/30"
            />
            <button
              onClick={handleUpload}
              disabled={uploading}
              className="mt-3 px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
            >
              {uploading ? "Subiendo…" : "Subir y procesar"}
            </button>
            {uploadResult && (
              <pre className="mt-3 text-xs bg-background p-3 rounded-lg overflow-auto max-h-48 border border-border">
                {JSON.stringify(uploadResult, null, 2)}
              </pre>
            )}
          </div>
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Procesar URL</h3>
            <div className="flex gap-2">
              <input
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                placeholder="https://…"
                className="flex-1 px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none"
              />
              <button
                onClick={handleUrlIngest}
                disabled={urlLoading}
                className="px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
              >
                {urlLoading ? "Procesando…" : "Ingerir"}
              </button>
            </div>
            {urlResult && (
              <pre className="mt-3 text-xs bg-background p-3 rounded-lg overflow-auto max-h-48 border border-border">
                {JSON.stringify(urlResult, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </Section>

      <Section
        title="Búsqueda RAG"
        description="Consulta semántica con recuperación de contexto (FAISS)"
      >
        <div className="flex flex-col gap-2 md:flex-row md:items-end">
          <div className="flex-1">
            <label className="text-sm text-muted-foreground">Pregunta</label>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="¿Qué dice el documento sobre…?"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
          </div>
          <div>
            <label className="text-sm text-muted-foreground">Top‑K</label>
            <input
              type="number"
              min={1}
              max={20}
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value || "5"))}
              className="w-24 px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
          </div>
          <button
            onClick={handleQuery}
            disabled={queryLoading}
            className="px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
          >
            {queryLoading ? "Buscando…" : "Consultar"}
          </button>
        </div>
        {queryResult && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2 border border-border rounded-lg p-4">
              <h4 className="font-semibold mb-2 text-cyan-400">Respuesta</h4>
              <pre className="text-sm whitespace-pre-wrap">
                {queryResult.answer || JSON.stringify(queryResult, null, 2)}
              </pre>
            </div>
            <div className="border border-border rounded-lg p-4">
              <h4 className="font-semibold mb-2 text-cyan-400">
                Contexto (Top‑K)
              </h4>
              <pre className="text-xs bg-background p-3 rounded-lg overflow-auto max-h-72 border border-border">
                {JSON.stringify(
                  queryResult.context || queryResult.matches || [],
                  null,
                  2
                )}
              </pre>
            </div>
          </div>
        )}
      </Section>

      <Section
        title="Memoria del Agente"
        description="Guarda y busca recuerdos en AgentMemory"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Guardar en memoria</h3>
            <textarea
              value={memText}
              onChange={(e) => setMemText(e.target.value)}
              rows={4}
              placeholder="Texto a recordar…"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
            <button
              onClick={handleSaveMemory}
              disabled={memSaveLoading}
              className="mt-3 px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
            >
              {memSaveLoading ? "Guardando…" : "Guardar"}
            </button>
            {memSaveResult && (
              <pre className="mt-3 text-xs bg-background p-3 rounded-lg overflow-auto max-h-48 border border-border">
                {JSON.stringify(memSaveResult, null, 2)}
              </pre>
            )}
          </div>
          <div className="border border-border rounded-lg p-4">
            <h3 className="font-semibold mb-2">Buscar en memoria</h3>
            <div className="flex gap-2">
              <input
                value={memSearch}
                onChange={(e) => setMemSearch(e.target.value)}
                placeholder="palabra clave…"
                className="flex-1 px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none"
              />
              <button
                onClick={handleSearchMemory}
                disabled={memSearchLoading}
                className="px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
              >
                {memSearchLoading ? "Buscando…" : "Buscar"}
              </button>
            </div>
            {memSearchResult && (
              <pre className="mt-3 text-xs bg-background p-3 rounded-lg overflow-auto max-h-48 border border-border">
                {JSON.stringify(memSearchResult, null, 2)}
              </pre>
            )}
          </div>
        </div>
      </Section>

      <Section
        title="Datasets de Evaluación"
        description="Crea conjuntos de prueba (EvalDataset)"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border border-border rounded-lg p-4">
            <label className="text-sm text-muted-foreground">
              Nombre del dataset
            </label>
            <input
              value={datasetName}
              onChange={(e) => setDatasetName(e.target.value)}
              placeholder="p.ej. demo-v1"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
            <div className="h-px bg-border my-4" />
            <label className="text-sm text-muted-foreground">
              Items (JSON array)
            </label>
            <textarea
              value={datasetItems}
              onChange={(e) => setDatasetItems(e.target.value)}
              rows={8}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg font-mono text-xs focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
            <button
              onClick={handleCreateDataset}
              disabled={datasetLoading}
              className="mt-3 px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
            >
              {datasetLoading ? "Creando…" : "Crear dataset"}
            </button>
            {datasetResult && (
              <pre className="mt-3 text-xs bg-background p-3 rounded-lg overflow-auto max-h-48 border border-border">
                {JSON.stringify(datasetResult, null, 2)}
              </pre>
            )}
          </div>
          <div className="border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Ejemplo de item</p>
            <pre className="text-xs bg-background p-3 rounded-lg overflow-auto border border-border mt-2">
              {`{
  "input": "¿Qué es Algorithmics AI?",
  "expected": "Una agencia de IA para escuelas y notarías"
}`}
            </pre>
            <p className="mt-3 text-sm text-muted-foreground">
              Cada item puede incluir campos adicionales según tu evaluador.
            </p>
          </div>
        </div>
      </Section>

      <Section
        title="Entrenamiento"
        description="Lanza trabajos de entrenamiento (POST /api/agents/train)"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border border-border rounded-lg p-4">
            <label className="text-sm text-muted-foreground">
              Config (JSON)
            </label>
            <textarea
              value={trainConfig}
              onChange={(e) => setTrainConfig(e.target.value)}
              rows={8}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg font-mono text-xs focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
            <button
              onClick={handleTrain}
              disabled={trainLoading}
              className="mt-3 px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
            >
              {trainLoading ? "Lanzando…" : "Lanzar entrenamiento"}
            </button>
            {trainResult && (
              <pre className="mt-3 text-xs bg-background p-3 rounded-lg overflow-auto max-h-48 border border-border">
                {JSON.stringify(trainResult, null, 2)}
              </pre>
            )}
          </div>
          <div className="border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Ejemplo mínimo</p>
            <pre className="text-xs bg-background p-3 rounded-lg overflow-auto border border-border mt-2">
              {`{
  "strategy": "sft",
  "epochs": 1,
  "learning_rate": 3e-5,
  "batch_size": 4,
  "dataset": "demo-v1"
}`}
            </pre>
            <p className="mt-3 text-sm text-muted-foreground">
              Ajusta según tus recursos. Tu backend ya maneja los fallbacks.
            </p>
          </div>
        </div>
      </Section>

      <Section
        title="Evaluación"
        description="Ejecuta corridas y muestra métricas (EvalRun / EvalMetric)"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="border border-border rounded-lg p-4">
            <label className="text-sm text-muted-foreground">Dataset ID</label>
            <input
              value={evalDatasetId}
              onChange={(e) => setEvalDatasetId(e.target.value)}
              placeholder="ID del dataset…"
              className="w-full px-3 py-2 bg-background border border-border rounded-lg focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
            <div className="h-px bg-border my-4" />
            <label className="text-sm text-muted-foreground">
              Config (JSON)
            </label>
            <textarea
              value={evalConfig}
              onChange={(e) => setEvalConfig(e.target.value)}
              rows={8}
              className="w-full px-3 py-2 bg-background border border-border rounded-lg font-mono text-xs focus:ring-2 focus:ring-cyan-500 focus:outline-none"
            />
            <button
              onClick={handleEval}
              disabled={evalLoading}
              className="mt-3 px-4 py-2 rounded-lg bg-cyan-500 text-black font-medium disabled:opacity-50 hover:bg-cyan-400 transition-colors"
            >
              {evalLoading ? "Evaluando…" : "Ejecutar evaluación"}
            </button>
            {evalResult && (
              <pre className="mt-3 text-xs bg-background p-3 rounded-lg overflow-auto max-h-48 border border-border">
                {JSON.stringify(evalResult, null, 2)}
              </pre>
            )}
          </div>
          <div className="border border-border rounded-lg p-4">
            <p className="text-sm text-muted-foreground">Ejemplo</p>
            <pre className="text-xs bg-background p-3 rounded-lg overflow-auto border border-border mt-2">
              {`{
  "metrics": ["accuracy", "bleu"],
  "max_examples": 50
}`}
            </pre>
            <p className="mt-3 text-sm text-muted-foreground">
              Define tus métricas y límites. Visualización avanzada se puede
              añadir con charts.
            </p>
          </div>
        </div>
      </Section>

      <div className="text-center text-xs text-muted-foreground pb-4">
        RAG/Training Dashboard · AXON Agency Platform
      </div>
    </div>
  );
}
