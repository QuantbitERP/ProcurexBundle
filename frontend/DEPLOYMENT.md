# Deploying the ProcureX UI

This frontend is part of the `procurex` Frappe app. Follow the repository's
[installation and Frappe Cloud guide](../README.md).

`bench build --app procurex` compiles the static React UI. Frappe serves it at
`/procurex`, with assets under `/assets/procurex/ui/`. All local `/api` calls use
the same Frappe site and session. There is no production frontend process.

Change React pages in `frontend/src/` and backend APIs in `procurex/api.py`,
then rebuild the app using the bench's supported Node toolchain.
