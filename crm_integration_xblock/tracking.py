"""
Wrapper module fo the tracker.emit functions
"""
import logging
from django.conf import settings

try:
    from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
except ImportError:
    configuration_helpers = None

LOG = logging.getLogger(__name__)

try:
    from eventtracking import tracker  # pylint: disable=import-error,wrong-import-position
except ImportError:
    LOG.warning(u"Could not load the eventtracking module")


def emit(event, priority=20, data=None):
    """Wrapper for the openedx tracker function"""
    level = 30
    if configuration_helpers:
        level = configuration_helpers.get_value("CRM_INTEGRATION_TRACKING_LEVEL", level)  # pylint: disable=no-member
    if priority > getattr(settings, "CRM_INTEGRATION_TRACKING_LEVEL", level):
        tracker.emit(
            event,
            data
        )
