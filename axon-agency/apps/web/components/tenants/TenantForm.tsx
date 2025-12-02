"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useApiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Loader2, Save, Trash2 } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

interface Tenant {
  id: string;
  slug: string;
  name: string;
  business_type: string;
  contact_email: string;
  contact_phone?: string;
  contact_name?: string;
  branding?: {
    primary_color?: string;
  };
  active: boolean;
  notes: string;
}

interface TenantFormProps {
  tenant: Tenant;
  onUpdate?: () => void;
}

const businessTypes = [
  { value: "school", label: "School" },
  { value: "notary", label: "Notary" },
  { value: "delivery", label: "Delivery" },
  { value: "health", label: "Health" },
  { value: "retail", label: "Retail" },
  { value: "general", label: "General" },
];

export function TenantForm({ tenant, onUpdate }: TenantFormProps) {
  const api = useApiClient();
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: tenant.name,
    business_type: tenant.business_type,
    contact_email: tenant.contact_email,
    contact_phone: tenant.contact_phone || "",
    contact_name: tenant.contact_name || "",
    primary_color: tenant.branding?.primary_color || "",
    notes: tenant.notes || "",
  });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    try {
      const updateData: any = {
        name: formData.name,
        business_type: formData.business_type,
        contact_email: formData.contact_email,
        contact_phone: formData.contact_phone || null,
        contact_name: formData.contact_name || null,
        notes: formData.notes,
      };

      if (formData.primary_color) {
        updateData.branding = {
          ...tenant.branding,
          primary_color: formData.primary_color,
        };
      }

      await api.put(`/api/tenants/${tenant.id}`, updateData);

      if (onUpdate) {
        onUpdate();
      } else {
        router.refresh();
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to update tenant");
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    setDeleting(true);
    setError(null);

    try {
      await api.del(`/api/tenants/${tenant.id}`);
      router.push("/agent/tenants");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to delete tenant");
      setDeleting(false);
    }
  };

  return (
    <Card className="bg-slate-900 border-slate-800">
      <CardHeader>
        <CardTitle className="text-slate-200">Tenant Details</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name" className="text-slate-300">
                Name
              </Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, name: e.target.value })
                }
                className="bg-slate-950 border-slate-700 text-slate-200"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="slug" className="text-slate-300">
                Slug (read-only)
              </Label>
              <Input
                id="slug"
                value={tenant.slug}
                disabled
                className="bg-slate-950 border-slate-700 text-slate-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="business_type" className="text-slate-300">
                Business Type
              </Label>
              <Select
                value={formData.business_type}
                onValueChange={(value) =>
                  setFormData({ ...formData, business_type: value })
                }
              >
                <SelectTrigger className="bg-slate-950 border-slate-700 text-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-700">
                  {businessTypes.map((type) => (
                    <SelectItem
                      key={type.value}
                      value={type.value}
                      className="text-slate-200"
                    >
                      {type.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="contact_email" className="text-slate-300">
                Contact Email
              </Label>
              <Input
                id="contact_email"
                type="email"
                value={formData.contact_email}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, contact_email: e.target.value })
                }
                className="bg-slate-950 border-slate-700 text-slate-200"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contact_name" className="text-slate-300">
                Contact Name (optional)
              </Label>
              <Input
                id="contact_name"
                value={formData.contact_name}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, contact_name: e.target.value })
                }
                className="bg-slate-950 border-slate-700 text-slate-200"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="contact_phone" className="text-slate-300">
                Contact Phone (optional)
              </Label>
              <Input
                id="contact_phone"
                value={formData.contact_phone}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                  setFormData({ ...formData, contact_phone: e.target.value })
                }
                className="bg-slate-950 border-slate-700 text-slate-200"
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="primary_color" className="text-slate-300">
              Primary Color (optional)
            </Label>
            <Input
              id="primary_color"
              type="color"
              value={formData.primary_color}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                setFormData({ ...formData, primary_color: e.target.value })
              }
              className="bg-slate-950 border-slate-700 h-10"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="notes" className="text-slate-300">
              Internal Notes
            </Label>
            <Textarea
              id="notes"
              value={formData.notes}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                setFormData({ ...formData, notes: e.target.value })
              }
              className="bg-slate-950 border-slate-700 text-slate-200"
              rows={4}
              placeholder="Internal team notes about this tenant..."
            />
          </div>

          {error && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          <div className="flex items-center justify-between pt-4">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  type="button"
                  variant="destructive"
                  disabled={deleting}
                >
                  {deleting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Deleting...
                    </>
                  ) : (
                    <>
                      <Trash2 className="mr-2 h-4 w-4" />
                      Delete Tenant
                    </>
                  )}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="bg-slate-900 border-slate-700">
                <AlertDialogHeader>
                  <AlertDialogTitle className="text-slate-200">
                    Delete Tenant?
                  </AlertDialogTitle>
                  <AlertDialogDescription className="text-slate-400">
                    This will permanently delete the tenant &quot;{tenant.name}&quot;.
                    Orders associated with this tenant will remain but will have
                    their tenant_id set to null. This action cannot be undone.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel className="bg-slate-800 border-slate-700 text-slate-200">
                    Cancel
                  </AlertDialogCancel>
                  <AlertDialogAction
                    onClick={handleDelete}
                    className="bg-red-500 hover:bg-red-600"
                  >
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>

            <Button type="submit" disabled={saving}>
              {saving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
