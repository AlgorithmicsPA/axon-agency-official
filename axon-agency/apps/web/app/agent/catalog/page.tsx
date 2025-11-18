"use client";

import { useState, useEffect } from "react";
import { AdminOnly } from "@/components/auth/RoleGuard";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { 
  MessageCircle, 
  Send, 
  Share2, 
  Mail, 
  Hash, 
  Package, 
  CheckCircle2, 
  Clock, 
  Loader2,
  Code,
  Database,
  Settings,
  AlertCircle,
  RefreshCw
} from "lucide-react";

interface Product {
  product_type: string;
  name: string;
  description: string;
  channels: string[];
  template_module: string | null;
  template_function: string | null;
  deploy_endpoint: string | null;
  required_env_vars: string[];
  optional_env_vars: string[];
  available: boolean;
}

function CatalogPageContent() {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<"available" | "future">("available");

  const fetchProducts = async () => {
    setRefreshing(true);
    setError(null);
    try {
      const res = await fetch("/api/products/catalog/all", {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }
      const data = await res.json();
      setProducts(data);
    } catch (error) {
      console.error("Error fetching products:", error);
      setError("No se pudieron cargar los productos del catálogo");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const filteredProducts = products.filter(p => 
    filter === "available" ? p.available : !p.available
  );

  const getChannelInfo = (channel: string) => {
    const channelMap: Record<string, { icon: React.ReactNode; text: string; color: string }> = {
      whatsapp: { 
        icon: <MessageCircle className="h-3 w-3" />, 
        text: "WhatsApp",
        color: "bg-green-500/10 text-green-500 border-green-500/20"
      },
      telegram: { 
        icon: <Send className="h-3 w-3" />, 
        text: "Telegram",
        color: "bg-blue-500/10 text-blue-500 border-blue-500/20"
      },
      social: { 
        icon: <Share2 className="h-3 w-3" />, 
        text: "Redes Sociales",
        color: "bg-purple-500/10 text-purple-500 border-purple-500/20"
      },
      email: { 
        icon: <Mail className="h-3 w-3" />, 
        text: "Email",
        color: "bg-orange-500/10 text-orange-500 border-orange-500/20"
      },
      slack: { 
        icon: <Hash className="h-3 w-3" />, 
        text: "Slack",
        color: "bg-pink-500/10 text-pink-500 border-pink-500/20"
      },
    };

    return channelMap[channel.toLowerCase()] || { 
      icon: <MessageCircle className="h-3 w-3" />, 
      text: channel,
      color: "bg-gray-500/10 text-gray-500 border-gray-500/20"
    };
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <Loader2 className="animate-spin text-cyan-400" size={48} />
        <p className="text-muted-foreground">Cargando catálogo...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full gap-4">
        <AlertCircle className="text-red-400" size={48} />
        <h2 className="text-xl font-semibold text-red-400">{error}</h2>
        <Button onClick={fetchProducts} variant="outline">
          <RefreshCw className="mr-2 h-4 w-4" />
          Reintentar
        </Button>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col space-y-6 overflow-auto p-6">
      <div className="flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <Package className="h-8 w-8 text-cyan-400" />
          <h1 className="text-3xl font-bold text-cyan-400">Catálogo de Autopilots</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Productos y servicios disponibles en la plataforma
        </p>
      </div>

      <Tabs value={filter} onValueChange={(value) => setFilter(value as "available" | "future")}>
        <TabsList>
          <TabsTrigger value="available" className="gap-2">
            <CheckCircle2 className="h-4 w-4" />
            Disponibles
          </TabsTrigger>
          <TabsTrigger value="future" className="gap-2">
            <Clock className="h-4 w-4" />
            Próximamente
          </TabsTrigger>
        </TabsList>

        <TabsContent value={filter} className="mt-6">
          {filteredProducts.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-64 gap-4 border border-dashed rounded-lg">
              <Package className="h-16 w-16 text-muted-foreground opacity-50" />
              <div className="text-center">
                <h3 className="text-lg font-semibold text-muted-foreground">
                  No hay productos {filter === "available" ? "disponibles" : "próximamente"}
                </h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {filter === "available" 
                    ? "No hay autopilots disponibles en este momento" 
                    : "No hay productos planificados para el futuro"}
                </p>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {filteredProducts.map((product) => (
                <Card key={product.product_type} className="border-border">
                  <CardHeader>
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <CardTitle className="text-xl text-foreground mb-2">
                          {product.name}
                        </CardTitle>
                        <CardDescription className="text-muted-foreground">
                          {product.description}
                        </CardDescription>
                      </div>
                      <Badge 
                        className={
                          product.available
                            ? "bg-green-500/10 text-green-500 border-green-500/20"
                            : "bg-gray-500/10 text-gray-500 border-gray-500/20"
                        }
                      >
                        {product.available ? (
                          <CheckCircle2 className="h-3 w-3 mr-1" />
                        ) : (
                          <Clock className="h-3 w-3 mr-1" />
                        )}
                        {product.available ? "Disponible" : "Próximamente"}
                      </Badge>
                    </div>
                  </CardHeader>
                  
                  <CardContent className="space-y-4">
                    {product.channels.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {product.channels.map((channel) => {
                          const channelInfo = getChannelInfo(channel);
                          return (
                            <Badge 
                              key={channel} 
                              variant="outline"
                              className={channelInfo.color}
                            >
                              {channelInfo.icon}
                              <span className="ml-1">{channelInfo.text}</span>
                            </Badge>
                          );
                        })}
                      </div>
                    )}

                    <div className="flex flex-wrap gap-2">
                      {product.required_env_vars.length > 0 && (
                        <Badge 
                          variant="outline"
                          className="bg-purple-500/10 text-purple-500 border-purple-500/20"
                        >
                          <Settings className="h-3 w-3 mr-1" />
                          {product.required_env_vars.length} variable{product.required_env_vars.length !== 1 ? 's' : ''} requerida{product.required_env_vars.length !== 1 ? 's' : ''}
                        </Badge>
                      )}
                      
                      {product.optional_env_vars.length > 0 && (
                        <Badge 
                          variant="outline"
                          className="bg-blue-500/10 text-blue-500 border-blue-500/20"
                        >
                          + {product.optional_env_vars.length} opcional{product.optional_env_vars.length !== 1 ? 'es' : ''}
                        </Badge>
                      )}
                    </div>

                    <Accordion type="single" collapsible className="w-full">
                      <AccordionItem value="details" className="border-border">
                        <AccordionTrigger className="text-sm font-medium text-cyan-400 hover:text-cyan-300">
                          Ver detalles técnicos
                        </AccordionTrigger>
                        <AccordionContent className="space-y-4 pt-2">
                          {product.required_env_vars.length > 0 && (
                            <div className="space-y-2">
                              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                                <Settings className="h-4 w-4 text-purple-500" />
                                Variables Requeridas
                              </h4>
                              <ul className="space-y-1 pl-6">
                                {product.required_env_vars.map((varName) => (
                                  <li key={varName} className="text-sm text-muted-foreground font-mono">
                                    • {varName}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {product.optional_env_vars.length > 0 && (
                            <div className="space-y-2">
                              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                                <Database className="h-4 w-4 text-blue-500" />
                                Variables Opcionales
                              </h4>
                              <ul className="space-y-1 pl-6">
                                {product.optional_env_vars.map((varName) => (
                                  <li key={varName} className="text-sm text-muted-foreground font-mono">
                                    • {varName}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}

                          {product.deploy_endpoint && (
                            <div className="space-y-2">
                              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                                <Code className="h-4 w-4 text-green-500" />
                                Endpoint de Deploy
                              </h4>
                              <p className="text-sm text-muted-foreground font-mono bg-muted/50 px-3 py-2 rounded">
                                {product.deploy_endpoint}
                              </p>
                            </div>
                          )}

                          {(product.template_module || product.template_function) && (
                            <div className="space-y-2">
                              <h4 className="text-sm font-semibold text-foreground flex items-center gap-2">
                                <Code className="h-4 w-4 text-orange-500" />
                                Información de Template
                              </h4>
                              {product.template_module && (
                                <p className="text-sm text-muted-foreground">
                                  <span className="font-semibold">Módulo:</span>{" "}
                                  <code className="bg-muted/50 px-2 py-1 rounded text-xs">
                                    {product.template_module}
                                  </code>
                                </p>
                              )}
                              {product.template_function && (
                                <p className="text-sm text-muted-foreground">
                                  <span className="font-semibold">Función:</span>{" "}
                                  <code className="bg-muted/50 px-2 py-1 rounded text-xs">
                                    {product.template_function}
                                  </code>
                                </p>
                              )}
                            </div>
                          )}
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

export default function CatalogPage() {
  return (
    <AdminOnly>
      <CatalogPageContent />
    </AdminOnly>
  );
}
