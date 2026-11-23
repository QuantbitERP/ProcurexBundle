"""Legacy import bridge for sites retiring the old ProcureX wrapper.

The procurex distribution ships this bridge; it is not installed as another
app on new sites and does not fetch, install or serve any application.
"""

from procurex import __version__
