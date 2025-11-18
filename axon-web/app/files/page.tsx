"use client";

import { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useApiClient } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/hooks/use-toast";
import { FolderOpen, File, Folder, Download, ArrowLeft } from "lucide-react";
import type { FileEntry } from "@/lib/types";

export default function Files() {
  const [currentPath, setCurrentPath] = useState("/");
  const api = useApiClient();
  const { toast } = useToast();

  const { data: entries, isLoading } = useQuery({
    queryKey: ["files", currentPath],
    queryFn: async () => {
      const { data } = await api.post<{ entries: FileEntry[] }>("/api/files/list", {
        path: currentPath,
      });
      return data.entries;
    },
  });

  const downloadMutation = useMutation({
    mutationFn: async (path: string) => {
      const { data } = await api.post(
        "/api/files/download",
        { path },
        { responseType: "blob" }
      );
      return { data, path };
    },
    onSuccess: ({ data, path }) => {
      const url = window.URL.createObjectURL(new Blob([data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", path.split("/").pop() || "file");
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast({
        title: "Download started",
        description: `Downloading ${path.split("/").pop()}`,
      });
    },
    onError: () => {
      toast({
        variant: "destructive",
        title: "Download failed",
        description: "Unable to download file",
      });
    },
  });

  const goUp = () => {
    const parts = currentPath.split("/").filter(Boolean);
    parts.pop();
    setCurrentPath("/" + parts.join("/"));
  };

  const formatSize = (bytes?: number) => {
    if (!bytes) return "-";
    const kb = bytes / 1024;
    if (kb < 1024) return `${kb.toFixed(1)} KB`;
    const mb = kb / 1024;
    return `${mb.toFixed(1)} MB`;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-glow-cyan flex items-center gap-3">
          <FolderOpen className="h-8 w-8" />
          Files
        </h1>
        <p className="text-slate-400 mt-2">Browse and download files</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>File Browser</span>
            {currentPath !== "/" && (
              <Button variant="outline" size="sm" onClick={goUp}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Go Up
              </Button>
            )}
          </CardTitle>
          <div className="pt-2">
            <Input value={currentPath} onChange={(e) => setCurrentPath(e.target.value)} />
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-slate-400">Loading...</div>
          ) : (
            <div className="space-y-2">
              {entries?.map((entry) => (
                <div
                  key={entry.path}
                  className="flex items-center justify-between rounded-lg border border-slate-800 bg-slate-900/50 p-4 hover:bg-slate-800/50 transition-colors"
                >
                  <div className="flex items-center gap-3 flex-1">
                    {entry.type === "directory" ? (
                      <Folder className="h-5 w-5 text-cyan-400" />
                    ) : (
                      <File className="h-5 w-5 text-slate-400" />
                    )}
                    <div>
                      <div className="font-semibold">{entry.name}</div>
                      <div className="text-xs text-slate-400">
                        {entry.type === "file" && formatSize(entry.size)}
                      </div>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    {entry.type === "directory" ? (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setCurrentPath(entry.path)}
                      >
                        Open
                      </Button>
                    ) : (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => downloadMutation.mutate(entry.path)}
                        disabled={downloadMutation.isPending}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Download
                      </Button>
                    )}
                  </div>
                </div>
              ))}

              {entries?.length === 0 && (
                <div className="text-center py-8 text-slate-400">Directory is empty</div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
