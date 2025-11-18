"use client";

import { useState, useEffect } from "react";
import { useMutation } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import { useSocket } from "@/lib/ws-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Terminal, Play, Trash2 } from "lucide-react";

interface LogEntry {
  line: string;
  timestamp: number;
}

export default function Commands() {
  const [cmd, setCmd] = useState("/usr/bin/ls -la");
  const [cwd, setCwd] = useState("");
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const socket = useSocket();
  const api = useApiClient();
  const { toast } = useToast();

  useEffect(() => {
    if (!socket) return;

    socket.on("task:log", (data: { taskId: string; line: string }) => {
      if (data.taskId === currentTaskId) {
        setLogs((prev) => [...prev, { line: data.line, timestamp: Date.now() }]);
      }
    });

    return () => {
      socket.off("task:log");
    };
  }, [socket, currentTaskId]);

  const runMutation = useMutation({
    mutationFn: async () => {
      const { data } = await api.post<{ taskId: string }>("/api/commands/run", {
        cmd,
        cwd: cwd || undefined,
      });
      return data;
    },
    onSuccess: (data) => {
      setCurrentTaskId(data.taskId);
      setLogs([{ line: `> ${cmd}`, timestamp: Date.now() }]);
      toast({
        title: "Command started",
        description: `Task ID: ${data.taskId}`,
      });
    },
    onError: (error: any) => {
      toast({
        variant: "destructive",
        title: "Command failed",
        description: error.response?.data?.detail || "Failed to execute command",
      });
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-glow-cyan flex items-center gap-3">
          <Terminal className="h-8 w-8" />
          Commands
        </h1>
        <p className="text-slate-400 mt-2">Execute whitelisted commands with live streaming logs</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Command Execution</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="command">Command</Label>
            <Input
              id="command"
              placeholder="/usr/bin/ls -la"
              value={cmd}
              onChange={(e) => setCmd(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  runMutation.mutate();
                }
              }}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="cwd">Working Directory (optional)</Label>
            <Input
              id="cwd"
              placeholder="/home/runner/axon-core"
              value={cwd}
              onChange={(e) => setCwd(e.target.value)}
            />
          </div>

          <div className="flex gap-3">
            <Button
              onClick={() => runMutation.mutate()}
              disabled={runMutation.isPending || !cmd}
              className="glow-cyan"
            >
              <Play className="mr-2 h-4 w-4" />
              Run Command
            </Button>
            <Button variant="outline" onClick={() => setLogs([])}>
              <Trash2 className="mr-2 h-4 w-4" />
              Clear Logs
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Live Terminal Output</span>
            {currentTaskId && (
              <span className="text-sm font-mono text-slate-400">Task: {currentTaskId}</span>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="rounded-lg bg-black p-4 font-mono text-sm min-h-[300px] max-h-[500px] overflow-auto">
            {logs.length === 0 ? (
              <div className="text-slate-500">No output yet. Run a command to see logs.</div>
            ) : (
              <div className="space-y-1">
                {logs.map((log, i) => (
                  <div key={i} className="text-green-400">
                    {log.line}
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
