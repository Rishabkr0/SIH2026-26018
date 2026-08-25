import React from "react";
import { Map as MapIcon, Filter, Layers } from "lucide-react";

export const GisPage = () => {
  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      <div className="flex items-center justify-between mb-4 flex-shrink-0">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">GIS Visualization</h1>
          <p className="text-muted-foreground text-sm mt-1">Spatial view of verified land parcels.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="px-4 py-2 border rounded-md text-sm font-medium hover:bg-secondary flex items-center gap-2">
            <Layers className="w-4 h-4" /> Base Map
          </button>
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium flex items-center gap-2 hover:bg-primary/90">
            <Filter className="w-4 h-4" /> Spatial Filter
          </button>
        </div>
      </div>

      <div className="flex-1 bg-secondary border rounded-lg shadow-sm flex items-center justify-center relative overflow-hidden">
        {/* Placeholder for Leaflet */}
        <div className="text-center">
          <MapIcon className="w-16 h-16 text-muted-foreground/30 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-muted-foreground">Interactive Map Placeholder</h3>
          <p className="text-sm text-muted-foreground/80 mt-2 max-w-sm mx-auto">
            This container is ready to be integrated with Leaflet/MapLibre and PostGIS. It will display synthetic parcel boundaries overlaying an open tile service for the P1 MVP demonstration.
          </p>
        </div>
      </div>
    </div>
  );
};
