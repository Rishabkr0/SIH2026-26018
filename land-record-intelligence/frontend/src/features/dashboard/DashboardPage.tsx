import React, { useEffect, useState } from "react";
import { api } from "@/services/api";
import { DashboardMetrics } from "@/types";
import { FileText, CheckCircle, AlertTriangle, ListTodo, Activity, ShieldAlert } from "lucide-react";

export const DashboardPage = () => {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);

  useEffect(() => {
    api.getDashboardMetrics().then(setMetrics);
  }, []);

  if (!metrics) return <div className="p-8">Loading dashboard...</div>;

  const cards = [
    { title: "Total Uploaded", value: metrics.totalUploaded, icon: FileText, color: "text-blue-500" },
    { title: "Processing", value: metrics.processing, icon: Activity, color: "text-blue-400" },
    { title: "Pending Verification", value: metrics.pendingVerification, icon: ListTodo, color: "text-amber-500" },
    { title: "Low Confidence", value: metrics.lowConfidence, icon: AlertTriangle, color: "text-orange-500" },
    { title: "Conflicts Detected", value: metrics.conflicts, icon: ShieldAlert, color: "text-red-500" },
    { title: "Verified Records", value: metrics.verified, icon: CheckCircle, color: "text-green-500" },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">System Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">Overview of digitization pipeline and verification queue.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {cards.map((card, i) => (
          <div key={i} className="bg-card border rounded-lg p-6 flex items-center justify-between shadow-sm">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{card.title}</p>
              <h3 className="text-3xl font-bold mt-2">{card.value}</h3>
            </div>
            <div className={`p-3 bg-secondary rounded-full ${card.color}`}>
              <card.icon className="w-6 h-6" />
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <div className="bg-card border rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="text-sm text-muted-foreground italic">Activity feed will be connected to audit logs...</div>
          </div>
        </div>
        <div className="bg-card border rounded-lg p-6 shadow-sm">
          <h3 className="text-lg font-semibold mb-4">Verification Priority</h3>
          <div className="space-y-4">
             <div className="text-sm text-muted-foreground italic">Queue priorities will be displayed here...</div>
          </div>
        </div>
      </div>
    </div>
  );
};
