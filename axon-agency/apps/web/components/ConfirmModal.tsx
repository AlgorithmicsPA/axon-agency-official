"use client";

import { createContext, useContext, useState, useCallback, ReactNode } from "react";
import { AlertTriangle } from "lucide-react";

interface ConfirmOptions {
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  variant?: "danger" | "warning" | "info";
}

interface ConfirmContextType {
  confirm: (options: ConfirmOptions) => Promise<boolean>;
}

const ConfirmContext = createContext<ConfirmContextType | undefined>(undefined);

export const useConfirm = () => {
  const context = useContext(ConfirmContext);
  if (!context) {
    throw new Error("useConfirm must be used within a ConfirmProvider");
  }
  return context;
};

export const ConfirmProvider = ({ children }: { children: ReactNode }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [options, setOptions] = useState<ConfirmOptions | null>(null);
  const [resolvePromise, setResolvePromise] = useState<((value: boolean) => void) | null>(null);

  const confirm = useCallback((opts: ConfirmOptions): Promise<boolean> => {
    setOptions(opts);
    setIsOpen(true);

    return new Promise((resolve) => {
      setResolvePromise(() => resolve);
    });
  }, []);

  const handleConfirm = () => {
    if (resolvePromise) {
      resolvePromise(true);
    }
    setIsOpen(false);
    setOptions(null);
    setResolvePromise(null);
  };

  const handleCancel = () => {
    if (resolvePromise) {
      resolvePromise(false);
    }
    setIsOpen(false);
    setOptions(null);
    setResolvePromise(null);
  };

  const getVariantStyles = (variant: string = "warning") => {
    switch (variant) {
      case "danger":
        return {
          icon: "text-red-400",
          confirmBtn: "bg-red-500 hover:bg-red-600"
        };
      case "warning":
        return {
          icon: "text-yellow-400",
          confirmBtn: "bg-yellow-500 hover:bg-yellow-600"
        };
      case "info":
        return {
          icon: "text-blue-400",
          confirmBtn: "bg-blue-500 hover:bg-blue-600"
        };
      default:
        return {
          icon: "text-yellow-400",
          confirmBtn: "bg-yellow-500 hover:bg-yellow-600"
        };
    }
  };

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}

      {isOpen && options && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card border border-border rounded-lg p-6 max-w-md w-full mx-4 animate-in fade-in zoom-in-95">
            <div className="flex items-start gap-4">
              <div className={`p-2 rounded-lg ${getVariantStyles(options.variant).icon}`}>
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold mb-2">{options.title}</h3>
                <p className="text-muted-foreground text-sm">{options.message}</p>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={handleCancel}
                className="flex-1 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
              >
                {options.cancelText || "Cancelar"}
              </button>
              <button
                onClick={handleConfirm}
                className={`flex-1 px-4 py-2 rounded-lg font-semibold transition-colors ${getVariantStyles(options.variant).confirmBtn}`}
              >
                {options.confirmText || "Confirmar"}
              </button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  );
};
