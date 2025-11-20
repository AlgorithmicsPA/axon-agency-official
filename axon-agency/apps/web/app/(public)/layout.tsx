import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "../globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Axon Agency — Inteligencia Artificial para tu Negocio",
  description: "Automatización, agentes inteligentes, WhatsApp AI, pipelines N8N y soluciones IA listas para producción.",
};

export default function PublicLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="dark">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
