"""UI lifecycle checks that run without a site or database."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from procurex import build
from procurex.renderer import ProcureXSPARenderer


class TestUIBuild(unittest.TestCase):
	def setUp(self):
		self.temp = tempfile.TemporaryDirectory()
		self.addCleanup(self.temp.cleanup)
		self.root = Path(self.temp.name)
		self.frontend = self.root / "frontend"
		self.client = self.frontend / "dist/client"
		self.client.mkdir(parents=True)
		self.output = self.root / "public/ui"
		for name, value in (("APP_ROOT", self.root), ("FRONTEND", self.frontend), ("OUTPUT", self.output)):
			patcher = patch.object(build, name, value)
			patcher.start()
			self.addCleanup(patcher.stop)

	def test_publish_retains_open_browser_chunks_and_readable_assets(self):
		self.output.mkdir(parents=True)
		(self.output / "old-hash.js").write_text("old")
		(self.client / "new-hash.js").write_text("new")
		(self.client / "_shell.html").write_text('<script src="new-hash.js"></script>')
		build.publish("fingerprint")
		self.assertEqual((self.output / "old-hash.js").read_text(), "old")
		self.assertEqual((self.output / "new-hash.js").read_text(), "new")
		self.assertTrue(build.is_current("fingerprint"))
		self.assertEqual((self.output / "index.html").stat().st_mode & 0o777, 0o644)
		(self.output / "new-hash.js").unlink()
		self.assertFalse(build.is_current("fingerprint"))

	def test_failed_build_keeps_existing_shell(self):
		self.output.mkdir(parents=True)
		(self.output / "index.html").write_text("working UI")
		with self.assertRaisesRegex(RuntimeError, "SPA shell"):
			build.publish("new")
		self.assertEqual((self.output / "index.html").read_text(), "working UI")

	def test_install_or_migrate_reuses_cloud_build_without_node_or_writes(self):
		self.output.mkdir(parents=True)
		(self.output / "index.html").write_text("built in asset stage")
		(self.output / "build.json").write_text(json.dumps({"source": "ready", "files": ["index.html"]}))
		with patch.object(build, "source_fingerprint", return_value="ready"), patch.object(build, "node_environment") as node:
			build.build_custom_ui()
			node.assert_not_called()
		self.assertFalse((self.root / ".frontend-build.lock").exists())

	def test_renderer_only_claims_procurex_routes(self):
		renderer = ProcureXSPARenderer.__new__(ProcureXSPARenderer)
		for route, expected in (("procurex", True), ("procurex/auth", True), ("procurex/supplier-portal/rfq", True), ("procurex-other", False), ("app", False), ("login", False), ("foundry-ui", False)):
			with self.subTest(route=route):
				renderer.path = route
				self.assertEqual(renderer.can_render(), expected)


if __name__ == "__main__":
	unittest.main()
