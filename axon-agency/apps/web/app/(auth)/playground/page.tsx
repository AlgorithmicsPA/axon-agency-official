"use client";

import { useState, useRef, useEffect } from "react";
import Editor from "@monaco-editor/react";
import { useApiClient } from "@/lib/api";
import {
  Play,
  Code,
  Sparkles,
  FileCode,
  Zap,
  Terminal,
  Loader2,
  Copy,
  Check,
  AlertTriangle,
} from "lucide-react";
import { useToast } from "@/components/Toast";

const TEMPLATES = {
  python: `# Python Example
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

for i in range(10):
    print(f"fib({i}) = {fibonacci(i)}")`,
  
  javascript: `// JavaScript Example
function quickSort(arr) {
  if (arr.length <= 1) return arr;
  
  const pivot = arr[Math.floor(arr.length / 2)];
  const left = arr.filter(x => x < pivot);
  const middle = arr.filter(x => x === pivot);
  const right = arr.filter(x => x > pivot);
  
  return [...quickSort(left), ...middle, ...quickSort(right)];
}

const numbers = [64, 34, 25, 12, 22, 11, 90];
console.log("Sorted:", quickSort(numbers));`,

  typescript: `// TypeScript Example
interface User {
  id: number;
  name: string;
  email: string;
}

function greetUser(user: User): string {
  return \`Hello, \${user.name}! Your email is \${user.email}\`;
}

const user: User = {
  id: 1,
  name: "Super Axon",
  email: "axon@algorithmics.ai"
};

console.log(greetUser(user));`,

  go: `// Go Example
package main

import "fmt"

func factorial(n int) int {
    if n <= 1 {
        return 1
    }
    return n * factorial(n-1)
}

func main() {
    for i := 0; i < 10; i++ {
        fmt.Printf("factorial(%d) = %d\\n", i, factorial(i))
    }
}`,
};

