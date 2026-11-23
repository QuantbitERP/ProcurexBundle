"""Allow existing installed-app entries to load until the wrapper is removed."""

app_name = "procurex_bundle"
app_title = "ProcureX Bundle (legacy migration bridge)"
app_publisher = "Quantbit Technologies Pvt Ltd"
app_description = "Compatibility imports for uninstalling the obsolete wrapper"
app_email = "contact@quantbit.io"
app_license = "mit"

before_install = "procurex_bundle.compat.before_install"
before_uninstall = "procurex_bundle.compat.before_uninstall"
