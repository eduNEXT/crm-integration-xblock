"""
This class only will work for Varkey requirements.
"""

import json
import requests


VERSION = "v41.0"

class SalesForce(object):
    """
    Class for handles main requests methods of SalesForce.
    """

    def __init__(self, token, instance_url):
        self.headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}
        self.base_url = "{}/services/data/{}/sobjects/".format(instance_url, VERSION)
        self.query_url = "{}/services/data/{}/query/".format(instance_url, VERSION)
        self.bulk_url = "{}/services/data/{}/composite/tree/".format(instance_url, VERSION)

    def validate(self, data):
        """
        Validate method mandatory for Subclasses.
        """
        raise NotImplementedError('Validate method not implemented.')

    def query(self, query):
        """
        Executes SalesForce Object Query Language.
        """
        url = self.query_url
        params = {"q":query}
        response = requests.request("GET", url, headers=self.headers, params=params)

        return response

    def get(self, salesforce_object, data, id_object=None):
        """
        Make GET request to SalesForce. If not id_object is passed
        returns all recorsds of the object.
        """
        if id_object:
            url = self.base_url+"{}/{}".format(salesforce_object, id_object)
        else:
            url = self.base_url+"{}".format(salesforce_object)
        response = requests.request("GET", url, data=json.dumps(data), headers=self.headers)

        return response

    def create(self, salesforce_object, data):
        """
        Make POST request.
        """
        url = self.base_url+"{}".format(salesforce_object)
        sf_response = requests.request("POST", url, data=json.dumps(data), headers=self.headers)

        if sf_response.status_code != 200:
            return {"success": False, "message": sf_response.text}
        else:
            return {"success": True, "message": sf_response.text}

    def update(self, salesforce_object, data, id_object):
        """
        Make PATCH request to SalesForce, id_object it's mandatory.
        """
        url = self.base_url+"{}/{}".format(salesforce_object, id_object)
        sf_response = requests.request("PATCH", url, data=json.dumps(data), headers=self.headers)

        if sf_response.status_code != 204:
            return {"success": False}
        else:
            return {"success": True}

    def delete(self, salesforce_object, id_object):
        """
        Delete objects one by one
        """
        url = "{base}{object}/{id}".format(base=self.base_url,
                                           object=salesforce_object,
                                           id=id_object)

        response = requests.request("DELETE", url, headers=self.headers)
        return response

    def bulk(self, salesforce_object, data):
        """
        Create or update multiple records in one request.
        """
        url = self.bulk_url+"{}".format(salesforce_object)
        response = requests.request("POST", url, data=json.dumps(data), headers=self.headers)

        return response

