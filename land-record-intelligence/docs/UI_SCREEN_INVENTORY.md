# UI Screen Inventory

## Authentication
- **Login** (P0): Purpose - Secure access. User - All.

## Operations
- **Dashboard** (P0): Purpose - System KPIs. User - Admin/Operator. Data - Counters, charts.
- **Document Upload** (P0): Purpose - Ingest files. User - Operator. Actions - Drag/drop, submit.
- **Document Queue / Status** (P0): Purpose - Track background processing. User - Operator.

## Verification
- **Verification Queue** (P0): Purpose - List of documents needing human review. User - Verifier.
- **Verification Workspace** (P0): Purpose - Core UI. Side-by-side document image and extracted fields. User - Verifier. Actions - Edit, Resolve, Approve, Reject.
- **Conflict Resolution Modal** (P0): Purpose - Resolve data mismatches (e.g., Duplicates). User - Verifier.

## Records
- **Record Search / List** (P0): Purpose - Find digitized records. User - All.
- **Record Detail** (P0): Purpose - View finalized record data and original document link. User - All.
- **Record History / Audit** (P1): Purpose - Traceability. User - Admin/Verifier.

## GIS
- **GIS Map View** (P1): Purpose - Spatial view of parcels. User - Admin/Verifier. Actions - Click polygon to view Record Detail.

## Administration
- **User Management** (P1): Purpose - RBAC. User - Admin.
- **Validation Rules Config** (P2): Purpose - Adjust thresholds. User - SysAdmin.
