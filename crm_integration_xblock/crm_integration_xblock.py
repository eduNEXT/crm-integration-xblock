"""
CRM Integration Xblock.

This module is the actual implemetation of the Xblock related classes
"""

import pkg_resources
import requests

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.middleware.csrf import CsrfViewMiddleware, get_token

from xblock.core import XBlock
from xblock.fields import Scope, String, Integer
from xblock.fragment import Fragment

from xblockutils.studio_editable import StudioEditableXBlockMixin


def load(path):
    """Handy helper for getting resources from our kit."""
    data = pkg_resources.resource_string(__name__, path)
    return data.decode("utf8")

class CrmIntegration(StudioEditableXBlockMixin, XBlock):
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

    url = String(help="The URL for sandbox is "
        "https://test.salesforce.com/services/oauth2/token and for production"
        "https://login.salesforce.com/services/oauth2/token",
        scope=Scope.content,
        display_name="URL",
        required = True
    )

    client_id = String(help="",
        scope=Scope.content,
        display_name="Customer Key"
    )

    client_secret = String(help="Your Customer Secret is found in the app you created in SalesForce"
        "for Oauth. See instructions here: "
        "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/quickstart_oauth.htm",
        scope=Scope.content,
        display_name="Customer Secret"
    )

    username = String(help="Your Salesforce's email",
        scope=Scope.content,
        display_name="Email"
    )

    password = String(help="",
        scope=Scope.content,
        display_name="Password"
    )

    security_token = String(help="Be aware that your security token will change if you change your password",
        scope=Scope.content,
        display_name="Security Token"
    )

    editable_fields = ('url',
                       'client_id',
                       'client_secret',
                       'username',
                       'password',
                       'security_token',)

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
    def generate_token(self, data, suffix=''):
        """
        This method generate an authentication token for SalesForce
        """
        # pylint: disable=unused-argument
        url = self.url
        client_id = self.client_id
        client_secret = self.client_secret
        username = self.username
        password = self.password
        security_token = self.security_token
        
        payload = "grant_type=password&client_id={}&client_secret={}&username={}&password={}{}".format(
            client_id,
            client_secret,
            username,
            password,
            security_token
        )
          
        headers = {'content-type': "application/x-www-form-urlencoded",}
        response = requests.request("POST", url, data=payload, headers=headers)

        if response.status_code != 200:
            return {"status": 0, "message": "Status not generated"}
        else:
            return {"status": 1}

    @XBlock.json_handler
    def send_crm_data(self, data, suffix=''):
        """
        This method sends the data to the appropiate backend which in turn sends it to the CRM
        """
        # pylint: disable=unused-argument

        print "We are hapilly using the send_crm_data"
        print "And the data we receive is:" + str(data)
        return {"placeholder": "ok", "hola": "dsde js input"}

    def get_general_rendering_context(self, context=None):
        # This method creates or adds to the generic context for rendering the html
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
