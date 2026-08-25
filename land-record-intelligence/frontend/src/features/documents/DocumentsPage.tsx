import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/services/api";
import { DocumentRecord } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Search, Upload, Filter } from "lucide-react";

export const DocumentsPage = () => {
  const [documents, setDocuments] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    api.getDocuments().then(setDocuments);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Documents</h1>
          <p className="text-muted-foreground text-sm mt-1">Manage uploaded land records and processing status.</p>
        </div>
        <Link to="/documents/upload" className="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-primary/90">
          <Upload className="w-4 h-4" /> Upload Document
        </Link>
      </div>

      <div className="bg-card border rounded-lg shadow-sm">
        <div className="p-4 border-b flex items-center gap-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input type="text" placeholder="Search filename or ID..." className="pl-9 h-9 w-full rounded-md border text-sm" />
          </div>
          <button className="flex items-center gap-2 border px-3 py-1.5 rounded-md text-sm hover:bg-secondary">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-secondary/50 text-muted-foreground text-xs uppercase">
              <tr>
                <th className="px-6 py-3 font-medium">Document ID</th>
                <th className="px-6 py-3 font-medium">Filename</th>
                <th className="px-6 py-3 font-medium">Upload Date</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {documents.map((doc) => (
                <tr key={doc.id} className="hover:bg-muted/50">
                  <td className="px-6 py-4 font-medium text-primary">{doc.recordId || doc.id}</td>
                  <td className="px-6 py-4">{doc.fileName}</td>
                  <td className="px-6 py-4 text-muted-foreground">{new Date(doc.uploadDate).toLocaleString()}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={doc.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link to={`/verification/${doc.id}`} className="text-blue-600 hover:underline">View</Link>
                  </td>
                </tr>
              ))}
              {documents.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">No documents found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
