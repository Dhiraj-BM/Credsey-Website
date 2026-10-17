"""Creates a random admin key, saves it locally and uploads it as the ADMIN_KEY worker secret."""
import secrets, subprocess, pathlib

key = secrets.token_urlsafe(24)
pathlib.Path("admin-key.secret.txt").write_text(f"Credsey leads admin key — open https://credsey.com/admin/\n{key}\n", encoding="utf-8")
r = subprocess.run("npx --yes wrangler secret put ADMIN_KEY", input=key, text=True, encoding="utf-8", errors="replace", shell=True, capture_output=True)
print("ADMIN_KEY set" if r.returncode == 0 else "failed")
