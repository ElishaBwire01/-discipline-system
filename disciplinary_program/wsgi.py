# disciplinary_program/wsgi.py

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "disciplinary_program.settings",
)

application = get_wsgi_application()

# Vercel requires this
app = application


# ------------------------------------------------------------
# ONE-TIME PRODUCTION ADMIN BOOTSTRAP
# ------------------------------------------------------------
#
# This runs ONLY when:
#
#     BOOTSTRAP_ADMIN=true
#
# The username/password are read from Vercel environment
# variables and are NOT stored in GitHub.
#
# After the admin has been created successfully:
#
#     BOOTSTRAP_ADMIN=false
#
# or remove the variable entirely from Vercel.
# ------------------------------------------------------------

if os.environ.get("BOOTSTRAP_ADMIN", "").lower() == "true":
    try:
        from disciplinary_program.production_admin_bootstrap import (
            bootstrap_production_admin,
        )

        bootstrap_production_admin()

    except Exception:
        import logging

        logging.getLogger(__name__).exception(
            "Production admin bootstrap could not be executed."
        )
