"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useApiClient } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Settings as SettingsIcon, Server, Key, CheckCircle2 } from "lucide-react";

export default function Settings() {
  const { backendUrl, jwtToken, setBackendUrl, setJwtToken } = useAppStore();
  const [localUrl, setLocalUrl] = useState(backendUrl);
  const [localToken, setLocalToken] = useState(jwtToken);
  const [testing, setTesting] = useState(false);
  const api = useApiClient();
  const { toast } = useToast();

  const handleSave = () => {
    setBackendUrl(localUrl);
    setJwtToken(localToken);
    toast({
      title: "Settings saved",
      description: "Configuration has been updated successfully",
    });
  };

  const handleTest = async () => {
    setTesting(true);
    try {
      const { data } = await api.get("/api/health");
      toast({
        title: "Connection successful",
        description: `Backend is reachable. Status: ${data.status}`,
      });
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Connection failed",
        description: "Unable to connect to backend. Check your URL and token.",
      });
    } finally {
      setTesting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-2xl">
      <div>
        <h1 className="text-3xl font-bold text-glow-cyan flex items-center gap-3">
          <SettingsIcon className="h-8 w-8" />
          Settings
        </h1>
        <p className="text-slate-400 mt-2">Configure backend connection and preferences</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="h-5 w-5 text-cyan-400" />
            Backend Configuration
          </CardTitle>
          <CardDescription>Set the backend API URL and authentication token</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="backend-url">Backend URL</Label>
            <Input
              id="backend-url"
              placeholder="https://your-backend.repl.co"
              value={localUrl}
              onChange={(e) => setLocalUrl(e.target.value)}
            />
            <p className="text-xs text-slate-400">
              The base URL of your Axon Core backend API
            </p>
          </div>

          <div className="space-y-2">
            <Label htmlFor="jwt-token">JWT Token</Label>
            <Input
              id="jwt-token"
              type="password"
              placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
              value={localToken}
              onChange={(e) => setLocalToken(e.target.value)}
            />
            <p className="text-xs text-slate-400">
              Your authentication token from the backend
            </p>
          </div>

          <div className="flex gap-3 pt-4">
            <Button onClick={handleSave} className="glow-cyan">
              <CheckCircle2 className="mr-2 h-4 w-4" />
              Save Settings
            </Button>
            <Button onClick={handleTest} variant="outline" disabled={testing}>
              {testing ? "Testing..." : "Test Connection"}
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5 text-fuchsia-400" />
            Getting Started
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <h3 className="font-semibold mb-2">1. Set Backend URL</h3>
            <p className="text-slate-400">
              Enter the URL of your Axon Core backend. If running locally, use{" "}
              <code className="bg-slate-800 px-2 py-0.5 rounded">http://localhost:5000</code>
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">2. Get JWT Token</h3>
            <p className="text-slate-400">
              In development mode, get a token from{" "}
              <code className="bg-slate-800 px-2 py-0.5 rounded">/api/token/dev</code>
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-2">3. Test Connection</h3>
            <p className="text-slate-400">
              Click "Test Connection" to verify the backend is reachable
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
