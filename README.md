# ProcureX

One Frappe v16 app containing the procurement backend and the React UI.
The repository is named **ProcurexBundle**, but its Frappe app and Python package
are both named **procurex**. The corrected `main` branch contains both parts.
Release `0.0.2` also includes a small `procurex_bundle` import bridge for sites
that already list the obsolete wrapper. New sites install only `procurex`;
the bridge never fetches or installs another app.
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
  procurex_bundle/          # legacy imports for retiring old site entries
```

## Install on a Bench

Use a Frappe v16 bench with ERPNext installed, Python 3.14+, and its supported
Node 24+ / npm / Yarn toolchain. Node is used to compile assets, not to serve
ProcureX in production. No developer-specific Node path is required.

```bash
bench get-app https://github.com/QuantbitERP/ProcurexBundle.git --branch main
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

Publish these changes to `QuantbitERP/ProcurexBundle`, branch `main`, then use
that source for the **procurex** app on a compatible Frappe v16 custom-app bench
with ERPNext. Deploy the bench and install `procurex` on the site. Cloud must
recognize the source's app name as `procurex`, as declared in `pyproject.toml`.
Do not deploy the previous `procurex_bundle` wrapper or the standalone React
repository as the application.

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

### Recovering `ModuleNotFoundError: No module named 'procurex'`

This error means the server expects the `procurex` Python package but cannot
import it. It is different from the Whoosh `SyntaxWarning` messages.

The old wrapper ran `bench get-app` during site installation. Downloading an
app inside a running Cloud bench does not put it into Cloud's next deployment
image. This repository now ships `procurex/__init__.py`, all backend APIs and
DocTypes, and the frontend in the same source. It never downloads another app
or edits `sites/apps.txt` during installation.

If `pip show procurex` reports no installed package and
`apps/procurex_bundle/procurex` does not exist, the running bench still has the
old wrapper source. Uninstalling or clearing caches cannot restore that missing
code. Deploy a new Cloud build containing the corrected source first.

The current distribution includes both `procurex.hooks` and the legacy
`procurex_bundle.hooks`, so Frappe can load existing installed-app entries during
dependency checks. The legacy hooks have no downloader or UI renderer. They
reject new wrapper installs and allow removal only when it owns no DocTypes.
Backend APIs, DocTypes and data continue to belong to `procurex`.

For an affected Cloud site, back it up, publish the corrected code, ensure the
bench's Apps configuration includes the source as **procurex**, and use the
Cloud dashboard to build and deploy that source. If the source is still shown
as `procurex_bundle`, refresh/re-add its App Source registration with the new
app name before deploying. Preserve any existing `procurex` installation and
data; do not uninstall it to repair this import error. Only retire the obsolete
wrapper after the backend is available and the site is healthy again.

See Frappe Cloud's [deployment debugging guidance](https://docs.frappe.io/cloud/benches/debugging)
on why runtime app downloads do not persist across bench updates. For an urgent
recovery before publishing this branch, the consolidated backend source is
also available at `QuantbitERP/ProcureX-Backend`, branch `version-16`; register
that source as `procurex` through the Cloud dashboard and deploy it. Use one
source for the `procurex` app, not both repositories as duplicate apps.

## Existing installations using the wrapper

The backend app name, API paths, DocTypes and existing procurement records remain
`procurex`.

On **Frappe Cloud**, publish release `0.0.2` and use the dashboard to deploy it
before running the following checks. Do not run `bench get-app` or an asset
build in the running Cloud container as a substitute for deploying its image.
Verify that both imports succeed in the new bench:

```bash
cd ~/frappe-bench
./env/bin/python -c "import procurex, procurex.hooks, procurex_bundle.hooks; print(procurex.__version__)"
```

The version must be `0.0.2` (or a later compatible release). Then back up the
site and preview uninstalling only the wrapper:

```bash
bench --site dev-balaji-castings.frappe.cloud backup --with-files
bench --site dev-balaji-castings.frappe.cloud uninstall-app procurex_bundle --dry-run
```

Only if the preview lists the empty `Procurex Bundle` module and no DocTypes,
remove **only** the obsolete wrapper:

```bash
bench --site dev-balaji-castings.frappe.cloud uninstall-app procurex_bundle --yes
bench --site dev-balaji-castings.frappe.cloud clear-cache
bench --site dev-balaji-castings.frappe.cloud list-apps
```

The final list should retain `procurex` and omit `procurex_bundle`. Do not
uninstall `procurex` or manually delete installed-app database entries to work
around an import failure.

For a **self-hosted bench**, build the consolidated app first, back up the site,
then preview removing the empty wrapper:

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

Once no site uses the wrapper, a separate old wrapper checkout can be archived.
Keep the consolidated repository, even if its checkout is named ProcurexBundle.
Do not uninstall `procurex`; it owns the procurement data.

## Existing integrations

The UI and business APIs are preserved. Some Project/Finance pages call the
separate `quantbit_construction_management` app or existing external services.
Consolidation does not supply those independent integrations.

## Checks

```bash
./env/bin/python -m unittest procurex.tests.test_ui_build procurex.tests.test_legacy_bridge
```

Run from the bench root. The UI lifecycle tests do not use a database.

## License

MIT. See `license.txt`.
