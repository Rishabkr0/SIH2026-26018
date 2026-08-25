import React from "react";
import { RecordStatus } from "@/types";
import { cn } from "@/lib/utils";

export const StatusBadge = ({ status, className }: { status: RecordStatus, className?: string }) => {
  const statusStyles: Record<RecordStatus, string> = {
    Verified: "bg-status-success/15 text-status-success border-status-success/30",
    "Review Required": "bg-status-warning/15 text-status-warning border-status-warning/30",
    Conflict: "bg-status-error/15 text-status-error border-status-error/30",
    Processing: "bg-status-info/15 text-status-info border-status-info/30",
    Rejected: "bg-muted text-muted-foreground border-border",
    Failed: "bg-destructive/15 text-destructive border-destructive/30"
  };

  return (
    <span className={cn("px-2 py-1 rounded-full text-xs font-semibold border inline-flex items-center", statusStyles[status] || "bg-secondary text-secondary-foreground", className)}>
      {status}
    </span>
  );
};
