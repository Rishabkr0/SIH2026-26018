import React from "react";
import { Search, Bell, User } from "lucide-react";

export const TopBar = () => {
  return (
    <header className="h-14 bg-background border-b flex items-center justify-between px-6 flex-shrink-0">
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        {/* Breadcrumb Placeholder */}
        <span>Home</span>
        <span>/</span>
        <span className="text-foreground font-medium">Bhu-Lekh Application</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="relative">
          <Search className="w-4 h-4 absolute left-2.5 top-2.5 text-muted-foreground" />
          <input
            type="text"
            placeholder="Global search..."
            className="h-9 w-64 rounded-md border border-border bg-background pl-9 pr-3 text-sm focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
        <button className="text-muted-foreground hover:text-foreground">
          <Bell className="w-5 h-5" />
        </button>
        <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center border">
          <User className="w-4 h-4 text-secondary-foreground" />
        </div>
      </div>
    </header>
  );
};
