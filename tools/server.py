import http.server
import socketserver
import os
import json
import subprocess
import urllib.parse

# ── Auto-carga del archivo .env ──────────────────────────────────────────────
def load_dotenv(env_path):
    """Carga variables de entorno desde un archivo .env sin dependencias externas."""
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding='utf-8-sig') as f:  # utf-8-sig elimina el BOM de Windows
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, _, value = line.partition('=')
            os.environ.setdefault(key.strip(), value.strip())

_ENV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(_ENV_FILE)
# ─────────────────────────────────────────────────────────────────────────────

PORT = 8050
REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class GeneratorHandler(http.server.BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == "/" or path == "/generator":
            self.serve_file(os.path.join(REPO_DIR, "tools", "generator_ui.html"), "text/html")
            return
            
        if path == "/api/templates":
            self.list_templates()
            return

        if path == "/api/config":
            self.send_config()
            return

        # Serve static files from REPO_DIR
        rel_path = path.lstrip('/')
        full_path = os.path.abspath(os.path.join(REPO_DIR, rel_path))
        
        # Security check: ensure path is within REPO_DIR
        if not full_path.startswith(REPO_DIR):
            self.send_error(403, "Access Forbidden")
            return
            
        if os.path.exists(full_path) and os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            mime_types = {
                ".html": "text/html",
                ".css": "text/css",
                ".js": "application/javascript",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".gif": "image/gif",
                ".svg": "image/svg+xml",
                ".json": "application/json",
            }
            mime = mime_types.get(ext, "application/octet-stream")
            self.serve_file(full_path, mime)
        else:
            self.send_error(404, "File Not Found")

    def serve_file(self, file_path, mime_type):
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {e}")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        if path == "/api/publish":
            self.handle_publish()
            return
        
        self.send_error(404, "Endpoint not found")

    def send_config(self):
        """Expone la GOOGLE_API_KEY al frontend de forma segura (solo local)."""
        api_key = os.environ.get('GOOGLE_API_KEY', '')
        self.send_json_response(200, {"google_api_key": api_key})

    def list_templates(self):
        try:
            files = [f for f in os.listdir(REPO_DIR) if f.startswith("carta_") and f.endswith(".html")]
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"templates": files}).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def handle_publish(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            req_data = json.loads(post_data.decode('utf-8'))
            filename = req_data.get("filename")
            html_content = req_data.get("html")
            trainer_name = req_data.get("trainer_name", "Entrenador")
            
            if not filename or not html_content:
                self.send_json_response(400, {"error": "Missing filename or html content"})
                return
                
            filename = os.path.basename(filename)
            if not filename.endswith(".html"):
                filename += ".html"
                
            full_file_path = os.path.join(REPO_DIR, filename)
            
            # 1. Save file
            with open(full_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            # 2. Git steps
            # git add
            add_res = subprocess.run(["git", "add", "-f", filename], cwd=REPO_DIR, capture_output=True, text=True)
            if add_res.returncode != 0:
                self.send_json_response(500, {
                    "error": f"Error running 'git add': {add_res.stderr}",
                    "stage": "git add"
                })
                return
                
            # git commit
            commit_msg = f"Agregar carta de bienvenida y radar para {trainer_name}"
            commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=REPO_DIR, capture_output=True, text=True)
            if commit_res.returncode != 0 and "nothing to commit" not in commit_res.stdout:
                self.send_json_response(500, {
                    "error": f"Error running 'git commit': {commit_res.stderr}",
                    "stage": "git commit"
                })
                return
                
            # git push
            push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)
            if push_res.returncode != 0:
                self.send_json_response(500, {
                    "error": f"Error running 'git push': {push_res.stderr}",
                    "stage": "git push"
                })
                return
                
            # Success
            self.send_json_response(200, {
                "success": True,
                "filename": filename,
                "url": f"https://crearpsl.net/{filename}",
                "git_output": push_res.stdout + "\n" + push_res.stderr
            })
            
        except Exception as e:
            self.send_json_response(500, {"error": str(e)})

    def send_json_response(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

class MyTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

if __name__ == "__main__":
    print(f"Iniciando servidor local en el puerto {PORT}...")
    print(f"Sirviendo repositorio: {REPO_DIR}")
    api_key_status = "[OK] GOOGLE_API_KEY cargada" if os.environ.get('GOOGLE_API_KEY') else "[WARN] GOOGLE_API_KEY NO encontrada (revisa el archivo .env)"
    print(api_key_status)
    
    with MyTCPServer(("", PORT), GeneratorHandler) as httpd:
        print(f"Servidor activo en http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServidor detenido.")
