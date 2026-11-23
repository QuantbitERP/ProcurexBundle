"""Retire wrapper metadata through Frappe's normal uninstall path."""


def before_install():
	raise RuntimeError(
		"procurex_bundle is obsolete. Install the single procurex app instead: "
		"bench --site <site> install-app procurex. "
		"The legacy module is included only to let existing sites uninstall the wrapper."
	)


def before_uninstall():
	import frappe

	# Never remove unexpected customer DocTypes along with this empty wrapper.
	# The procurement DocTypes belong to procurex and are not queried here.
	modules = frappe.get_all(
		"Module Def", filters={"app_name": "procurex_bundle", "custom": 0}, pluck="name"
	)
	if modules:
		doctypes = frappe.get_all("DocType", filters={"module": ["in", modules]}, pluck="name")
		if doctypes:
			raise RuntimeError(
				"The legacy wrapper owns DocTypes; stop and review before uninstalling: "
				+ ", ".join(sorted(doctypes))
			)
