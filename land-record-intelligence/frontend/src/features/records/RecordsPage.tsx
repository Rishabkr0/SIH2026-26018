import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "@/services/api";
import { DocumentRecord } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { Search, Filter, Download } from "lucide-react";

export const RecordsPage = () => {
  const [records, setRecords] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    api.getRecords().then(setRecords);
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Verified Records</h1>
          <p className="text-muted-foreground text-sm mt-1">Search and view fully verified digital land records.</p>
        </div>
        <button className="bg-secondary text-secondary-foreground border px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 hover:bg-secondary/80">
          <Download className="w-4 h-4" /> Export
        </button>
      </div>

      <div className="bg-card border rounded-lg shadow-sm">
        <div className="p-4 border-b flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <input type="text" placeholder="Search Khasra, Owner, or Record ID..." className="pl-9 h-9 w-full rounded-md border text-sm" />
          </div>
          <button className="flex items-center gap-2 border px-3 py-1.5 rounded-md text-sm hover:bg-secondary">
            <Filter className="w-4 h-4" /> Filter
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-secondary/50 text-muted-foreground text-xs uppercase">
              <tr>
                <th className="px-6 py-3 font-medium">Record ID</th>
                <th className="px-6 py-3 font-medium">Owner Name</th>
                <th className="px-6 py-3 font-medium">Khasra</th>
                <th className="px-6 py-3 font-medium">Village</th>
                <th className="px-6 py-3 font-medium">Status</th>
                <th className="px-6 py-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {records.map((doc) => (
                <tr key={doc.id} className="hover:bg-muted/50">
                  <td className="px-6 py-4 font-medium text-primary">{doc.recordId}</td>
                  <td className="px-6 py-4">{doc.owner.value}</td>
                  <td className="px-6 py-4">{doc.khasra.value}</td>
                  <td className="px-6 py-4">{doc.village.value}</td>
                  <td className="px-6 py-4">
                    <StatusBadge status={doc.status} />
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link to={`/records/${doc.id}`} className="text-blue-600 hover:underline">View Details</Link>
                  </td>
                </tr>
              ))}
              {records.length === 0 && (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-muted-foreground">No verified records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
