# User Journeys

## A. Login
- **Actor**: Any User
- **Trigger**: Navigates to app URL
- **Steps**: 1. Enter credentials. 2. Submit.
- **Success State**: Redirected to role-based dashboard.
- **Failure State**: Invalid credentials message.

## B. Upload Document
- **Actor**: Digitization Operator
- **Trigger**: Clicks "Upload Document"
- **Steps**: 1. Select PDF/Image. 2. Verify preview. 3. Click Upload.
- **System Response**: Validates file, generates checksum, stores, and queues.
- **Success State**: Document appears in processing queue with "Pending" status.
- **Edge Cases**: Unsupported file format, file too large.

## C. Process Document (System)
- **Actor**: System (Background)
- **Trigger**: Document added to queue.
- **Steps**: Preprocessing -> OCR -> Extraction -> Confidence -> Validation.
- **System Response**: Updates document status to "Review Required" or "Failed".
- **Success State**: Structured fields and validation findings generated.

## D. Low-Confidence Review
- **Actor**: Verification Officer
- **Trigger**: Opens "Verification Queue" and selects a document.
- **Preconditions**: Document status is "Review Required".
- **Steps**: 1. Review side-by-side UI. 2. Spot flagged (yellow/red) fields. 3. Look at source document highlight. 4. Correct text. 5. Save correction.
- **Success State**: Field confidence indicator clears, audit log records change.

## E. Validation Conflict / Duplicate Detection
- **Actor**: Verification Officer
- **Trigger**: Validation Engine flags a conflict (e.g., Area mismatch, Duplicate Khasra).
- **Steps**: 1. UI displays "Validation Findings" pane. 2. Officer views both conflicting records. 3. Decides truth based on source. 4. Adds resolution comment. 5. Marks finding as resolved.
- **Success State**: Finding cleared, ready for approval.

## F. Record Approval
- **Actor**: Verification Officer
- **Trigger**: All low-confidence fields reviewed, conflicts resolved.
- **Steps**: 1. Click "Approve". 2. Confirm.
- **System Response**: Updates status to VERIFIED. Logs approval.
- **Success State**: Record is now searchable and included in GIS/Dashboard stats.

## G. Record Rejection
- **Actor**: Verification Officer
- **Trigger**: Document is unreadable or completely invalid.
- **Steps**: 1. Click "Reject". 2. Enter reason.
- **System Response**: Updates status to REJECTED.

## H. Search Record
- **Actor**: Administrator / Verifier
- **Trigger**: Needs to find a specific land record.
- **Steps**: 1. Enter Khasra number or Owner Name in global search. 2. View results. 3. Click to open details.
- **Success State**: Record Detail page loads.

## I. Dashboard Monitoring
- **Actor**: Administrator
- **Trigger**: Logs in to check operations.
- **Steps**: 1. View KPI cards (Total Uploaded, Pending Verification). 2. View charts (Accuracy, Processing Time).
- **Success State**: Real-time insights based on DB queries.

## J. Audit Inspection
- **Actor**: Administrator
- **Trigger**: Investigating a changed field.
- **Steps**: 1. Go to Record Detail. 2. Click "History/Audit". 3. View timeline of old vs new values and who changed them.
- **Success State**: Full accountability traced.
