# Mock Integrations

## Purpose
The system must demonstrate the *capability* to interface with existing government infrastructure without actually having live credentials to those systems. 

## Adapter Architecture
We will use the Adapter pattern in the backend. 
`GovtIntegrationAdapter(BaseAdapter)` -> implementation calls `http://localhost:8000/mock-api/lrms` instead of a real endpoint.

## Mock Endpoints Required

### 1. LRMS (Land Record Management System) Validation
- **Endpoint**: `GET /mock-api/lrms/khasra/{id}`
- **Behavior**: Given a Khasra number, returns JSON of the "official" record.
- **Scenarios to Mock**:
  - *Match*: Returns data exactly matching the extraction (Validates).
  - *Conflict*: Returns data with a different Area or Owner (Flags a conflict).
  - *Missing*: Returns 404 Not Found (Flags a potential unregistered/legacy parcel).

### 2. DILRMP Registration Linkage
- **Endpoint**: `GET /mock-api/registration/{khasra_id}`
- **Behavior**: Returns recent registration deeds for the parcel to cross-verify ownership changes.

### 3. State GIS System
- **Endpoint**: `GET /mock-api/gis/parcel/{id}`
- **Behavior**: Returns GeoJSON polygons for a given parcel ID to render on the prototype map.

## UI Requirements for Mocks
Any data pulled from these mock APIs must be visually badged in the UI as **"MOCK INTEGRATION DATA"** to maintain absolute transparency during the demo.
