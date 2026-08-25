# Mock Integrations

## Purpose
The system must demonstrate the capability to interface with existing government infrastructure using the **Zero-Cost Constraint**. We do not have live access to government systems, nor do we pay for integration proxies.

## Adapter Architecture
We use the Adapter pattern in the backend to ensure zero-cost local demonstrations. 

Default Implementation: `MockAdapter`
```python
class LRMSAdapter(BaseLRMSAdapter):
    def get_record(self, khasra_id: str):
        # Calls internal http://localhost:8000/mock-api/lrms
        pass
```

## Mock Endpoints Required

### 1. LRMS (Land Record Management System) Validation
- **Interface**: `LRMSAdapter`
- **Behavior**: Given a Khasra number, returns JSON of the "official" record.
- **Scenarios to Mock**:
  - *Match*: Returns data exactly matching the extraction (Validates).
  - *Conflict*: Returns data with a different Area or Owner (Flags a conflict).
  - *Missing*: Returns 404 Not Found (Flags a potential unregistered/legacy parcel).
  - *API Failure/Timeout*: Returns 503 or blocks to test async fault tolerance.

### 2. DILRMP Registration Linkage
- **Interface**: `RegistrationAdapter`
- **Behavior**: Returns recent registration deeds for the parcel.

### 3. State GIS System
- **Interface**: `GovernmentGISAdapter`
- **Behavior**: Returns synthetic or mock GeoJSON polygons for a given parcel ID to render on the local Leaflet map.

## UI Requirements for Mocks
Any data pulled from these mock APIs must be visually badged in the UI as **"MOCK INTEGRATION DATA"** to maintain absolute transparency during the demo.
