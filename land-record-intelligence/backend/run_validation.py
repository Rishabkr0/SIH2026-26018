import httpx
import io
import time

BASE_URL = "http://localhost:8000"

def run_test(name, fn):
    print(f"--- {name} ---")
    try:
        fn()
    except Exception as e:
        print(f"FAIL: {e}")
    print("\n")

def test_health():
    with httpx.Client() as client:
        res = client.get(f"{BASE_URL}/health")
        print(f"GET /health: {res.status_code}")
        print(res.text)

def test_api_health():
    with httpx.Client() as client:
        res = client.get(f"{BASE_URL}/api/v1/health")
        print(f"GET /api/v1/health: {res.status_code}")
        print(res.text)

document_id = None

def test_upload():
    global document_id
    pdf_content = b"%PDF-1.4\nTest PDF"
    files = {"file": ("test.pdf", io.BytesIO(pdf_content), "application/pdf")}
    with httpx.Client() as client:
        res = client.post(f"{BASE_URL}/api/v1/documents", files=files)
        print(f"POST /api/v1/documents: {res.status_code}")
        print(res.text)
        if res.status_code == 201:
            data = res.json()
            document_id = data["document"]["id"]

def test_get_doc():
    if not document_id:
        print("Skipped (no doc ID)")
        return
    with httpx.Client() as client:
        res = client.get(f"{BASE_URL}/api/v1/documents/{document_id}")
        print(f"GET /api/v1/documents/ID: {res.status_code}")
        print(res.text)

def test_get_processing():
    if not document_id:
        print("Skipped (no doc ID)")
        return
    with httpx.Client() as client:
        res = client.get(f"{BASE_URL}/api/v1/documents/{document_id}/processing")
        print(f"GET /api/v1/documents/ID/processing: {res.status_code}")
        print(res.text)

def test_get_file():
    if not document_id:
        print("Skipped (no doc ID)")
        return
    with httpx.Client() as client:
        res = client.get(f"{BASE_URL}/api/v1/documents/{document_id}/file")
        print(f"GET /api/v1/documents/ID/file: {res.status_code}")
        print(f"Content length: {len(res.content)}")

def test_unsupported_type():
    content = b"fake"
    files = {"file": ("test.txt", io.BytesIO(content), "text/plain")}
    with httpx.Client() as client:
        res = client.post(f"{BASE_URL}/api/v1/documents", files=files)
        print(f"POST unsupported type: {res.status_code}")
        print(res.text)

def test_oversized():
    # 11MB
    content = b"0" * (11 * 1024 * 1024)
    files = {"file": ("large.pdf", io.BytesIO(content), "application/pdf")}
    with httpx.Client() as client:
        res = client.post(f"{BASE_URL}/api/v1/documents", files=files)
        print(f"POST oversized: {res.status_code}")
        print(res.text[:200])

def test_not_found():
    with httpx.Client() as client:
        res = client.get(f"{BASE_URL}/api/v1/documents/00000000-0000-0000-0000-000000000000")
        print(f"GET nonexistent doc: {res.status_code}")
        print(res.text)

if __name__ == "__main__":
    run_test("Health", test_health)
    run_test("API Health", test_api_health)
    run_test("Upload valid PDF", test_upload)
    run_test("Get Doc", test_get_doc)
    run_test("Get Processing Job", test_get_processing)
    run_test("Get File Stream", test_get_file)
    run_test("Unsupported Type", test_unsupported_type)
    run_test("Oversized File", test_oversized)
    run_test("Nonexistent Doc", test_not_found)
