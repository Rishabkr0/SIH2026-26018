import React from "react";
import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, FileText, CheckSquare, Database, Map, Users, ShieldAlert, Settings } from "lucide-react";

export const Sidebar = () => {
  const location = useLocation();

  const mainLinks = [
    { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
    { name: "Documents", href: "/documents", icon: FileText },
    { name: "Verification", href: "/verification", icon: CheckSquare },
    { name: "Records", href: "/records", icon: Database },
    { name: "GIS", href: "/gis", icon: Map },
  ];

  const adminLinks = [
    { name: "Users", href: "/users", icon: Users },
    { name: "Validation Rules", href: "/validation-rules", icon: ShieldAlert },
    { name: "Audit Logs", href: "/audit-logs", icon: FileText },
    { name: "Settings", href: "/settings", icon: Settings },
  ];

  const NavItem = ({ name, href, icon: Icon }: any) => {
    const isActive = location.pathname.startsWith(href);
    return (
      <Link
        to={href}
        className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-sm font-medium ${
          isActive
            ? "bg-primary text-primary-foreground"
            : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
        }`}
      >
        <Icon className="w-4 h-4" />
        {name}
      </Link>
    );
  };

  return (
    <aside className="w-64 bg-sidebar border-r flex flex-col h-screen flex-shrink-0">
      <div className="h-14 flex items-center px-4 border-b">
        <span className="font-semibold text-lg tracking-tight text-primary">Bhu-Lekh</span>
      </div>
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        <div>
          <p className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Navigation</p>
          <div className="space-y-1">
            {mainLinks.map((link) => (
              <NavItem key={link.href} {...link} />
            ))}
          </div>
        </div>
        <div>
          <p className="px-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Administration</p>
          <div className="space-y-1">
            {adminLinks.map((link) => (
              <NavItem key={link.href} {...link} />
            ))}
          </div>
        </div>
      </div>
    </aside>
  );
};
