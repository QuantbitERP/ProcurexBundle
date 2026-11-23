"""Build the bundled React UI during Bench builds, installs and migrations.

This module also runs directly from package.json, without Frappe or a database.
Node is a build dependency; the published UI is served by Frappe.
"""

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
FRONTEND = APP_ROOT / "frontend"
OUTPUT = APP_ROOT / "procurex" / "public" / "ui"
IGNORED = {"node_modules", "dist", ".git", ".output", ".tanstack", ".nitro", "__pycache__"}


def source_fingerprint():
	files = [Path(__file__), APP_ROOT / "package.json"]
	files.extend(
		path for path in FRONTEND.rglob("*")
		if path.is_file() and not IGNORED.intersection(path.relative_to(FRONTEND).parts)
	)
	digest = hashlib.sha256()
	for path in sorted(files):
		digest.update(str(path.relative_to(APP_ROOT)).encode() + b"\0")
		digest.update(path.read_bytes())
	return digest.hexdigest()


def is_current(fingerprint):
	try:
		manifest = json.loads((OUTPUT / "build.json").read_text())
		return (
			manifest["source"] == fingerprint
			and "index.html" in manifest["files"]
			and all((OUTPUT / name).is_file() for name in manifest["files"])
		)
	except (OSError, ValueError, KeyError, TypeError):
		return False


def node_environment():
	env = os.environ.copy()
	if node_bin := env.get("PROCUREX_NODE_BIN"):
		env["PATH"] = node_bin + os.pathsep + env.get("PATH", "")
	node = shutil.which("node", path=env.get("PATH"))
	npm = shutil.which("npm", path=env.get("PATH"))
	if not node or not npm:
		raise RuntimeError("ProcureX UI builds require Node.js 24+ and npm on PATH, as required by Frappe v16.")
	version = subprocess.check_output([node, "--version"], text=True, env=env).strip()
	if int(version.lstrip("v").split(".")[0]) < 24:
		raise RuntimeError(f"ProcureX UI builds require Node.js 24+; found {version}. Select the bench's Node 24 toolchain.")
	# Vite lives in devDependencies and must be available in production build images.
	env.pop("NODE_ENV", None)
	return npm, env


def install_dependencies(npm, env):
	lock_hash = hashlib.sha256(
		(FRONTEND / "package.json").read_bytes() + (FRONTEND / "package-lock.json").read_bytes()
	).hexdigest()
	marker = FRONTEND / "node_modules" / ".procurex-dependencies"
	if marker.exists() and marker.read_text() == lock_hash and (FRONTEND / "node_modules/vite/bin/vite.js").exists():
		return
	subprocess.run(
		[npm, "ci", "--include=dev", "--no-audit", "--no-fund"],
		cwd=FRONTEND, env=env, check=True,
	)
	marker.write_text(lock_hash)


def atomic_write(path, content):
	with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as file:
		temporary = Path(file.name)
		file.write(content)
	# NamedTemporaryFile starts at 0600; published assets must be readable by nginx.
	temporary.chmod(0o644)
	os.replace(temporary, path)


def publish(fingerprint):
	client = FRONTEND / "dist" / "client"
	shell = client / "_shell.html"
	if not shell.is_file():
		raise RuntimeError(f"ProcureX build did not produce the SPA shell: {shell}")
	OUTPUT.mkdir(parents=True, exist_ok=True)
	# Publish chunks before replacing the shell. Retain older hashed chunks so
	# browsers open during an upgrade can still finish loading their current UI.
	shutil.copytree(client, OUTPUT, dirs_exist_ok=True, ignore=shutil.ignore_patterns("_shell.html"))
	atomic_write(OUTPUT / "index.html", shell.read_bytes())
	files = [str(path.relative_to(client)) for path in client.rglob("*") if path.is_file() and path != shell]
	files.append("index.html")
	atomic_write(OUTPUT / "build.json", (json.dumps({"source": fingerprint, "files": sorted(files)}) + "\n").encode())


def build_custom_ui(install_only=False):
	fingerprint = source_fingerprint()
	if not install_only and is_current(fingerprint):
		print("[procurex] React UI is already built.", flush=True)
		return
	with (APP_ROOT / ".frontend-build.lock").open("w") as lock:
		fcntl.flock(lock, fcntl.LOCK_EX)
		if not install_only and is_current(fingerprint):
			return
		npm, env = node_environment()
		install_dependencies(npm, env)
		if install_only:
			return
		env["NODE_ENV"] = "production"
		subprocess.run([npm, "run", "build"], cwd=FRONTEND, env=env, check=True)
		publish(fingerprint)
		print("[procurex] Published React UI at /procurex.", flush=True)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--install-deps", action="store_true")
	build_custom_ui(install_only=parser.parse_args().install_deps)
