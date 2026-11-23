"""Serve the bundled React UI through Frappe's website router and session."""

import frappe
from frappe.website.page_renderers.base_renderer import BaseRenderer
from frappe.website.utils import build_response

from procurex.build import OUTPUT


class ProcureXSPARenderer(BaseRenderer):
	def can_render(self):
		path = (self.path or "").strip("/")
		return path == "procurex" or path.startswith("procurex/")

	def render(self):
		index = OUTPUT / "index.html"
		if not index.is_file():
			return build_response(
				self.path, "ProcureX UI is unavailable. Run bench build --app procurex.",
				503, {"Cache-Control": "no-store"},
			)
		html = index.read_text(encoding="utf-8")
		csrf = frappe.as_json(frappe.sessions.get_csrf_token())
		user = frappe.as_json(frappe.session.user)
		script = (
			f"<script>window.csrf_token={csrf};window.frappe_user={user};"
			f"document.cookie='csrf_token='+encodeURIComponent({csrf})+';path=/';</script>"
		)
		return build_response(
			self.path, html.replace("</head>", script + "</head>", 1),
			200, {"Cache-Control": "no-store"},
		)
