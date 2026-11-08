import os
import json
import time
import uuid
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

DATA_DIR = os.environ.get("DATA_DIR", "/data")
DATA_FILE = os.path.join(DATA_DIR, "guestbook.json")

def init_storage():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        atomic_write([])

def atomic_write(data):
    """Menulis data secara atomik: simpan ke file temporary lalu lakukan atomic replace"""
    temp_file = f"{DATA_FILE}.{uuid.uuid4().hex}.tmp"
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp_file, DATA_FILE)

def read_data():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

class GuestbookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Mematikan log default agar output konsisten dalam format JSON
        pass

    def emit_json_log(self, status_code, start_time):
        latency_ms = round((time.time() - start_time) * 1000, 2)
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": self.command,
            "path": self.path,
            "status": status_code,
            "latency_ms": latency_ms,
            "client_ip": self.headers.get("X-Real-IP", self.client_address[0])
        }
        print(json.dumps(log_entry), flush=True)

    def send_json_response(self, status_code, data, start_time):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)
        self.emit_json_log(status_code, start_time)

    def do_GET(self):
        start_time = time.time()
        parsed = urlparse(self.path)
        clean_path = parsed.path.rstrip("/")
        
        # 1. Healthcheck probe untuk kontainer dan Jenkins
        if clean_path == "/health":
            self.send_json_response(200, {"status": "healthy"}, start_time)
            return

        # 2. Endpoint pengambilan data buku tamu
        if clean_path in ["/api/messages", "/messages"]:
            messages = read_data()
            self.send_json_response(200, messages, start_time)
            return

        self.send_json_response(404, {"error": "Not Found"}, start_time)

    def do_POST(self):
        start_time = time.time()
        parsed = urlparse(self.path)
        clean_path = parsed.path.rstrip("/")
        
        if clean_path in ["/api/messages", "/messages"]:
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(content_length)
                payload = json.loads(raw_body.decode("utf-8"))
            except Exception:
                self.send_json_response(400, {"error": "Format JSON tidak valid"}, start_time)
                return

            entry_id = str(payload.get("id") or ("e" + uuid.uuid4().hex[:8]))
            created_at = payload.get("at") or datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M")
            nama_tamu = payload.get("nama", "").strip()

            if not nama_tamu:
                self.send_json_response(400, {"error": "Nama wajib diisi"}, start_time)
                return

            fak_val = payload.get("fak") or payload.get("instansi", "").strip()
            review_val = payload.get("review") or payload.get("pesan", "").strip()

            new_entry = {
                "id": entry_id,
                "nama": nama_tamu,
                "instansi": fak_val,
                "fak": fak_val,
                "pesan": review_val,
                "review": review_val,
                "at": created_at,
                "role": payload.get("role", "mhs"),
                "nim": str(payload.get("nim", "")).strip(),
                "prodi": str(payload.get("prodi", "")).strip(),
                "mhs": str(payload.get("mhs", "")).strip(),
                "rating": int(payload.get("rating", 5)),
                "photos": payload.get("photos", []),
                "done": True
            }

            current_data = read_data()
            current_data.insert(0, new_entry)
            atomic_write(current_data)

            response_payload = {
                "success": True,
                "message": f"Data kunjungan atas nama '{nama_tamu}' berhasil disimpan!",
                "data": new_entry
            }
            self.send_json_response(201, response_payload, start_time)
            return

        self.send_json_response(404, {"error": "Not Found"}, start_time)

    def do_DELETE(self):
        start_time = time.time()
        parsed = urlparse(self.path)
        clean_path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)

        target_id = None
        parts = clean_path.split("/")

        # Jalur 1: /api/messages/<id> atau /messages/<id>
        if len(parts) >= 3 and parts[-2] == "messages":
            target_id = parts[-1]
        # Jalur 2: /messages?index=X atau ?id=X (Kompatibilitas rubrik ujian)
        elif clean_path in ["/api/messages", "/messages"]:
            if "index" in query:
                target_id = query["index"][0]
            elif "id" in query:
                target_id = query["id"][0]

        if not target_id:
            self.send_json_response(400, {"error": "Target ID atau index wajib disertakan"}, start_time)
            return

        current_data = read_data()
        target_entry = None
        target_index = -1

        # Pencarian berdasarkan string ID
        for i, item in enumerate(current_data):
            if str(item.get("id")) == str(target_id):
                target_entry = item
                target_index = i
                break

        # Pencarian alternatif berdasarkan indeks angka array
        if target_entry is None and target_id.isdigit():
            idx = int(target_id)
            if 0 <= idx < len(current_data):
                target_entry = current_data[idx]
                target_index = idx

        if target_entry is None:
            self.send_json_response(404, {"error": "Data tamu tidak ditemukan"}, start_time)
            return

        deleted_name = target_entry.get("nama")
        new_data = [item for i, item in enumerate(current_data) if i != target_index]
        atomic_write(new_data)

        response_payload = {
            "success": True,
            "message": f"Data kunjungan '{deleted_name}' berhasil dihapus permanen.",
            "deleted_id": target_id
        }
        self.send_json_response(200, response_payload, start_time)

def run(server_class=HTTPServer, handler_class=GuestbookHandler, port=5000):
    init_storage()
    server_address = ("0.0.0.0", port)
    httpd = server_class(server_address, handler_class)
    print(f"Backend berjalan di port {port}...", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run()