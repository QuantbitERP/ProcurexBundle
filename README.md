# ProcureX

One Frappe v16 app containing the procurement backend and the React UI.
Install **only `procurex`**. No wrapper app, frontend repository clone, PM2,
Next.js server, Nitro server, separate port, or proxy configuration is needed.

## Layout

```text
procurex/
  procurex/
    api.py                  # existing procurex.api.* endpoints
    procurex/doctype/       # existing procurement DocTypes
    build.py                # automatic frontend build and publish
    renderer.py             # Frappe renderer for /procurex/*
    public/ui/              # generated static UI
  frontend/
    src/                    # React pages and components, versioned in this repo
    public/
    vite.config.ts
    package.json
    package-lock.json
  package.json              # normal Bench dependency/build commands
  yarn.lock
  pyproject.toml
```

## Install on a Bench

Use a Frappe v16 bench with ERPNext installed, Python 3.14+, and its supported
Node 24+ / npm / Yarn toolchain. Node is used to compile assets, not to serve
ProcureX in production. No developer-specific Node path is required.

For a local bench managed with nvm, select Node 24 in the terminal before
running Bench commands. This selects Node for that terminal without changing
the global default or other benches:

```bash
cd /path/to/frappe-bench
source "$HOME/.nvm/nvm.sh"
nvm use 24
node --version
```

The version must be 24 or newer. Do not bypass Yarn's engine check: Frappe
itself requires this Node version, even before ProcureX's build starts.

```bash
bench get-app https://github.com/QuantbitERP/ProcurexBundle.git --branch version-16
bench --site <site> install-app procurex
```

Open `https://<site>/procurex`. ProcureX also appears on the Frappe apps screen.
`bench get-app` installs the frontend dependencies and builds the UI through the
normal asset build. `after_install` ensures the UI is available if assets were
skipped earlier. Build errors fail visibly rather than reporting a successful
install with a missing UI.

```bash
# After updating the app, the normal Bench build publishes the updated UI.
bench build --app procurex
```

`after_migrate` also checks the bundled UI. An unchanged, complete build is
reused without running npm, requiring Node at runtime, or writing app files.
Builds on the same bench share a lock. Assets are published before the shell,
and old hashed chunks remain available to already-open browser sessions.

## Frappe Cloud

Publish this `version-16` branch of `QuantbitERP/ProcurexBundle`, add **procurex** to a compatible
Frappe v16 custom-app bench with ERPNext, deploy it, and install it on the site.
The GitHub repository is named `ProcurexBundle`; its single Frappe app is named
`procurex`. Bench uses the Python package name and creates `apps/procurex`.
Do not install a second app named `procurex_bundle` or the standalone React repository.

The root `package.json` installs the nested frontend dependencies with `npm ci`
(including build-time dev dependencies). Its build script produces static UI
assets in the normal Bench/Cloud asset stage. The site then serves `/procurex`
through Frappe, using the same-origin `/api` endpoints, session cookie and CSRF
token. No extra web process is created.

The structure follows Frappe Cloud's documented nested frontend
[dependency installation pattern](https://docs.frappe.io/cloud/common-issues/vite-not-found)
and Frappe's [build and install hooks](https://docs.frappe.io/framework/user/en/python-api/hooks).
The build and site lifecycle have been tested locally; a Frappe Cloud deployment
must use the published consolidated code and has not been performed here.

## Existing installations using the wrapper

The backend app name, API paths, DocTypes and existing procurement records remain
`procurex`. Build the consolidated app first. Back up the site, then preview
removing the empty wrapper:

```bash
bench build --app procurex
bench --site <site> backup --with-files
bench --site <site> uninstall-app procurex_bundle --dry-run
```

Verify that only the wrapper's empty module is listed. Uninstall **only** the
wrapper, then clear cache:

```bash
bench --site <site> uninstall-app procurex_bundle --yes
bench --site <site> clear-cache
```

Once no site uses the wrapper, its old source can be archived outside `apps/`.
Do not uninstall `procurex`; it owns the procurement data.

## Existing integrations

The UI and business APIs are preserved. Some Project/Finance pages call the
separate `quantbit_construction_management` app or existing external services.
Consolidation does not supply those independent integrations.

## Checks

```bash
./env/bin/python -m unittest procurex.tests.test_ui_build
```

Run from the bench root. The UI lifecycle tests do not use a database.

## License

MIT. See `license.txt`.
