import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { UploadCloud, File, CheckCircle2, ArrowLeft } from "lucide-react";

export const UploadPage = () => {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<"idle" | "uploading" | "success">("idle");

  const handleSimulatedUpload = () => {
    if (!file) return;
    setStatus("uploading");
    setTimeout(() => {
      setStatus("success");
      setTimeout(() => navigate("/documents"), 1500);
    }, 2000);
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/documents" className="p-2 border rounded-md hover:bg-secondary"><ArrowLeft className="w-4 h-4" /></Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Upload Document</h1>
          <p className="text-muted-foreground text-sm mt-1">Upload a scanned land record for digitization.</p>
        </div>
      </div>

      <div className="bg-card border rounded-lg p-8 shadow-sm text-center">
        {status === "success" ? (
          <div className="flex flex-col items-center justify-center py-12">
            <CheckCircle2 className="w-16 h-16 text-status-success mb-4" />
            <h2 className="text-xl font-semibold">Upload Complete</h2>
            <p className="text-muted-foreground mt-2">Document queued for processing.</p>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center">
            <div className="w-20 h-20 bg-secondary rounded-full flex items-center justify-center mb-6 border-4 border-dashed border-muted-foreground/30">
              <UploadCloud className="w-10 h-10 text-muted-foreground" />
            </div>
            <h3 className="text-lg font-medium">Select a file to upload</h3>
            <p className="text-sm text-muted-foreground mt-1 mb-6">PDF, JPG, or PNG up to 10MB</p>
            
            <input 
              type="file" 
              className="hidden" 
              id="file-upload" 
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            
            {!file ? (
              <label htmlFor="file-upload" className="cursor-pointer bg-primary text-primary-foreground px-4 py-2 rounded-md font-medium text-sm hover:bg-primary/90">
                Browse Files
              </label>
            ) : (
              <div className="w-full max-w-sm text-left bg-secondary p-4 rounded-md border flex items-center gap-3">
                <File className="w-8 h-8 text-blue-500" />
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm font-medium truncate">{file.name}</p>
                  <p className="text-xs text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                </div>
              </div>
            )}

            {file && (
              <div className="mt-8 flex gap-4">
                <button 
                  onClick={() => setFile(null)} 
                  className="px-4 py-2 border rounded-md text-sm font-medium hover:bg-secondary"
                  disabled={status === "uploading"}
                >
                  Cancel
                </button>
                <button 
                  onClick={handleSimulatedUpload}
                  disabled={status === "uploading"}
                  className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 flex items-center gap-2"
                >
                  {status === "uploading" ? "Uploading..." : "Start Processing"}
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
