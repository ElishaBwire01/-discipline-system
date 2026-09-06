import os
import logging

logger = logging.getLogger(__name__)


def bootstrap_production_admin():
    """
    One-time production admin bootstrap.

    Enabled only when BOOTSTRAP_ADMIN=true.
    Credentials come from environment variables, never source code.
    """

    enabled = os.environ.get("BOOTSTRAP_ADMIN", "").lower() == "true"

    if not enabled:
        return

    username = os.environ.get("BOOTSTRAP_ADMIN_USERNAME", "bwire")
    password = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")

    if not password:
        logger.error(
            "BOOTSTRAP_ADMIN=true but BOOTSTRAP_ADMIN_PASSWORD is missing."
        )
        return

    try:
        from django.contrib.auth import get_user_model

        User = get_user_model()

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )

        # Promote the requested account without deleting
        # or modifying any other administrator.
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True

        # Set the requested password.
        user.set_password(password)

        # Give the account an email only if one is supplied.
        email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL")
        if email:
            user.email = email

        user.save()

        if created:
            logger.warning(
                "PRODUCTION ADMIN BOOTSTRAP: user '%s' CREATED.",
                username,
            )
        else:
            logger.warning(
                "PRODUCTION ADMIN BOOTSTRAP: user '%s' PROMOTED/UPDATED.",
                username,
            )

        logger.warning(
            "PRODUCTION ADMIN BOOTSTRAP COMPLETE. "
            "Disable BOOTSTRAP_ADMIN immediately after login."
        )

    except Exception:
        logger.exception("PRODUCTION ADMIN BOOTSTRAP FAILED.")
