app_name = "procurex"
app_title = "ProcureX"
app_publisher = "Quantbit Technologies Pvt Ltd"
app_description = "ProcureX procurement APIs and bundled React UI"
app_email = "contact@quantbit.io"
app_license = "mit"

required_apps = ["erpnext"]

add_to_apps_screen = [
    {
        "name": "procurex",
        "logo": "/assets/procurex/ui/favicon.ico",
        "title": "ProcureX",
        "route": "/procurex",
    }
]

page_renderer = ["procurex.renderer.ProcureXSPARenderer"]

# Build in the Bench/Cloud asset stage, then reuse that output on each site.
after_build = "procurex.build.build_custom_ui"
after_install = "procurex.build.build_custom_ui"
after_migrate = "procurex.build.build_custom_ui"
