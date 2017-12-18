"""
This class only will work for Varkey requirements.
"""

import json
import requests


class SalesForceTasks():
    """
    TODO: Make init method to get all variables from SalesForceVarkey
    """

    def validate_data(self, token, data, instance_url, salesforce_object, username):  # pylint: disable=too-many-arguments
        """
        In SalesForce's Varkey are handle 5 objects:
            1. Accounts: Where School data are storaged, this data comes by default.
            2. Historial Escuela: Are the initial data.
            3. Proyecto: Initial Proyecto data.
            4. Objetivos: Objectives of the project.
            5. Acciones: Actions of each objective.

           It's neccesary validate which SalesForce object we are receiving since
           of this depends if we create or update the record.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}

        # Since the first form does not has the project created still. We validate if
        # object exists by user in other forms we validate by project id.
        # TODO: DONT FORGOT DO THIS VALIDATION.
        url = "{}/services/data/v41.0/query/".format(instance_url)

        # We use here SOQL (SalesForce Object Query Language) due to SalesForce does not
        # let search a value different to the id for custom objects.
        querystring = {"q":"SELECT Escuela__r.CUE__c FROM Historial_escuela__c WHERE username__c='{}'".format(username, salesforce_object)}  # pylint: disable=line-too-long
        response = requests.request("GET", url, headers=headers, params=querystring)
        salesforce_response = json.loads(response.text)
        records = salesforce_response["records"]

        if records == []:
            cue = None
        else:
            cue = salesforce_response["records"][0]["Escuela__r"]["CUE__c"]

        if salesforce_object == "Proyectos__c":
            querystring = {"q":"SELECT Id FROM {} WHERE CUE__c='{}'".format(salesforce_object, cue)}
            response = requests.request("GET", url, headers=headers, params=querystring)
            salesforce_response = json.loads(response.text)

        total_objects = salesforce_response["totalSize"]

        # If there are 0 objects means there is not a project yet. Proceed to create it.
        if total_objects == 0:
            return self.post(token, data, instance_url, salesforce_object, username)

        if total_objects == 1:  # Exists the object
            # SalesForce does not return explicity the id of the object queried. It returns a url
            # with the ID, example: /services/data/v41.0/sobjects/Historial_escuela__c/a16W0000000r3DAIAY
            # We split this URL and get this ID, due to make another request to the SF API it would not be
            # the most efficient.
            attribute_url = salesforce_response["records"][0]["attributes"]["url"]
            object_to_patch = attribute_url.split("/")[6]
            return self.patch(token, data, object_to_patch, instance_url, salesforce_object)

    def patch(self, token, data, id_object, instance_url, salesforce_object):  # pylint: disable=too-many-arguments
        """
        Update the object.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}
        where_to_patch = id_object
        url = "{}/services/data/v41.0/sobjects/{}/{}".format(instance_url, salesforce_object, where_to_patch)
        payload = json.dumps(data["answers"])

        if "Escuela__c" in payload:
            # Delete Escuela key due to security settings of SalesForce that
            # does not let send primary keys to update.
            del data["answers"]["Escuela__c"]

        if salesforce_object == "Historial_escuela__c":
            # Remove unnecessary objects from the dict
            del data["answers"]["CUE__c"]

        payload = json.dumps(data["answers"])  # New payload without unneccesary fields
        response = requests.request("PATCH", url, data=payload, headers=headers)

        # PATCH does not return anything in body
        # https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/dome_update_fields.htm
        # we only can get the status_code
        if response.status_code == 400 or response.status_code == 404:
            return {"success":False}
        if response.status_code == 204:
            return {"success":True}

    def post(self, token, data, instance_url, salesforce_object, username):  # pylint: disable=too-many-arguments
        """
        Create a new object.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}
        url = "{}/services/data/v41.0/sobjects/{}".format(instance_url, salesforce_object)
        # Remove unnecessary objects from the dict.
        if salesforce_object == "Historial_escuela__c":
            # Remove unnecessary objects from the dict
            del data["answers"]["CUE__c"]
            # We add user object
            data["answers"]["username__c"] = username # Only for Datos Establecimientos

        payload = json.dumps(data["answers"])
        requests.request("POST", url, data=payload, headers=headers)
        return {"success":True}

    def objectives(self, token, data, instance_url, salesforce_object):
        """
        Since we are using bulk API because we load more than one objective in one request
        there is no need to validate if post or patch due to SalesForce do that in background.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}
        url = "{}/services/data/v41.0/composite/tree/{}".format(instance_url, salesforce_object)
        payload = json.dumps(data["answers"])
        requests.request("POST", url, data=payload, headers=headers)
        return {"success":True}



