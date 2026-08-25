import React from "react";
import { cn } from "@/lib/utils";

export const ConfidenceIndicator = ({ score, showValue = true }: { score: number, showValue?: boolean }) => {
  // score is 0 to 1
  let color = "bg-status-success";
  if (score < 0.8) color = "bg-status-warning";
  if (score < 0.5) color = "bg-status-error";

  return (
    <div className="flex items-center gap-2">
      <div className="w-16 h-1.5 bg-secondary rounded-full overflow-hidden">
        <div className={cn("h-full", color)} style={{ width: `${score * 100}%` }} />
      </div>
      {showValue && <span className="text-xs text-muted-foreground">{(score * 100).toFixed(0)}%</span>}
    </div>
  );
};
