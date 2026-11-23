# Source provenance

The React source was incorporated from
https://github.com/QuantbitERP/ProcureX at commit
`cf2765abe6ea13daf7f9dbf7d1194eb9dd966ba4`.

The original source remains intact. The Frappe-specific Vite configuration
replaces the standalone deployment configuration and adapts navigation at build
time to `/procurex`. Frontend source now belongs to this single repository;
installation never clones another repository.

The backend originates from https://github.com/QuantbitERP/ProcureX-Backend
at commit `85faec21745299179019c74a290a671388d4e13b`. Existing API names and
DocTypes are retained.
