import React, { useEffect, useState } from "react";
import { api } from "@/services/api";
import { DocumentRecord } from "@/types";
import { Loader2, CheckCircle2, Circle } from "lucide-react";

export const ProcessingPage = () => {
  const [processing, setProcessing] = useState<DocumentRecord[]>([]);

  useEffect(() => {
    api.getDocuments().then(docs => {
      setProcessing(docs.filter(d => d.status === "Processing"));
    });
  }, []);

  const Step = ({ name, active, done }: { name: string, active: boolean, done: boolean }) => (
    <div className="flex flex-col items-center flex-1">
      <div className={`w-8 h-8 rounded-full flex items-center justify-center mb-2 ${
        done ? "bg-status-success text-white" : active ? "bg-primary text-primary-foreground animate-pulse" : "bg-secondary text-muted-foreground border"
      }`}>
        {done ? <CheckCircle2 className="w-5 h-5" /> : active ? <Loader2 className="w-5 h-5 animate-spin" /> : <Circle className="w-5 h-5" />}
      </div>
      <p className={`text-xs font-medium text-center ${active || done ? "text-foreground" : "text-muted-foreground"}`}>{name}</p>
    </div>
  );

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Active Processing</h1>
        <p className="text-muted-foreground text-sm mt-1">Live view of the asynchronous Redis/Celery background queue.</p>
      </div>

      <div className="space-y-4">
        {processing.map(doc => (
          <div key={doc.id} className="bg-card border rounded-lg shadow-sm p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="font-semibold text-lg">{doc.fileName}</h3>
                <p className="text-xs text-muted-foreground">ID: {doc.recordId || doc.id}</p>
              </div>
              <span className="text-xs bg-status-info/15 text-status-info px-2 py-1 rounded-full font-bold">Processing</span>
            </div>

            <div className="flex items-start justify-between relative px-4">
              <div className="absolute top-4 left-8 right-8 h-0.5 bg-secondary -z-10" />
              <Step name="Uploaded" done={true} active={false} />
              <Step name="Preprocessing" done={true} active={false} />
              <Step name="Local OCR" done={false} active={true} />
              <Step name="Extraction" done={false} active={false} />
              <Step name="Validation" done={false} active={false} />
            </div>
          </div>
        ))}
        {processing.length === 0 && (
          <div className="bg-card border rounded-lg p-12 text-center text-muted-foreground">
            No documents are currently processing.
          </div>
        )}
      </div>
    </div>
  );
};
