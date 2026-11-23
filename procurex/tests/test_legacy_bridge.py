"""Existing wrapper registrations must be removable without losing backend data."""

import sys
import types
import unittest
from unittest.mock import Mock, patch

from procurex_bundle import compat, hooks


class TestLegacyBridge(unittest.TestCase):
	def test_fresh_sites_cannot_install_the_obsolete_wrapper(self):
		with self.assertRaisesRegex(RuntimeError, "install-app procurex"):
			compat.before_install()
		self.assertFalse(hasattr(hooks, "after_install"))
		self.assertFalse(hasattr(hooks, "page_renderer"))

	def test_empty_wrapper_can_be_retired_without_querying_backend_doctypes(self):
		frappe = types.SimpleNamespace(get_all=Mock(side_effect=[["Procurex Bundle"], []]))
		with patch.dict(sys.modules, {"frappe": frappe}):
			compat.before_uninstall()
		self.assertEqual(frappe.get_all.call_args_list[0].kwargs["filters"]["app_name"], "procurex_bundle")
		self.assertEqual(frappe.get_all.call_args_list[1].kwargs["filters"]["module"], ["in", ["Procurex Bundle"]])

	def test_unexpected_wrapper_doctypes_block_uninstallation(self):
		frappe = types.SimpleNamespace(get_all=Mock(side_effect=[["Procurex Bundle"], ["Customer Wrapper DocType"]]))
		with patch.dict(sys.modules, {"frappe": frappe}), self.assertRaisesRegex(RuntimeError, "Customer Wrapper DocType"):
			compat.before_uninstall()


if __name__ == "__main__":
	unittest.main()
