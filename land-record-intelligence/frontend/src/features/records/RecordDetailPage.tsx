import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "@/services/api";
import { DocumentRecord, AuditLog } from "@/types";
import { ArrowLeft, CheckCircle2, History, Map } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";

export const RecordDetailPage = () => {
  const { recordId } = useParams();
  const [record, setRecord] = useState<DocumentRecord | null>(null);
  const [audit, setAudit] = useState<AuditLog[]>([]);

  useEffect(() => {
    if (recordId) {
      api.getDocument(recordId).then(doc => setRecord(doc || null));
      api.getAuditHistory(recordId).then(setAudit);
    }
  }, [recordId]);

  if (!record) return <div className="p-8">Loading record details...</div>;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-4">
        <Link to="/records" className="p-2 border rounded-md hover:bg-secondary"><ArrowLeft className="w-4 h-4" /></Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">{record.recordId}</h1>
            <StatusBadge status={record.status} />
          </div>
          <p className="text-muted-foreground text-sm mt-1">Verified Digital Record</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <div className="bg-card border rounded-lg shadow-sm">
            <div className="p-4 border-b bg-secondary/30 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-status-success" />
              <h2 className="font-semibold">Structured Data</h2>
            </div>
            <div className="p-0">
              <dl className="divide-y text-sm">
                <div className="flex p-4"><dt className="w-1/3 text-muted-foreground">Owner Name</dt><dd className="font-medium">{record.owner.value}</dd></div>
                <div className="flex p-4"><dt className="w-1/3 text-muted-foreground">Khasra No.</dt><dd className="font-medium">{record.khasra.value}</dd></div>
                <div className="flex p-4"><dt className="w-1/3 text-muted-foreground">Khata No.</dt><dd className="font-medium">{record.khata.value}</dd></div>
                <div className="flex p-4"><dt className="w-1/3 text-muted-foreground">Land Area</dt><dd className="font-medium">{record.landArea.value}</dd></div>
                <div className="flex p-4"><dt className="w-1/3 text-muted-foreground">Village</dt><dd className="font-medium">{record.village.value}</dd></div>
                <div className="flex p-4"><dt className="w-1/3 text-muted-foreground">Tehsil</dt><dd className="font-medium">{record.tehsil.value}</dd></div>
                <div className="flex p-4"><dt className="w-1/3 text-muted-foreground">District</dt><dd className="font-medium">{record.district.value}</dd></div>
              </dl>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-card border rounded-lg shadow-sm p-4">
             <h3 className="font-semibold mb-4 flex items-center gap-2"><Map className="w-4 h-4"/> Spatial Data</h3>
             <div className="h-40 bg-secondary border rounded-md flex items-center justify-center text-muted-foreground text-sm">
               GIS Map Placeholder
             </div>
          </div>

          <div className="bg-card border rounded-lg shadow-sm p-4">
             <h3 className="font-semibold mb-4 flex items-center gap-2"><History className="w-4 h-4"/> Verification Audit</h3>
             <div className="space-y-4">
               {audit.map(log => (
                 <div key={log.id} className="text-sm border-l-2 border-primary pl-3 py-1">
                   <p className="font-medium">{log.action} <span className="text-muted-foreground font-normal ml-2">{new Date(log.timestamp).toLocaleString()}</span></p>
                   <p className="text-muted-foreground mt-1">{log.details}</p>
                 </div>
               ))}
               {audit.length === 0 && <p className="text-sm text-muted-foreground">No audit trail available.</p>}
             </div>
          </div>
        </div>
      </div>
    </div>
  );
};
