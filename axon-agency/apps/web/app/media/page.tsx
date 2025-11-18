"use client";

import { useEffect, useState, useCallback } from "react";
import { useApiClient } from "@/lib/api";
import { Upload, Image as ImageIcon, Video, File as FileIcon, Trash2, Download } from "lucide-react";
import { useDropzone } from "react-dropzone";
import { useToast } from "@/components/Toast";
import { useConfirm } from "@/components/ConfirmModal";

const ITEMS_PER_PAGE = 12;

export default function MediaPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const { confirm } = useConfirm();
  const [media, setMedia] = useState<any[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchMedia();
  }, []);

  const fetchMedia = async () => {
    try {
      const res = await api.get("/api/media/list");
      setMedia(res.data.items || []);
    } catch (error) {
      console.error("Error fetching media:", error);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setUploading(true);
    try {
      for (const file of acceptedFiles) {
        const formData = new FormData();
        formData.append("file", file);

        await api.post("/api/media/upload", formData, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }
      fetchMedia();
    } catch (error) {
      console.error("Error uploading files:", error);
      showToast("Error al subir archivos", "error");
    } finally {
      setUploading(false);
    }
  }, [showToast]);

  const deleteMedia = async (id: number) => {
    const confirmed = await confirm({
      title: "Confirmar eliminación",
      message: "¿Eliminar este archivo?",
      variant: "danger"
    });
    if (!confirmed) return;

    try {
      await api.delete(`/api/media/${id}`);
      fetchMedia();
    } catch (error) {
      console.error("Error deleting media:", error);
      showToast("Error al eliminar archivo", "error");
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  const totalPages = Math.ceil(media.length / ITEMS_PER_PAGE);
  const paginatedMedia = media.slice(
    (currentPage - 1) * ITEMS_PER_PAGE,
    currentPage * ITEMS_PER_PAGE
  );

  const getMediaIcon = (mimeType: string) => {
    if (mimeType.startsWith("image/")) return <ImageIcon size={24} className="text-cyan-400" />;
    if (mimeType.startsWith("video/")) return <Video size={24} className="text-purple-400" />;
    return <FileIcon size={24} className="text-green-400" />;
  };

  const formatSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-cyan-400">Galería de Medios</h1>
          <p className="text-muted-foreground">Gestiona imágenes, videos y archivos</p>
        </div>
        <div className="text-sm text-muted-foreground">
          {media.length} archivo(s)
        </div>
      </div>

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
          isDragActive
            ? "border-cyan-500 bg-cyan-500/10"
            : "border-border hover:border-cyan-500/50 bg-card"
        }`}
      >
        <input {...getInputProps()} />
        <Upload
          className={`mx-auto mb-4 ${isDragActive ? "text-cyan-400" : "text-muted-foreground"}`}
          size={48}
        />
        {uploading ? (
          <p className="text-cyan-400 font-medium">Subiendo archivos...</p>
        ) : isDragActive ? (
          <p className="text-cyan-400 font-medium">Suelta los archivos aquí</p>
        ) : (
          <div>
            <p className="font-medium mb-2">Arrastra archivos aquí o haz clic para seleccionar</p>
            <p className="text-sm text-muted-foreground">
              Soporta imágenes, videos y documentos
            </p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {paginatedMedia.map((item) => (
          <div
            key={item.id}
            className="bg-card rounded-lg border border-border overflow-hidden hover:border-cyan-500/40 transition-colors group"
          >
            <div className="aspect-square bg-accent flex items-center justify-center">
              {item.mime_type.startsWith("image/") ? (
                <img
                  src={item.url}
                  alt={item.original_filename}
                  className="w-full h-full object-cover"
                />
              ) : (
                getMediaIcon(item.mime_type)
              )}
            </div>
            <div className="p-3">
              <p className="text-sm font-medium truncate mb-1">{item.original_filename}</p>
              <p className="text-xs text-muted-foreground mb-2">{formatSize(item.size_bytes)}</p>
              <div className="flex gap-2">
                <button
                  onClick={() => window.open(item.url, "_blank")}
                  className="flex-1 flex items-center justify-center gap-1 px-2 py-1 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded text-xs transition-colors"
                >
                  <Download size={12} />
                  Ver
                </button>
                <button
                  onClick={() => deleteMedia(item.id)}
                  className="flex-1 flex items-center justify-center gap-1 px-2 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded text-xs transition-colors"
                >
                  <Trash2 size={12} />
                  Borrar
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Anterior
          </button>
          <div className="flex gap-2">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  currentPage === page
                    ? "bg-cyan-500 text-white"
                    : "bg-card border border-border hover:bg-accent"
                }`}
              >
                {page}
              </button>
            ))}
          </div>
          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Siguiente
          </button>
        </div>
      )}

      {media.length === 0 && !uploading && (
        <div className="bg-card p-12 rounded-lg border border-border text-center">
          <ImageIcon className="mx-auto mb-4 text-muted-foreground" size={48} />
          <p className="text-muted-foreground">No hay archivos. Sube tu primer archivo arriba.</p>
        </div>
      )}
    </div>
  );
}
