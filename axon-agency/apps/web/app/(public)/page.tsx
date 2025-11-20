"use client";

import Link from "next/link";
import { MessageCircle, Zap, Bot, Workflow, Shield, Sparkles } from "lucide-react";

export default function LandingPage() {
  const whatsappPhone = process.env.NEXT_PUBLIC_WHATSAPP_PHONE_NUMBER || "5219841234567";
  const whatsappMessage = process.env.NEXT_PUBLIC_WHATSAPP_DEFAULT_MESSAGE || "Hola, quiero información sobre Axon Agency";
  
  const handleWhatsAppClick = () => {
    const url = `https://wa.me/${whatsappPhone}?text=${encodeURIComponent(whatsappMessage)}`;
    window.open(url, '_blank');
  };

  const features = [
    {
      icon: <Bot className="h-8 w-8 text-cyan-400" />,
      title: "Agentes IA Inteligentes",
      description: "Asistentes conversacionales personalizados para WhatsApp, Telegram y más canales digitales."
    },
    {
      icon: <Workflow className="h-8 w-8 text-purple-400" />,
      title: "Automatización n8n",
      description: "Flujos automáticos avanzados que conectan tus sistemas, APIs y procesos sin código."
    },
    {
      icon: <Zap className="h-8 w-8 text-yellow-400" />,
      title: "Integraciones Multi-Canal",
      description: "Conecta WhatsApp, CRM, bases de datos, APIs externas y herramientas empresariales."
    },
    {
      icon: <Shield className="h-8 w-8 text-green-400" />,
      title: "Multi-Tenancy",
      description: "Plataforma aislada por cliente con seguridad, escalabilidad y gestión centralizada."
    },
    {
      icon: <Sparkles className="h-8 w-8 text-pink-400" />,
      title: "RAG & Búsqueda Semántica",
      description: "Agentes que aprenden de tus documentos y responden con información contextual precisa."
    },
    {
      icon: <MessageCircle className="h-8 w-8 text-blue-400" />,
      title: "WhatsApp Sales Agent",
      description: "Vendedor automático con calificación de leads, enriquecimiento y pagos integrados."
    }
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-pink-500/10"></div>
        <div className="relative max-w-7xl mx-auto px-6 py-24 sm:py-32 lg:py-40">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold tracking-tight text-white mb-6">
              Axon Agency —<br />
              <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Inteligencia Artificial
              </span>
              <br />
              para Escuelas, Empresas y Creadores
            </h1>
            
            <p className="mt-6 text-lg sm:text-xl md:text-2xl text-slate-300 max-w-3xl mx-auto">
              Automatización, agentes inteligentes, WhatsApp AI, pipelines N8N y soluciones IA listas para producción.
            </p>
            
            <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center items-center">
              <button
                onClick={handleWhatsAppClick}
                className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-green-500 to-green-600 text-white text-lg font-semibold rounded-lg hover:from-green-600 hover:to-green-700 transition-all duration-200 shadow-lg hover:shadow-xl hover:scale-105"
              >
                <MessageCircle className="h-6 w-6" />
                Hablar por WhatsApp
              </button>
              
              <Link
                href="/catalog"
                className="inline-flex items-center gap-3 px-8 py-4 bg-slate-800 text-white text-lg font-semibold rounded-lg hover:bg-slate-700 transition-all duration-200 border border-slate-700 hover:border-cyan-500/50"
              >
                Ver Catálogo de Agentes
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-slate-900/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              Soluciones IA listas para producción
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Desde asistentes conversacionales hasta automatizaciones complejas,
              todo en una plataforma robusta y escalable.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group p-6 bg-slate-800/50 rounded-xl border border-slate-700 hover:border-cyan-500/50 transition-all duration-200 hover:shadow-lg hover:shadow-cyan-500/10"
              >
                <div className="mb-4">{feature.icon}</div>
                <h3 className="text-xl font-semibold text-white mb-2">
                  {feature.title}
                </h3>
                <p className="text-slate-400">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-800 py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Axon Agency</h3>
              <p className="text-slate-400 text-sm">
                Inteligencia Artificial para tu negocio.<br />
                Puerto Aventuras, Quintana Roo, México
              </p>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Contacto</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <a href="mailto:contacto@axonagency.mx" className="text-slate-400 hover:text-cyan-400 transition-colors">
                    contacto@axonagency.mx
                  </a>
                </li>
                <li>
                  <button
                    onClick={handleWhatsAppClick}
                    className="text-slate-400 hover:text-green-400 transition-colors flex items-center gap-2"
                  >
                    <MessageCircle className="h-4 w-4" />
                    WhatsApp
                  </button>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-semibold text-white mb-4">Legal</h3>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/privacy-policy" className="text-slate-400 hover:text-cyan-400 transition-colors">
                    Política de Privacidad
                  </Link>
                </li>
                <li>
                  <Link href="/terms-of-service" className="text-slate-400 hover:text-cyan-400 transition-colors">
                    Condiciones de Servicio
                  </Link>
                </li>
                <li>
                  <Link href="/data-deletion" className="text-slate-400 hover:text-cyan-400 transition-colors">
                    Eliminación de Datos
                  </Link>
                </li>
              </ul>
            </div>
          </div>
          
          <div className="pt-8 border-t border-slate-800 text-center">
            <p className="text-slate-500 text-sm">
              © 2025 Axon Agency. Todos los derechos reservados.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
