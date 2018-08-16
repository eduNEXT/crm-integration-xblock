"""
"""
import logging

log = logging.getLogger(__name__)

try:
    from openedx.conf import settings
except Exception as e:
    from django.conf import settings

try:
    from eventtracking import tracker
except Exception as e:
    log.warning(u"Could not load the eventtracking module")


def emit(event, priority=20, data=None):
    """Wrapper for the openedx tracker function"""

    if priority > getattr(settings, "CRM_INTEGRATION_TRACKING_LEVEL", 20):
        tracker.emit(
            event,
            data
        )
