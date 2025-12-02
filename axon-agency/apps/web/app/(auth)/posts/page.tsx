"use client";

import { useEffect, useState } from "react";
import { useApiClient } from "@/lib/api";
import { Plus, FileText, Send, Eye, Edit, TrendingUp } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { useToast } from "@/components/Toast";

export default function PostsPage() {
  const api = useApiClient();
  const { showToast } = useToast();
  const [posts, setPosts] = useState<any[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [editingPost, setEditingPost] = useState<any>(null);
  const [formData, setFormData] = useState({ title: "", topic: "", content: "" });

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const res = await api.get<{ items: any[] }>("/api/posts/list");
      setPosts(res.items || []);
    } catch (error) {
      console.error("Error fetching posts:", error);
    }
  };

  const createDraft = async () => {
    if (!formData.title || !formData.topic || !formData.content) {
      showToast("Por favor completa todos los campos", "info");
      return;
    }

    try {
      if (editingPost) {
        showToast("Edición requiere endpoint PATCH en backend (no implementado aún)\n\nPor ahora, puedes:\n1. Crear nuevo draft con cambios\n2. Publicar drafts existentes", "info");
        return;
      } else {
        await api.post("/api/posts/draft", {
          topic: formData.topic,
          brief: formData.title + ": " + formData.content
        });
      }
      setFormData({ title: "", topic: "", content: "" });
      setEditingPost(null);
      setShowModal(false);
      fetchPosts();
    } catch (error) {
      console.error("Error creating draft:", error);
      showToast("Error al crear borrador", "error");
    }
  };

  const publishPost = async (slug: string) => {
    try {
      await api.post(`/api/posts/publish/${slug}`, {});
      showToast("Post publicado exitosamente", "success");
      fetchPosts();
    } catch (error) {
      console.error("Error publishing post:", error);
      showToast("Error al publicar", "error");
    }
  };

  const openEditModal = (post: any) => {
    setEditingPost(post);
    setFormData({
      title: post.title,
      topic: post.topic,
      content: post.content || ""
    });
    setShowModal(true);
  };

  const openCreateModal = () => {
    setEditingPost(null);
    setFormData({ title: "", topic: "", content: "" });
    setShowModal(true);
  };

  const engagementData = posts.map((post, index) => ({
    name: post.title.slice(0, 15) + "...",
    views: Math.floor(Math.random() * 500) + 100,
    likes: Math.floor(Math.random() * 100) + 20,
    shares: Math.floor(Math.random() * 50) + 5,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-purple-400">Publicaciones</h1>
          <p className="text-muted-foreground">Gestiona tu contenido y posts</p>
        </div>
        <button
          onClick={openCreateModal}
          className="flex items-center gap-2 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg transition-colors"
        >
          <Plus size={20} />
          Nueva Publicación
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <FileText className="text-purple-400" size={20} />
            <p className="text-sm font-medium">Total Posts</p>
          </div>
          <p className="text-3xl font-bold">{posts.length}</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Send className="text-green-400" size={20} />
            <p className="text-sm font-medium">Publicados</p>
          </div>
          <p className="text-3xl font-bold">{posts.filter(p => p.status === 'published').length}</p>
        </div>

        <div className="bg-card p-6 rounded-lg border border-border">
          <div className="flex items-center gap-3 mb-2">
            <Eye className="text-cyan-400" size={20} />
            <p className="text-sm font-medium">Borradores</p>
          </div>
          <p className="text-3xl font-bold">{posts.filter(p => p.status === 'draft').length}</p>
        </div>
      </div>

      {engagementData.length > 0 && (
        <div className="bg-card p-6 rounded-lg border border-border">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <TrendingUp className="text-purple-400" size={20} />
            Engagement por Publicación
          </h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={engagementData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis dataKey="name" stroke="#888" fontSize={12} />
              <YAxis stroke="#888" fontSize={12} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1a1a1a', border: '1px solid #333' }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="views" fill="#8b5cf6" radius={[8, 8, 0, 0]} name="Vistas" />
              <Bar dataKey="likes" fill="#06b6d4" radius={[8, 8, 0, 0]} name="Likes" />
              <Bar dataKey="shares" fill="#10b981" radius={[8, 8, 0, 0]} name="Compartidos" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="grid gap-4">
        {posts.map((post) => (
          <div
            key={post.id}
            className="bg-card p-6 rounded-lg border border-border hover:border-purple-500/40 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-xl font-bold mb-2">{post.title}</h3>
                <p className="text-sm text-muted-foreground mb-3">{post.topic}</p>
                <div className="flex items-center gap-3">
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      post.status === 'published'
                        ? 'bg-green-500/20 text-green-400'
                        : 'bg-purple-500/20 text-purple-400'
                    }`}
                  >
                    {post.status === 'published' ? 'Publicado' : 'Borrador'}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Creado: {new Date(post.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => openEditModal(post)}
                  className="flex items-center gap-2 px-4 py-2 bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-400 rounded-lg transition-colors"
                >
                  <Edit size={16} />
                  Editar
                </button>
                {post.status === 'draft' && (
                  <button
                    onClick={() => publishPost(post.slug)}
                    className="flex items-center gap-2 px-4 py-2 bg-green-500 hover:bg-green-600 rounded-lg transition-colors"
                  >
                    <Send size={16} />
                    Publicar
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-card p-8 rounded-lg border border-border max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-2xl font-bold mb-6">
              {editingPost ? 'Editar Publicación' : 'Nueva Publicación'}
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Título</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-purple-500 outline-none"
                  placeholder="Título de la publicación"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Tema</label>
                <input
                  type="text"
                  value={formData.topic}
                  onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-purple-500 outline-none"
                  placeholder="Categoría o tema principal"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Contenido</label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  className="w-full px-4 py-2 bg-accent rounded-lg border border-border focus:border-purple-500 outline-none"
                  rows={8}
                  placeholder="Escribe el contenido de tu publicación..."
                />
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => {
                  setShowModal(false);
                  setEditingPost(null);
                }}
                className="flex-1 px-4 py-2 bg-accent hover:bg-accent/80 rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={createDraft}
                className="flex-1 px-4 py-2 bg-purple-500 hover:bg-purple-600 rounded-lg transition-colors"
              >
                {editingPost ? 'Actualizar' : 'Crear Borrador'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
