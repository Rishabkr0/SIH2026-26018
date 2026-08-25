# User Roles

## 1. Digitization Operator
**Objective**: Ingest physical and legacy digital records into the system efficiently.
**Responsibilities**: Upload documents, monitor processing queue, identify documents requiring review.
**Allowed Actions**: Upload files, view processing status, view document list.
**Restricted Actions**: Cannot verify/approve records, cannot manage users, cannot change system rules.
**Screens Needed**: Dashboard, Document Upload, Document Queue, Processing Status.
**Data Visibility**: Uploaded documents and extraction status.

## 2. Verification Officer
**Objective**: Ensure accuracy of extracted data and resolve conflicts before finalizing records.
**Responsibilities**: Inspect low-confidence fields, compare data to source document, correct fields, resolve validation findings, approve/reject records.
**Allowed Actions**: View verification queue, edit extracted fields, add comments, approve, reject, resolve validation findings, search records.
**Restricted Actions**: Cannot modify validation rules, cannot manage users.
**Screens Needed**: Verification Queue, Verification Workspace, Record Search, Record Detail.
**Data Visibility**: All processed documents, validation findings, verified records.

## 3. District/State Administrator
**Objective**: Monitor overall system performance and operator efficiency.
**Responsibilities**: Monitor processing metrics, review QA/QC workloads, manage users, review major conflicts.
**Allowed Actions**: View all dashboards, view audit logs, manage (add/remove) users, view GIS maps.
**Restricted Actions**: Typically does not perform primary verification (though may have override capabilities), cannot change deep system configurations.
**Screens Needed**: Dashboard, User Management, Audit Logs, GIS Map, Records Search.
**Data Visibility**: Full read access to all records and logs.

## 4. System Administrator
**Objective**: Maintain system health, security, and integration rules.
**Responsibilities**: Manage system configuration, roles, validation rules, and integrations.
**Allowed Actions**: Edit validation rule configurations, manage roles/permissions, manage system settings.
**Restricted Actions**: N/A (Superuser)
**Screens Needed**: Validation Rules, System Settings, Audit Logs, Integrations.
**Data Visibility**: Unrestricted.

## 5. Citizen / Landowner
*Note: Considered indirect beneficiaries for the prototype.*
**Objective**: Benefit from faster, accurate land record digitization.
**Responsibilities**: N/A
**Allowed Actions**: N/A
**Screens Needed**: N/A

## Permission Matrix
| Action | Operator | Verifier | Admin | SysAdmin |
|---|---|---|---|---|
| Upload Documents | Yes | No | Yes | Yes |
| View Documents | Yes | Yes | Yes | Yes |
| Edit Extractions | No | Yes | No | Yes |
| Approve/Reject | No | Yes | No | Yes |
| Manage Users | No | No | Yes | Yes |
| Config Rules | No | No | No | Yes |
| View Audit Logs | No | No | Yes | Yes |
