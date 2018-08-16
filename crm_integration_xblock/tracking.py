"""
"""
import logging
from django.conf import settings

log = logging.getLogger(__name__)

try:
    from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers
except Exception as e:
    configuration_helpers = False

try:
    from eventtracking import tracker
except Exception as e:
    log.warning(u"Could not load the eventtracking module")


def emit(event, priority=20, data=None):
    """Wrapper for the openedx tracker function"""
    level = 30
    if configuration_helpers:
        level = configuration_helpers.get_value("CRM_INTEGRATION_TRACKING_LEVEL", level)
    if priority > getattr(settings, "CRM_INTEGRATION_TRACKING_LEVEL", level):
        tracker.emit(
            event,
            data
        )
