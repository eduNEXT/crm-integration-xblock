"""
CRM Integration Xblock.

This module is the actual implemetation of the Xblock related classes
"""

import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment


class CrmIntegration(XBlock):
    """
    This Xblock allow any course unit to send information to an external CRM.
    It acts as a proxy to the external calls, adding the authentication parameters
    and holding the private data we don't want to send to the browsers.
    """

    display_name = String(
        display_name="Display Name",
        scope=Scope.settings,
        default="Crm Integration"
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def student_view(self, context=None):
        """
        The primary view of the CrmIntegration, shown to students
        when viewing courses.
        """
        # pylint: disable=no-member
        context = self.get_general_rendering_context(context)

        in_studio_runtime = hasattr(self.xmodule_runtime, 'is_author_mode')

        if in_studio_runtime:
            return self.author_view(context)

        html = self.resource_string("static/html/crm-integration-student.html")
        frag = Fragment(html.format(**context))
        frag.add_css(self.resource_string("static/css/crm-integration-xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/crm-integration-xblock.js"))
        frag.initialize_js('CrmIntegrationLms')
        return frag

    def author_view(self, context=None):
        """
        Returns author view fragment on Studio.
        Should display an example on how to use this xblock.
        """
        # pylint: disable=unused-argument, no-self-use
        html = self.resource_string("static/html/crm-integration-author.html")
        frag = Fragment(html.format(**context))
        frag.add_css(self.resource_string("static/css/crm-integration-xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/crm-integration-xblock.js"))
        frag.initialize_js('CrmIntegrationStudio')

        return frag

    @XBlock.json_handler
    def send_crm_data(self, data, suffix=''):
        """
        This method sends the data to the appropiate backend which in turn sends it to the CRM
        """
        # pylint: disable=unused-argument
        print "We are hapilly using the send_crm_data"
        print "And the data we receive is:" + str(data)
        return {"placeholder": "ok"}

    def get_general_rendering_context(self, context=None):
        """
        This method creates or adds to the generic context for rendering the html
        """
        if not context:
            context = {}

        context["self"] = self

        # Adapted from lms/urls.py # xblock Handler APIs
        context["lms_handler_url"] = '/courses/{course_key}/xblock/{usage_key}/handler/{handler_name}'.format(
            course_key=self.course_id,  # pylint: disable=no-member
            usage_key=self.url_name,  # pylint: disable=no-member
            handler_name='send_crm_data',  # manually set
        )

        return context

    @staticmethod
    def workbench_scenarios():
        """
        A canned scenario for display in the workbench.
        """
        return [
            ("CrmIntegration",
             """<crm-integration/>
             """),
            ("Multiple CrmIntegration",
             """<vertical_demo>
                <crm-integration/>
                <crm-integration/>
                <crm-integration/>
                </vertical_demo>
             """),
        ]
