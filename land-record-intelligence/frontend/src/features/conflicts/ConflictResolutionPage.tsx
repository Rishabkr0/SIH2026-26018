import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "@/services/api";
import { DocumentRecord, VerificationFinding } from "@/types";
import { ArrowLeft, CheckCircle } from "lucide-react";

export const ConflictResolutionPage = () => {
  const { conflictId } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState<DocumentRecord | null>(null);
  const [comment, setComment] = useState("");

  useEffect(() => {
    if (conflictId) {
      api.getDocument(conflictId).then(doc => setRecord(doc || null));
    }
  }, [conflictId]);

  if (!record) return <div className="p-8">Loading...</div>;

  const finding = record.findings.find(f => !f.resolved);
  
  const handleResolve = async () => {
    if (!finding) return;
    await api.resolveConflict(record.id, finding.id, comment);
    navigate("/verification");
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/verification" className="p-2 border rounded-md hover:bg-secondary"><ArrowLeft className="w-4 h-4" /></Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Conflict Resolution</h1>
          <p className="text-muted-foreground text-sm mt-1">Resolve validation engine discrepancies.</p>
        </div>
      </div>

      <div className="bg-card border rounded-lg shadow-sm p-6">
        <div className="bg-red-50 border border-red-200 p-4 rounded-md mb-6">
          <h3 className="text-red-800 font-bold">Detected Conflict</h3>
          <p className="text-red-900 text-sm mt-1">{finding?.message || "No active conflicts."}</p>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="border rounded-md p-4 bg-secondary/30">
            <h4 className="font-semibold text-sm text-muted-foreground uppercase mb-4">Extracted from Document</h4>
            <div className="text-2xl font-bold">{(record as any)[finding?.field || "landArea"]?.value || "N/A"}</div>
            <p className="text-xs text-muted-foreground mt-2">Source: {record.fileName}</p>
          </div>
          <div className="border rounded-md p-4 bg-secondary/30">
            <h4 className="font-semibold text-sm text-muted-foreground uppercase mb-4">Existing LRMS Record</h4>
            <div className="text-2xl font-bold">2.0 acre</div>
            <p className="text-xs text-muted-foreground mt-2">Source: Legacy DB (BL-1999)</p>
          </div>
        </div>

        <div className="space-y-4 border-t pt-6">
          <h4 className="font-semibold">Resolution Action</h4>
          
          <div className="flex gap-4">
            <button className="flex-1 py-3 border rounded-md hover:bg-secondary font-medium">Use Extracted Value</button>
            <button className="flex-1 py-3 border rounded-md hover:bg-secondary font-medium">Use LRMS Value</button>
            <button className="flex-1 py-3 border rounded-md hover:bg-secondary font-medium">Manual Entry</button>
          </div>

          <div className="mt-4">
            <label className="block text-sm font-medium mb-1">Resolution Comment (Required for Audit)</label>
            <textarea 
              className="w-full border rounded-md p-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring" 
              rows={3} 
              placeholder="Explain the reason for this decision..."
              value={comment}
              onChange={e => setComment(e.target.value)}
            />
          </div>

          <div className="flex justify-end pt-4">
            <button 
              onClick={handleResolve}
              disabled={!comment.trim()}
              className="bg-primary text-primary-foreground px-6 py-2 rounded-md font-medium disabled:opacity-50 flex items-center gap-2"
            >
              <CheckCircle className="w-4 h-4" /> Finalize Resolution
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
