"""Verify deployable artifacts contain the app, rather than a runtime downloader."""

import sys
import tarfile
import zipfile
from pathlib import Path


def check_distributions(directory):
	wheel_path, = directory.glob("procurex-*.whl")
	source_path, = directory.glob("procurex-*.tar.gz")
	backend = {
		"procurex/__init__.py", "procurex/api.py", "procurex/hooks.py",
		"procurex/build.py", "procurex/renderer.py", "procurex/modules.txt",
		"procurex/procurex/doctype/supplier_details/supplier_details.json",
		"procurex/procurex/doctype/avl_vendor_meta/avl_vendor_meta.json",
		"procurex/procurex/doctype/avl_certification/avl_certification.json",
	}
	with zipfile.ZipFile(wheel_path) as wheel:
		names = set(wheel.namelist())
		assert backend <= names, f"Backend missing from wheel: {backend - names}"
		legacy = {
			"procurex_bundle/__init__.py", "procurex_bundle/hooks.py",
			"procurex_bundle/compat.py", "procurex_bundle/modules.txt", "procurex_bundle/patches.txt",
		}
		assert legacy <= names, f"Legacy uninstall bridge missing: {legacy - names}"
		assert "procurex_bundle/backend.py" not in names, "The runtime downloader must not return"
	with tarfile.open(source_path) as source:
		names = {name.split("/", 1)[1] for name in source.getnames() if "/" in name}
		required = backend | legacy | {
			"frontend/package.json", "frontend/package-lock.json", "frontend/vite.config.ts",
			"frontend/src/router.tsx", "package.json", "yarn.lock", "pyproject.toml", "MANIFEST.in",
		}
		assert required <= names, f"Source missing deployment files: {required - names}"
		assert not any("/node_modules/" in name or "/.git/" in name for name in names)
	print("PASS: wheel contains the backend; source contains the backend and React build inputs.")


if __name__ == "__main__":
	check_distributions(Path(sys.argv[1]))
