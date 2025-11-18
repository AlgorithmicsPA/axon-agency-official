import Link from "next/link";
import { TenantBadge } from "./TenantBadge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ExternalLink, Edit } from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface Tenant {
  id: string;
  slug: string;
  name: string;
  business_type: string;
  contact_email: string;
  contact_phone?: string;
  contact_name?: string;
  active: boolean;
  created_at: string;
  updated_at: string;
}

interface TenantListTableProps {
  tenants: Tenant[];
}

export function TenantListTable({ tenants }: TenantListTableProps) {
  if (tenants.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <p>No tenants found.</p>
      </div>
    );
  }

  return (
    <div className="border border-slate-800 rounded-lg overflow-hidden">
      <Table>
        <TableHeader>
          <TableRow className="hover:bg-slate-900/50 border-slate-800">
            <TableHead className="text-slate-400">Name</TableHead>
            <TableHead className="text-slate-400">Slug</TableHead>
            <TableHead className="text-slate-400">Type</TableHead>
            <TableHead className="text-slate-400">Contact</TableHead>
            <TableHead className="text-slate-400">Created</TableHead>
            <TableHead className="text-slate-400 text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {tenants.map((tenant) => (
            <TableRow
              key={tenant.id}
              className="hover:bg-slate-900/50 border-slate-800"
            >
              <TableCell className="font-medium text-slate-200">
                {tenant.name}
                {!tenant.active && (
                  <span className="ml-2 text-xs text-red-400">(Inactive)</span>
                )}
              </TableCell>
              <TableCell className="text-slate-400 font-mono text-sm">
                {tenant.slug}
              </TableCell>
              <TableCell>
                <TenantBadge businessType={tenant.business_type} />
              </TableCell>
              <TableCell className="text-slate-400 text-sm">
                <div>{tenant.contact_email}</div>
                {tenant.contact_name && (
                  <div className="text-xs text-slate-500">{tenant.contact_name}</div>
                )}
              </TableCell>
              <TableCell className="text-slate-400 text-sm">
                {formatDistanceToNow(new Date(tenant.created_at), {
                  addSuffix: true,
                })}
              </TableCell>
              <TableCell className="text-right">
                <div className="flex items-center justify-end gap-2">
                  <Button
                    asChild
                    variant="outline"
                    size="sm"
                    className="border-slate-700"
                  >
                    <Link href={`/agent/tenants/${tenant.id}`}>
                      <Edit className="mr-2 h-4 w-4" />
                      Edit
                    </Link>
                  </Button>
                  <Button
                    asChild
                    variant="outline"
                    size="sm"
                    className="border-slate-700"
                  >
                    <Link
                      href={`/portal/${tenant.slug}`}
                      target="_blank"
                      rel="noopener noreferrer"
                    >
                      <ExternalLink className="mr-2 h-4 w-4" />
                      Portal
                    </Link>
                  </Button>
                </div>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
