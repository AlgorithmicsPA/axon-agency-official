"use client";

import { useState, useEffect } from "react";
import { useApiClient } from "@/lib/api";
import { Sparkles, Download, Copy, Check, Loader2 } from "lucide-react";
import { useToast } from "@/components/Toast";

interface Template {
  id: string;
  name: string;
  description: string;
  stack: string;
  features: string[];
  icon: string;
}

interface GeneratedFile {
  path: string;
  content: string;
  description: string;
}

interface ProjectResult {
  project_id: string;
  name: string;
  files: GeneratedFile[];
  dependencies: Record<string, string[]>;
  instructions: string;
  setup_commands: string[];
}

export default function NewProjectPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const [templates, setTemplates] = useState<Template[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>("");
  
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [stack, setStack] = useState("");
  const [features, setFeatures] = useState<string[]>([]);
  const [additionalNotes, setAdditionalNotes] = useState("");
  
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<ProjectResult | null>(null);
  const [copiedFile, setCopiedFile] = useState<string | null>(null);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const res = await api.get("/api/projects/templates");
      setTemplates(res.data.templates);
    } catch (error) {
      console.error("Failed to load templates:", error);
    }
  };

  const selectTemplate = (template: Template) => {
    setSelectedTemplate(template.id);
    setName(template.name);
    setDescription(template.description);
    setStack(template.stack);
    setFeatures(template.features);
  };

  const toggleFeature = (feature: string) => {
    setFeatures((prev) =>
      prev.includes(feature)
        ? prev.filter((f) => f !== feature)
        : [...prev, feature]
    );
  };

  const generateProject = async () => {
    if (!name || !description || !stack) {
      showToast("Por favor completa nombre, descripción y stack", "info");
      return;
    }

    setGenerating(true);
    setResult(null);

    try {
      const res = await api.post("/api/projects/generate", {
        name,
        description,
        stack,
        features,
        additional_notes: additionalNotes || undefined,
      });

      setResult(res.data);
    } catch (error: any) {
      console.error("Generation failed:", error);
      showToast(`Error: ${error.response?.data?.detail || "Generación falló"}`, "error");
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = async (content: string, filePath: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedFile(filePath);
      setTimeout(() => setCopiedFile(null), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  const downloadProject = async () => {
    if (!result) return;

    try {
      const res = await api.post(
        `/api/projects/generate/${result.project_id}/download`,
        result,
        { responseType: "blob" }
      );

      // Create download link
      const blob = new Blob([res.data], { type: "application/zip" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${result.project_id}.zip`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Download failed:", error);
      showToast("Error al descargar el proyecto", "error");
    }
  };

  return (
    <div className="h-full flex flex-col">
      <h1 className="text-3xl font-bold mb-6 text-cyan-400">
        <Sparkles className="inline mr-2" size={32} />
        Generar Proyecto con IA
      </h1>

      {!result ? (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 overflow-hidden">
          {/* Left: Templates */}
          <div className="bg-card rounded-lg border border-border p-6 overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4">Templates Rápidos</h2>
            <div className="space-y-3">
              {templates.map((template) => (
                <button
                  key={template.id}
                  onClick={() => selectTemplate(template)}
                  className={`w-full text-left p-4 rounded-lg border transition-colors ${
                    selectedTemplate === template.id
                      ? "border-cyan-500 bg-cyan-500/10"
                      : "border-border hover:border-cyan-500/50 bg-accent"
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-3xl">{template.icon}</span>
                    <div className="flex-1">
                      <h3 className="font-semibold">{template.name}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {template.description}
                      </p>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {template.features.map((f) => (
                          <span
                            key={f}
                            className="text-xs px-2 py-1 bg-background rounded"
                          >
                            {f}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Right: Custom Form */}
          <div className="bg-card rounded-lg border border-border p-6 overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4">Personalizar Proyecto</h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Nombre del Proyecto</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Mi Proyecto Increíble"
                  className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Descripción</label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="¿Qué hace tu proyecto? ¿Para qué se usa?"
                  rows={3}
                  className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Stack Tecnológico</label>
                <input
                  type="text"
                  value={stack}
                  onChange={(e) => setStack(e.target.value)}
                  placeholder="Python/FastAPI, TypeScript/React, etc."
                  className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Features (opcional)</label>
                <div className="flex flex-wrap gap-2">
                  {["REST API", "Database", "Authentication", "Frontend", "CLI", "Bot", "WebSocket", "CORS", "Testing"].map((f) => (
                    <button
                      key={f}
                      onClick={() => toggleFeature(f)}
                      className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                        features.includes(f)
                          ? "bg-cyan-500 text-white"
                          : "bg-accent hover:bg-accent/80"
                      }`}
                    >
                      {f}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Notas Adicionales (opcional)</label>
                <textarea
                  value={additionalNotes}
                  onChange={(e) => setAdditionalNotes(e.target.value)}
                  placeholder="Cualquier requisito especial..."
                  rows={3}
                  className="w-full px-4 py-2 bg-accent rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                />
              </div>

              <button
                onClick={generateProject}
                disabled={generating}
                className="w-full mt-4 px-6 py-3 bg-cyan-500 hover:bg-cyan-600 disabled:bg-cyan-700 disabled:opacity-50 rounded-lg flex items-center justify-center gap-2 font-semibold"
              >
                {generating ? (
                  <>
                    <Loader2 className="animate-spin" size={20} />
                    Generando Proyecto...
                  </>
                ) : (
                  <>
                    <Sparkles size={20} />
                    Generar Proyecto
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex-1 bg-card rounded-lg border border-border p-6 overflow-y-auto">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-semibold text-cyan-400">
              ✅ Proyecto Generado: {result.name}
            </h2>
            <div className="flex gap-2">
              <button
                onClick={downloadProject}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg flex items-center gap-2"
              >
                <Download size={20} />
                Descargar
              </button>
              <button
                onClick={() => setResult(null)}
                className="px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg"
              >
                Nuevo Proyecto
              </button>
            </div>
          </div>

          {/* Setup Instructions */}
          <div className="mb-6 p-4 bg-accent rounded-lg">
            <h3 className="font-semibold mb-2">📋 Instrucciones de Setup</h3>
            <p className="text-sm text-muted-foreground whitespace-pre-line">
              {result.instructions}
            </p>
          </div>

          {/* Setup Commands */}
          {result.setup_commands.length > 0 && (
            <div className="mb-6 p-4 bg-accent rounded-lg">
              <h3 className="font-semibold mb-2">⚡ Comandos de Setup</h3>
              <div className="space-y-2">
                {result.setup_commands.map((cmd, idx) => (
                  <code
                    key={idx}
                    className="block px-3 py-2 bg-background rounded text-sm"
                  >
                    {cmd}
                  </code>
                ))}
              </div>
            </div>
          )}

          {/* Dependencies */}
          {Object.keys(result.dependencies).length > 0 && (
            <div className="mb-6 p-4 bg-accent rounded-lg">
              <h3 className="font-semibold mb-2">📦 Dependencias</h3>
              {Object.entries(result.dependencies).map(([lang, deps]) => (
                <div key={lang} className="mb-2">
                  <span className="font-medium text-cyan-400">{lang}:</span>{" "}
                  <span className="text-sm">{deps.join(", ")}</span>
                </div>
              ))}
            </div>
          )}

          {/* Generated Files */}
          <div>
            <h3 className="font-semibold mb-3">📁 Archivos Generados ({result.files.length})</h3>
            <div className="space-y-4">
              {result.files.map((file, idx) => (
                <div key={idx} className="border border-border rounded-lg overflow-hidden">
                  <div className="flex items-center justify-between px-4 py-2 bg-accent">
                    <div>
                      <span className="font-mono text-sm">{file.path}</span>
                      <p className="text-xs text-muted-foreground mt-1">
                        {file.description}
                      </p>
                    </div>
                    <button
                      onClick={() => copyToClipboard(file.content, file.path)}
                      className="px-3 py-1 bg-background hover:bg-background/80 rounded flex items-center gap-2"
                    >
                      {copiedFile === file.path ? (
                        <>
                          <Check size={16} className="text-green-500" />
                          <span className="text-sm">Copiado</span>
                        </>
                      ) : (
                        <>
                          <Copy size={16} />
                          <span className="text-sm">Copiar</span>
                        </>
                      )}
                    </button>
                  </div>
                  <pre className="p-4 bg-background overflow-x-auto text-sm">
                    <code>{file.content}</code>
                  </pre>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
