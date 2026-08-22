"""Monolith entry points.

Puts the services root on `sys.path` so the service packages are importable
under the *same* names they use inside their containers — `shared.config`,
`graph.app.indexer`, and so on.

One spelling matters here, not just tidiness: a module reached as both
`shared.logger` and `services.shared.logger` becomes two distinct module
objects with separate state. `logger.py` configures a Loguru sink at import,
so a dual identity silently installs two stdout sinks and the CLI's --json
mode can only ever move one of them to stderr.
"""

import os
import sys

_SERVICES_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "services")
if _SERVICES_ROOT not in sys.path:
    sys.path.insert(0, _SERVICES_ROOT)
