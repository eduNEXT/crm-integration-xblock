"""
CRM Integration Xblock.

This module is the actual implemetation of the Xblock related classes
"""

import json

from collections import OrderedDict
from urllib import urlencode

from django.http import JsonResponse, HttpResponse

import requests
import pkg_resources

from xblock.core import XBlock
from xblock.fields import Scope, String
from xblock.fragment import Fragment

from xblockutils.studio_editable import StudioEditableXBlockMixin


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

    url = String(help="The URL for sandbox is https://test.salesforce.com/services/oauth2/token "
                 "and for production https://login.salesforce.com/services/oauth2/token",
                 scope=Scope.content,
                 display_name="URL")

    client_id = String(help="",
                       scope=Scope.content,
                       display_name="Customer Key")

    client_secret = String(help="Your Customer Secret is found in the app you created in SalesForce "
                           "for Oauth. See instructions here: "
                           "https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/"
                           "quickstart_oauth.htm",
                           scope=Scope.content,
                           display_name="Customer Secret")

    username = String(help="Your Salesforce's email",
                      scope=Scope.content,
                      display_name="Email")

    password = String(help="Your SalesForce's password",
                      scope=Scope.content,
                      display_name="Password")

    security_token = String(help="Be aware that your security token will change if you change your password",
                            scope=Scope.content,
                            display_name="Security Token")

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

    def generate_token(self, url, client_id, client_secret, username, password, security_token):  # pylint: disable=too-many-arguments
        """
        This method generate an authentication token for SalesForce
        """
        # pylint: disable=unused-argument

        payload = urlencode(OrderedDict(grant_type="password", client_id=client_id,
                                        client_secret=client_secret,
                                        username=username,
                                        password=password+security_token))

        headers = {'content-type': "application/x-www-form-urlencoded",}
        response = requests.request("POST", url, data=payload, headers=headers)

        return response

    @XBlock.json_handler
    def send_crm_data(self, data, suffix=''):
        """
        This method sends the data to the appropiate backend which in turn sends it to the CRM
        """
        # pylint: disable=unused-argument
        url = self.url
        client_id = self.client_id
        client_secret = self.client_secret
        username = self.username
        password = self.password
        security_token = self.security_token

        # return {"placeholder":"ok"}

        token = self.generate_token(url, client_id, client_secret, username, password, security_token)
        if token.status_code != 200:
            return {"status_code": token.status_code, "message": "Token not generated"}
        else:
            response_salesforce = json.loads(token.text)
            token = response_salesforce["access_token"]
            print token, "TOKENNNNNN"
            instance_url = response_salesforce["instance_url"]
            
            data = json.loads(data);
            salesforce_object = data["objeto"]

            url = "{}/services/data/v41.0/sobjects/{}/".format(instance_url, salesforce_object)
            
            if salesforce_object == "Historial_escuela__c":
                return self.data_school_salesforce(token, instance_url, salesforce_object, data)
            """
            # Aqui se vuelve a comentar
            else:
                # TODO: Here we need get the name of objetc too
                salesforce_data = data
                salesforce_data["Escuela__c"] = "001W000000br5sIIAQ"  # Dummy data
                payload = json.dumps(salesforce_data)
                headers = {
                    "authorization": "Bearer {}".format(token),
                    "content-type": "application/json",
                    }

                response = requests.request("POST", url, data=payload, headers=headers)

                return {"status_code": response.status_code}
            """
    def data_school_salesforce(self, token, instance_url, salesforce_object, data):
        """
        Accoding to Varkey requirements, the Data School object
        needs first verify a CUE id in order to initialize a project.
        This method handle this
        """

        # If the length of the dict data is equal 1, means we need the GET request
        # to query the CUE's school in order to persist the data.
        if len(data["answers"]) == 1:
            cue_id = data["answers"]["cue"]
            url = "{}/services/data/v41.0/sobjects/Account/CUE__c/{}".format(instance_url, cue_id)

            headers = {
                "authorization": "Bearer {}".format(token),
                "content-type": "application/json",
            }

            response = requests.request("GET", url, headers=headers)
            data_response = json.loads(response.text)
            
            data_response = json.loads(response.text)            
            
            if response.status_code == 200:
                school_name = data_response["Name"]
                school_sector = data_response["Sector__c"]
                school_locality = data_response["C_digo_localidad__c"]
                
                d = {"status_code":response.status_code,
                     "school_name":school_name,
                     "school_sector":school_sector,
                     "school_locality":school_locality}                
                return d
            else:
                return {"status_code":400, "message":"CUE not found"}

        # If data length is greather than 2, means we are making submit event in JSinput
        else:
            print salesforce_object
            url = "{}/services/data/v41.0/sobjects/{}".format(instance_url, salesforce_object)
            
            salesforce_data = data
            # salesforce_data["Escuela__c"] = "001W000000br5sIIAQ"  # Dummy data
            payload = json.dumps(salesforce_data)
            # print payload["answers"]
            



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
