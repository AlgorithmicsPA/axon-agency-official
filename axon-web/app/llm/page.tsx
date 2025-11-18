"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import { useCatalog } from "@/hooks/useCatalog";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Brain, Send, Loader2 } from "lucide-react";
import type { LLMRequest, LLMResponse } from "@/lib/types";

export default function LLM() {
  const [provider, setProvider] = useState("openai");
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState<LLMResponse | null>(null);
  const api = useApiClient();
  const { data: catalog } = useCatalog();
  const { toast } = useToast();

  const inferMutation = useMutation({
    mutationFn: async () => {
      const request: LLMRequest = {
        provider,
        input: {
          kind: "text",
          prompt,
        },
      };
      const { data } = await api.post<LLMResponse>("/api/llm/infer", request);
      return data;
    },
    onSuccess: (data) => {
      setResponse(data);
      toast({
        title: "Inference complete",
        description: `Response from ${data.provider}`,
      });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Inference failed",
        description: error.response?.data?.detail || "Failed to get LLM response",
      });
    },
  });

  const providers = catalog?.llmProviders || ["openai", "gemini", "deepseek", "ollama"];

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-3xl font-bold text-glow-cyan flex items-center gap-3">
          <Brain className="h-8 w-8" />
          LLM Playground
        </h1>
        <p className="text-slate-400 mt-2">Interact with multiple LLM providers</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Input</CardTitle>
            <CardDescription>Configure your LLM request</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label>Provider</Label>
              <div className="grid grid-cols-2 gap-2">
                {providers.map((p) => (
                  <Button
                    key={p}
                    variant={provider === p ? "default" : "outline"}
                    onClick={() => setProvider(p)}
                    className="w-full"
                  >
                    {p}
                  </Button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="prompt">Prompt</Label>
              <Textarea
                id="prompt"
                placeholder="Enter your prompt here..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows={8}
              />
            </div>

            <Button
              onClick={() => inferMutation.mutate()}
              disabled={inferMutation.isPending || !prompt}
              className="w-full glow-cyan"
            >
              {inferMutation.isPending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Processing...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Send to LLM
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Response</CardTitle>
            <CardDescription>
              {response && `From ${response.provider} (${response.model})`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {response ? (
              <div className="space-y-4">
                <div className="rounded-lg bg-slate-900 p-4 min-h-[200px] max-h-[400px] overflow-auto">
                  <p className="whitespace-pre-wrap text-sm">{response.output}</p>
                </div>

                {response.usage && (
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="rounded-lg bg-slate-900 p-2">
                      <div className="text-slate-400">Prompt Tokens</div>
                      <div className="font-semibold">{response.usage.prompt_tokens || "-"}</div>
                    </div>
                    <div className="rounded-lg bg-slate-900 p-2">
                      <div className="text-slate-400">Completion</div>
                      <div className="font-semibold">{response.usage.completion_tokens || "-"}</div>
                    </div>
                    <div className="rounded-lg bg-slate-900 p-2">
                      <div className="text-slate-400">Total</div>
                      <div className="font-semibold">{response.usage.total_tokens || "-"}</div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center min-h-[200px] text-slate-400">
                Response will appear here
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
