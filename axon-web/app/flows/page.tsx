"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { useToast } from "@/hooks/use-toast";
import { Workflow, Play, History } from "lucide-react";
import type { FlowResponse } from "@/lib/types";

interface FlowHistory {
  workflowId: string;
  runId: string;
  timestamp: number;
}

export default function Flows() {
  const [workflowId, setWorkflowId] = useState("");
  const [payload, setPayload] = useState("{}");
  const [history, setHistory] = useState<FlowHistory[]>([]);
  const api = useApiClient();
  const { toast } = useToast();

  const triggerMutation = useMutation({
    mutationFn: async () => {
      let parsedPayload;
      try {
        parsedPayload = JSON.parse(payload);
      } catch {
        throw new Error("Invalid JSON payload");
      }

      const { data } = await api.post<FlowResponse>("/api/flows/trigger", {
        workflowId,
        payload: parsedPayload,
      });
      return data;
    },
    onSuccess: (data) => {
      setHistory((prev) => [
        { workflowId, runId: data.runId, timestamp: Date.now() },
        ...prev.slice(0, 9),
      ]);
      toast({
        title: "Workflow triggered",
        description: `Run ID: ${data.runId}`,
      });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Trigger failed",
        description: error.message || error.response?.data?.detail || "Failed to trigger workflow",
      });
    },
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold text-glow-cyan flex items-center gap-3">
          <Workflow className="h-8 w-8" />
          Flows
        </h1>
        <p className="text-slate-400 mt-2">Trigger n8n workflows</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Trigger Workflow</CardTitle>
          <CardDescription>Execute an n8n workflow with custom payload</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="workflow-id">Workflow ID</Label>
            <Input
              id="workflow-id"
              placeholder="workflow-12345"
              value={workflowId}
              onChange={(e) => setWorkflowId(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="payload">Payload (JSON)</Label>
            <Textarea
              id="payload"
              placeholder='{"key": "value"}'
              value={payload}
              onChange={(e) => setPayload(e.target.value)}
              rows={6}
              className="font-mono text-xs"
            />
          </div>

          <Button
            onClick={() => triggerMutation.mutate()}
            disabled={triggerMutation.isPending || !workflowId}
            className="w-full glow-magenta"
          >
            <Play className="mr-2 h-4 w-4" />
            Trigger Workflow
          </Button>
        </CardContent>
      </Card>

      {history.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <History className="h-5 w-5" />
              Recent Triggers
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {history.map((item, i) => (
                <div
                  key={i}
                  className="flex justify-between rounded-lg border border-slate-800 bg-slate-900/50 p-3 text-sm"
                >
                  <div>
                    <div className="font-semibold">{item.workflowId}</div>
                    <div className="text-xs text-slate-400">
                      {new Date(item.timestamp).toLocaleString()}
                    </div>
                  </div>
                  <div className="font-mono text-xs text-slate-400">{item.runId}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
