import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { api } from "@/services/api";
import { DocumentRecord } from "@/types";
import { ConfidenceIndicator } from "@/components/ui/ConfidenceIndicator";
import { ArrowLeft, Check, AlertCircle, Edit2 } from "lucide-react";

export const VerificationWorkspacePage = () => {
  const { recordId } = useParams();
  const navigate = useNavigate();
  const [record, setRecord] = useState<DocumentRecord | null>(null);
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  useEffect(() => {
    if (recordId) {
      api.getDocument(recordId).then(doc => setRecord(doc || null));
    }
  }, [recordId]);

  if (!record) return <div className="p-8">Loading workspace...</div>;

  const handleSaveField = async (field: keyof DocumentRecord) => {
    await api.updateRecordField(record.id, field, editValue);
    setEditingField(null);
    const updated = await api.getDocument(record.id);
    setRecord(updated || null);
  };

  const handleApprove = async () => {
    await api.approveRecord(record.id);
    navigate("/verification");
  };

  const renderFieldRow = (label: string, fieldKey: keyof DocumentRecord) => {
    const fieldData = record[fieldKey] as any;
    if (!fieldData || typeof fieldData !== "object") return null;

    const isEditing = editingField === fieldKey;

    return (
      <div className={`p-3 flex items-center justify-between border-b ${fieldData.isFlagged ? "bg-red-50" : ""}`}>
        <div className="w-1/3">
          <p className="text-xs font-semibold text-muted-foreground uppercase">{label}</p>
          {isEditing ? (
            <input 
              autoFocus
              className="mt-1 w-full border rounded px-2 py-1 text-sm"
              value={editValue}
              onChange={e => setEditValue(e.target.value)}
            />
          ) : (
            <p className="font-medium mt-1">{fieldData.value || "—"}</p>
          )}
        </div>
        <div className="w-1/3 flex justify-center">
          {!isEditing && <ConfidenceIndicator score={fieldData.confidence} />}
        </div>
        <div className="w-1/3 flex justify-end">
          {isEditing ? (
            <div className="flex gap-2">
              <button onClick={() => setEditingField(null)} className="text-xs border px-2 py-1 rounded">Cancel</button>
              <button onClick={() => handleSaveField(fieldKey)} className="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">Save</button>
            </div>
          ) : (
            <button onClick={() => { setEditingField(fieldKey as string); setEditValue(fieldData.value?.toString() || ""); }} className="text-muted-foreground hover:text-primary">
              <Edit2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          <Link to="/verification" className="p-2 border rounded-md hover:bg-secondary"><ArrowLeft className="w-4 h-4" /></Link>
          <div>
            <h1 className="text-xl font-bold tracking-tight">Verification Workspace</h1>
            <p className="text-muted-foreground text-sm">Record: {record.recordId}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 border rounded-md text-sm font-medium hover:bg-secondary">Reject</button>
          <button onClick={handleApprove} className="px-4 py-2 bg-status-success text-white rounded-md text-sm font-medium hover:bg-status-success/90 flex items-center gap-2">
            <Check className="w-4 h-4" /> Approve Record
          </button>
        </div>
      </div>

      <div className="flex-1 flex gap-6 min-h-0">
        {/* Source Document Viewer Placeholder */}
        <div className="w-1/2 bg-neutral-200 border rounded-lg shadow-sm flex flex-col items-center justify-center relative overflow-hidden">
          <div className="absolute top-4 left-4 bg-black/60 text-white px-3 py-1 text-xs rounded-md backdrop-blur-sm">
            Source Document: {record.fileName}
          </div>
          <p className="text-muted-foreground font-medium flex items-center gap-2">
            <FileText className="w-5 h-5" /> Document Viewer Placeholder
          </p>
        </div>

        {/* Extracted Record Editor */}
        <div className="w-1/2 bg-card border rounded-lg shadow-sm flex flex-col min-h-0">
          <div className="p-4 border-b bg-secondary/30 flex-shrink-0">
            <h2 className="font-semibold text-lg">Extracted Data</h2>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {record.findings.length > 0 && (
              <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-md">
                <h3 className="text-amber-800 font-bold text-sm flex items-center gap-2 mb-2">
                  <AlertCircle className="w-4 h-4" /> Validation Findings
                </h3>
                <ul className="text-sm text-amber-900 space-y-1 list-disc list-inside">
                  {record.findings.map(f => (
                    <li key={f.id}>{f.message}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="border rounded-md">
              {renderFieldRow("Owner Name", "owner")}
              {renderFieldRow("Khasra No.", "khasra")}
              {renderFieldRow("Khata No.", "khata")}
              {renderFieldRow("Land Area", "landArea")}
              {renderFieldRow("Village", "village")}
              {renderFieldRow("Tehsil", "tehsil")}
              {renderFieldRow("District", "district")}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// adding this so the compiler doesnt complain about FileText not being imported
import { FileText } from "lucide-react";
