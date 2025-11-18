"use client";

import React, { memo } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { atomDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { Clock, ExternalLink } from "lucide-react";
import Link from "next/link";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  provider?: string;
  streaming?: boolean;
  sessionUrl?: string;
  sessionType?: string;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({
  role,
  content,
  timestamp,
  provider,
  streaming = false,
  sessionUrl,
  sessionType,
}) => {
  const isUser = role === "user";

  const formatTime = (ts?: string) => {
    if (!ts) return "";
    try {
      const date = new Date(ts);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return "ahora";
      if (diffMins < 60) return `hace ${diffMins}m`;
      if (diffHours < 24) return `hace ${diffHours}h`;
      if (diffDays < 7) return `hace ${diffDays}d`;
      return date.toLocaleDateString("es-ES", { month: "short", day: "numeric" });
    } catch {
      return "";
    }
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div className={`max-w-[80%] ${isUser ? "ml-auto" : "mr-auto"}`}>
        <div
          className={`rounded-2xl px-5 py-4 transition-all hover:shadow-lg ${
            isUser
              ? "bg-cyan-500/20 text-cyan-100 rounded-br-none border border-cyan-500/30"
              : "bg-accent/80 text-foreground rounded-bl-none border border-border"
          }`}
        >
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code({ node, inline, className, children, ...props }: any) {
                  const match = /language-(\w+)/.exec(className || "");
                  const language = match ? match[1] : "";

                  if (!inline && language) {
                    return (
                      <div className="my-3 rounded-lg overflow-hidden">
                        <SyntaxHighlighter
                          style={atomDark}
                          language={language}
                          PreTag="div"
                          customStyle={{
                            margin: 0,
                            padding: "1rem",
                            background: "rgba(0, 0, 0, 0.4)",
                            fontSize: "0.875rem",
                            borderRadius: "0.5rem",
                          }}
                          {...props}
                        >
                          {String(children).replace(/\n$/, "")}
                        </SyntaxHighlighter>
                      </div>
                    );
                  }

                  return (
                    <code
                      className={`px-2 py-0.5 rounded ${
                        isUser
                          ? "bg-cyan-600/40 text-cyan-100"
                          : "bg-black/30 text-cyan-300"
                      } text-sm font-mono`}
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },

                a({ node, children, href, ...props }: any) {
                  return (
                    <a
                      href={href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={`${
                        isUser ? "text-cyan-300" : "text-cyan-400"
                      } hover:text-cyan-200 underline underline-offset-2 transition-colors`}
                      {...props}
                    >
                      {children}
                    </a>
                  );
                },

                p({ node, children, ...props }: any) {
                  return (
                    <p className="mb-3 last:mb-0 leading-relaxed" {...props}>
                      {children}
                    </p>
                  );
                },

                ul({ node, children, ...props }: any) {
                  return (
                    <ul className="mb-3 space-y-1 list-disc list-inside" {...props}>
                      {children}
                    </ul>
                  );
                },

                ol({ node, children, ...props }: any) {
                  return (
                    <ol className="mb-3 space-y-1 list-decimal list-inside" {...props}>
                      {children}
                    </ol>
                  );
                },

                li({ node, children, ...props }: any) {
                  return (
                    <li className="ml-2" {...props}>
                      {children}
                    </li>
                  );
                },

                h1({ node, children, ...props }: any) {
                  return (
                    <h1 className="text-2xl font-bold mb-3 mt-4 first:mt-0" {...props}>
                      {children}
                    </h1>
                  );
                },

                h2({ node, children, ...props }: any) {
                  return (
                    <h2 className="text-xl font-bold mb-3 mt-3 first:mt-0" {...props}>
                      {children}
                    </h2>
                  );
                },

                h3({ node, children, ...props }: any) {
                  return (
                    <h3 className="text-lg font-semibold mb-2 mt-3 first:mt-0" {...props}>
                      {children}
                    </h3>
                  );
                },

                h4({ node, children, ...props }: any) {
                  return (
                    <h4 className="text-base font-semibold mb-2 mt-2 first:mt-0" {...props}>
                      {children}
                    </h4>
                  );
                },

                h5({ node, children, ...props }: any) {
                  return (
                    <h5 className="text-sm font-semibold mb-2 mt-2 first:mt-0" {...props}>
                      {children}
                    </h5>
                  );
                },

                h6({ node, children, ...props }: any) {
                  return (
                    <h6 className="text-xs font-semibold mb-2 mt-2 first:mt-0 uppercase tracking-wide" {...props}>
                      {children}
                    </h6>
                  );
                },

                blockquote({ node, children, ...props }: any) {
                  return (
                    <blockquote
                      className={`border-l-4 pl-4 py-2 my-3 italic ${
                        isUser
                          ? "border-cyan-400 text-cyan-200/90"
                          : "border-purple-500 text-foreground/90"
                      }`}
                      {...props}
                    >
                      {children}
                    </blockquote>
                  );
                },

                table({ node, children, ...props }: any) {
                  return (
                    <div className="my-3 overflow-x-auto rounded-lg">
                      <table
                        className={`min-w-full border ${
                          isUser ? "border-cyan-500/30" : "border-border"
                        }`}
                        {...props}
                      >
                        {children}
                      </table>
                    </div>
                  );
                },

                thead({ node, children, ...props }: any) {
                  return (
                    <thead
                      className={`${
                        isUser ? "bg-cyan-600/20" : "bg-accent"
                      }`}
                      {...props}
                    >
                      {children}
                    </thead>
                  );
                },

                th({ node, children, ...props }: any) {
                  return (
                    <th
                      className={`px-4 py-2 text-left font-semibold border ${
                        isUser ? "border-cyan-500/30" : "border-border"
                      }`}
                      {...props}
                    >
                      {children}
                    </th>
                  );
                },

                td({ node, children, ...props }: any) {
                  return (
                    <td
                      className={`px-4 py-2 border ${
                        isUser ? "border-cyan-500/30" : "border-border"
                      }`}
                      {...props}
                    >
                      {children}
                    </td>
                  );
                },

                hr({ node, ...props }: any) {
                  return (
                    <hr
                      className={`my-4 ${
                        isUser ? "border-cyan-500/30" : "border-border"
                      }`}
                      {...props}
                    />
                  );
                },

                pre({ node, children, ...props }: any) {
                  return <div {...props}>{children}</div>;
                },
              }}
            >
              {content}
            </ReactMarkdown>

            {streaming && (
              <span className="ml-2 inline-block animate-pulse text-cyan-400 text-lg">▋</span>
            )}
          </div>

          {sessionUrl && sessionType === "autonomous_session" && (
            <Link
              href={sessionUrl}
              className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors text-white font-medium text-sm"
            >
              <ExternalLink size={14} />
              Ver Progreso de la Sesión
            </Link>
          )}
        </div>

        {(timestamp || provider) && (
          <div
            className={`flex items-center gap-2 mt-2 px-2 text-xs text-muted-foreground ${
              isUser ? "justify-end" : "justify-start"
            }`}
          >
            {timestamp && (
              <div className="flex items-center gap-1">
                <Clock size={10} />
                <span>{formatTime(timestamp)}</span>
              </div>
            )}
            {provider && !isUser && (
              <span className="px-2 py-0.5 bg-accent rounded text-xs border border-border">
                {provider}
              </span>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default memo(MessageBubble);