export default function PlaygroundPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const editorRef = useRef<any>(null);
  
  const [code, setCode] = useState(TEMPLATES.python);
  const [language, setLanguage] = useState("python");
  const [provider, setProvider] = useState<"auto" | "openai" | "gemini" | "ollama">("auto");
  const [output, setOutput] = useState("");
  const [executing, setExecuting] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [providers, setProviders] = useState<any>(null);

  useEffect(() => {
    fetchProviders();
  }, []);

  async function fetchProviders() {
    try {
      const response = await api.get("/api/llm/providers");
      setProviders(response.data.providers);
    } catch (error) {
      console.error("Error fetching providers:", error);
    }
  }

  function handleEditorDidMount(editor: any) {
    editorRef.current = editor;
  }

  async function executeCode() {
    setExecuting(true);
    setOutput("⏳ Ejecutando código...\n");
    
    try {
      const response = await api.post("/api/code/execute", {
        code,
        language,
        timeout: 30,
      });
      
      const result = response.data;
      
      let outputText = "";
      
      if (result.warnings && result.warnings.length > 0) {
        outputText += "⚠️  WARNINGS:\n";
        result.warnings.forEach((w: string) => outputText += `   ${w}\n`);
        outputText += "\n";
      }
      
      if (result.stdout) {
        outputText += "📤 STDOUT:\n" + result.stdout + "\n";
      }
      if (result.stderr) {
        outputText += "⚠️  STDERR:\n" + result.stderr + "\n";
      }
      outputText += `\n✅ Exit Code: ${result.exit_code}\n`;
      outputText += `⏱️  Execution Time: ${result.execution_time.toFixed(3)}s\n`;
      
      setOutput(outputText);
    } catch (error: any) {
      setOutput(`❌ Error:\n${error.response?.data?.detail || error.message}`);
    } finally {
      setExecuting(false);
    }
  }

  async function improveWithAI() {
    if (!code.trim()) {
      showToast("Escribe algo de código primero", "info");
      return;
    }

    setAiLoading(true);
    try {
      const response = await api.post("/api/llm/chat", {
        messages: [
          {
            role: "user",
            content: `Mejora este código ${language} para que sea más eficiente, legible y siga best practices. Devuelve SOLO el código mejorado sin explicaciones:\n\n${code}`,
          },
        ],
        provider,
      });

      const improvedCode = response.data.content;
      setCode(improvedCode);
    } catch (error: any) {
      showToast(`Error con IA: ${error.response?.data?.detail || error.message}`, "error");
    } finally {
      setAiLoading(false);
    }
  }

  async function explainCode() {
    if (!code.trim()) {
      showToast("Escribe algo de código primero", "info");
      return;
    }

    setAiLoading(true);
    try {
      const response = await api.post("/api/llm/chat", {
        messages: [
          {
            role: "user",
            content: `Explica qué hace este código ${language} de forma clara y concisa:\n\n${code}`,
          },
        ],
        provider,
      });

      setOutput(`💡 Explicación:\n\n${response.data.content}`);
    } catch (error: any) {
      showToast(`Error con IA: ${error.response?.data?.detail || error.message}`, "error");
    } finally {
      setAiLoading(false);
    }
  }

  async function generateFromPrompt() {
    const prompt = window.prompt("¿Qué código quieres generar?");
    if (!prompt) return;

    setAiLoading(true);
    try {
      const response = await api.post("/api/llm/chat", {
        messages: [
          {
            role: "user",
            content: `Genera código ${language} para: ${prompt}\n\nDevuelve SOLO el código sin explicaciones.`,
          },
        ],
        provider,
      });

      setCode(response.data.content.replace(/```[a-z]*\n?/g, "").trim());
    } catch (error: any) {
      showToast(`Error generando código: ${error.response?.data?.detail || error.message}`, "error");
    } finally {
      setAiLoading(false);
    }
  }

  function changeLanguage(newLang: string) {
    setLanguage(newLang);
    if (TEMPLATES[newLang as keyof typeof TEMPLATES]) {
      setCode(TEMPLATES[newLang as keyof typeof TEMPLATES]);
    }
  }

  function copyOutput() {
    navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="h-screen flex flex-col">
      <div className="p-4 border-b border-border bg-card">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-cyan-400 flex items-center gap-2">
              <Code className="text-cyan-400" />
              Code Playground
            </h1>
            <p className="text-sm text-muted-foreground">
              Editor de código con ejecución segura y asistente IA
            </p>
          </div>

          <div className="flex items-center gap-3">
            <select
              value={language}
              onChange={(e) => changeLanguage(e.target.value)}
              className="bg-background border border-border rounded px-3 py-2 text-sm"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="go">Go</option>
              <option value="rust">Rust</option>
              <option value="bash">Bash</option>
            </select>

            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as any)}
              className="bg-background border border-border rounded px-3 py-2 text-sm"
              title="Proveedor de IA"
            >
              <option value="auto">🤖 Auto (Inteligente)</option>
              <option 
                value="gemini" 
                disabled={providers && !providers.gemini?.available}
              >
                💎 Gemini {providers && !providers.gemini?.available ? "(No disponible)" : "(Multimodal)"}
              </option>
              <option 
                value="openai"
                disabled={providers && !providers.openai?.available}
              >
                🧠 OpenAI {providers && !providers.openai?.available ? "(No disponible)" : "(GPT-4)"}
              </option>
              <option 
                value="ollama"
                disabled={providers && !providers.ollama?.available}
              >
                ⚡ Ollama {providers && !providers.ollama?.available ? "(No disponible)" : "(Local)"}
              </option>
            </select>
          </div>
        </div>

        <div className="flex gap-2 mt-3">
          <button
            onClick={executeCode}
            disabled={executing}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-green-800 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
          >
            {executing ? (
              <>
                <Loader2 className="animate-spin" size={18} />
                Ejecutando...
              </>
            ) : (
              <>
                <Play size={18} />
                Ejecutar
              </>
            )}
          </button>

          <button
            onClick={improveWithAI}
            disabled={aiLoading}
            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
          >
            <Sparkles size={18} />
            Mejorar con IA
          </button>

          <button
            onClick={explainCode}
            disabled={aiLoading}
            className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-700 disabled:bg-cyan-800 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
          >
            <FileCode size={18} />
            Explicar
          </button>

          <button
            onClick={generateFromPrompt}
            disabled={aiLoading}
            className="flex items-center gap-2 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-800 disabled:opacity-50 text-white px-4 py-2 rounded transition-colors"
          >
            <Zap size={18} />
            Generar
          </button>
        </div>
      </div>

      <div className="flex-1 flex">
        <div className="flex-1 border-r border-border">
          <Editor
            height="100%"
            language={language}
            value={code}
            onChange={(value) => setCode(value || "")}
            onMount={handleEditorDidMount}
            theme="vs-dark"
            options={{
              minimap: { enabled: true },
              fontSize: 14,
              scrollBeyondLastLine: false,
              wordWrap: "on",
              automaticLayout: true,
              tabSize: 2,
            }}
          />
        </div>

        <div className="w-1/3 bg-card flex flex-col">
          <div className="p-3 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Terminal size={18} className="text-green-400" />
              <span className="font-semibold">Output</span>
            </div>
            {output && (
              <button
                onClick={copyOutput}
                className="text-muted-foreground hover:text-foreground transition-colors"
                title="Copiar output"
              >
                {copied ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
              </button>
            )}
          </div>
          <div className="flex-1 overflow-auto p-4">
            <pre className="text-sm font-mono whitespace-pre-wrap">{output || "⚡ Presiona 'Ejecutar' para ver el resultado..."}</pre>
          </div>
        </div>
      </div>
    </div>
  );
}
