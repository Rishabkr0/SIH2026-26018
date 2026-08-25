# Information Architecture

## Primary Navigation
- **Dashboard**: Overview KPIs, charts, quick links.
- **Documents**: Upload and track raw files.
- **Verification**: Queue for manual review and conflict resolution.
- **Records**: Searchable database of all verified and pending land records.
- **Map (GIS)**: Spatial view of verified parcels.

## Secondary / Admin Navigation
- **Users**: Role management (Admin only).
- **Settings**: Validation rules and system config (Admin only).
- **Audit Logs**: Global system action ledger.

## Page Hierarchy

```text
/ (Login)
├── /dashboard
├── /documents
│   ├── /documents/upload
│   └── /documents/:id (Processing Status / Metadata)
├── /verification
│   ├── /verification/queue
│   └── /verification/:id (Side-by-side Workspace)
├── /records
│   ├── /records/search
│   └── /records/:id (Record Details & History)
├── /map (GIS View)
└── /admin
    ├── /admin/users
    ├── /admin/rules
    └── /admin/audit
```

## Global Elements
- **Top Bar**: Global Search (Khasra/Owner), User Profile, Notifications (Processing complete).
- **Breadcrumbs**: Used in nested pages (e.g., Records > Record #12345 > History).
- **Contextual Navigation**: Quick links from Document -> Verification Workspace -> Final Record.

## Role-Specific Navigation
- **Operator**: Sees Dashboard, Documents.
- **Verifier**: Sees Dashboard, Documents, Verification, Records.
- **Admin**: Sees all including Map and Admin panel.
