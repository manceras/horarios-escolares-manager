"""The desktop shell: paths, backups, the local server, updates and the window.

Everything in here knows about the user's machine. The domain does not, and must
stay that way: ``app/services``, ``app/repositories``, ``app/models`` and
``app/solver`` may never import from this package, or the business rules become
untestable without a Windows profile to run them in.

``app/api`` is the exception. Checking for a new version is a machine-level
feature with no domain behind it, and the window can only reach it over the same
local HTTP API as everything else -- so ``app/api/v1/updates.py`` imports from
here on purpose.
"""
