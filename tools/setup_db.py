"""One-time database setup: schema, starter blog posts and the first admin login.

Usage: python tools/setup_db.py admin@example.com "Admin Name"
The generated password is written to admin-login.secret.txt (gitignored), never printed.
"""
import base64, hashlib, secrets, subprocess, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
email = sys.argv[1].lower().strip()
name = sys.argv[2] if len(sys.argv) > 2 else "Admin"

def d1(*args):
    r = subprocess.run("npx wrangler d1 execute credsey-db --remote " + " ".join(args), cwd=ROOT, shell=True,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", stdin=subprocess.DEVNULL)
    ok = r.returncode == 0
    print(("ok   " if ok else "FAIL ") + " ".join(args)[:70])
    if not ok: print(r.stdout[-800:], r.stderr[-800:])
    return ok

d1("--file", "worker/schema.sql")
d1("--file", "worker/seed-posts.sql")

pw = secrets.token_urlsafe(12)
salt = secrets.token_bytes(16)
h = hashlib.pbkdf2_hmac("sha256", pw.encode(), salt, 100000, 32)
stored = f"pbkdf2$100000${base64.b64encode(salt).decode()}${base64.b64encode(h).decode()}"
sql = ROOT / "worker" / ".seed-admin.sql"
sql.write_text(f"INSERT INTO users (email,name,role,pass) VALUES ('{email}','{name.replace(chr(39), '')}','admin','{stored}') "
               f"ON CONFLICT(email) DO UPDATE SET pass=excluded.pass, role='admin';\n", encoding="utf-8")
if d1("--file", "worker/.seed-admin.sql"):
    (ROOT / "admin-login.secret.txt").write_text(f"Credsey admin portal: https://credsey.com/admin/\nEmail: {email}\nPassword: {pw}\n(Change it under My account after first sign-in.)\n", encoding="utf-8")
    print("admin login saved to admin-login.secret.txt")
sql.unlink()
