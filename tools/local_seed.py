"""Seeds the LOCAL dev database (wrangler dev) with schema, posts and a test admin.
Test login is stored in worker/.dev-login.txt (gitignored). Never used in production."""
import base64, hashlib, secrets, subprocess, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
run = lambda a: subprocess.run("npx wrangler d1 execute credsey-db --local " + a, cwd=ROOT, shell=True, capture_output=True, stdin=subprocess.DEVNULL).returncode
pw = "dev-" + secrets.token_urlsafe(9)
salt = secrets.token_bytes(16)
h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 100000, 32)
(ROOT / "worker" / ".dev-admin.sql").write_text(
    f"INSERT INTO users (email,name,role,pass) VALUES ('test@credsey.test','Test Admin','admin','pbkdf2$100000${base64.b64encode(salt).decode()}${base64.b64encode(h).decode()}') ON CONFLICT(email) DO UPDATE SET pass=excluded.pass;\n", encoding="utf-8")
codes = [run("--file worker/schema.sql"), run("--file worker/seed-posts.sql"), run("--file worker/.dev-admin.sql")]
(ROOT / "worker" / ".dev-login.txt").write_text(f"test@credsey.test\n{pw}\n", encoding="utf-8")
(ROOT / "worker" / ".dev-admin.sql").unlink()
print("local seed exit codes:", codes)
