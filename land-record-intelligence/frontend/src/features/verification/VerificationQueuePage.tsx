import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "@/services/api";
import { DocumentRecord } from "@/types";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ConfidenceIndicator } from "@/components/ui/ConfidenceIndicator";

export const VerificationQueuePage = () => {
  const [queue, setQueue] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    api.getVerificationQueue().then(setQueue);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Verification Queue</h1>
        <p className="text-muted-foreground text-sm mt-1">Targeted human review for low-confidence extractions and validation conflicts.</p>
      </div>

      <div className="bg-card border rounded-lg shadow-sm overflow-hidden">
        <table className="w-full text-sm text-left">
          <thead className="bg-secondary/50 text-muted-foreground text-xs uppercase">
            <tr>
              <th className="px-6 py-3 font-medium">Record ID</th>
              <th className="px-6 py-3 font-medium">Status</th>
              <th className="px-6 py-3 font-medium">Findings</th>
              <th className="px-6 py-3 font-medium">Avg Confidence</th>
              <th className="px-6 py-3 font-medium text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y">
            {queue.map((doc) => (
              <tr key={doc.id} className="hover:bg-muted/50">
                <td className="px-6 py-4 font-medium text-primary">{doc.recordId}</td>
                <td className="px-6 py-4"><StatusBadge status={doc.status} /></td>
                <td className="px-6 py-4">
                  <span className="inline-flex items-center justify-center px-2 py-1 rounded-full bg-red-100 text-red-700 text-xs font-bold">
                    {doc.findings.filter(f => !f.resolved).length}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <ConfidenceIndicator score={doc.status === 'Conflict' ? 0.9 : 0.6} />
                </td>
                <td className="px-6 py-4 text-right">
                  <Link to={doc.status === 'Conflict' ? `/conflicts/${doc.id}` : `/verification/${doc.id}`} 
                        className="bg-primary text-primary-foreground px-3 py-1.5 rounded-md text-xs font-medium hover:bg-primary/90">
                    Review
                  </Link>
                </td>
              </tr>
            ))}
            {queue.length === 0 && (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-muted-foreground">Queue is empty.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
