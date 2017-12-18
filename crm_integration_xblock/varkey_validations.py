"""
SalesForce Varkey Integration Xblock.

This only works for Varkey purpose
"""

import json
import requests

from .salesforce_tasks import SalesForceTasks

class SalesForceVarkey():
    """
    Each form in Varkey needs a context, to give to the user a guide
    of what the user has done in previous forms, for the first two form
    show info about the school, for the rest of forms show info about the project.

    1. Datos Establecimientos: This is the first form where there is no data still,
    it has to validate the CUE.

    2. Matriz TIC and FODA: Needs to validate the CUE but by user, since in the first
    form we associate a user.

    3. Forms after create project: Contexts for these forms are the info about the project
    that's why we have to validate wich type of form are receiving.
    """

    def __init__(self, method):
        """
        Each time a form is displayed we show an info automatically. For show
        this info we set the method "receive" from the jsinput, if the user
        click submit we set the method "send" in the jsinput.
        """
        self.method = method

    def validate_cue(self, token, instance_url, salesforce_object, data, username):  # pylint: disable=too-many-arguments
        """
        Method that look for CUE id in Account object.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}

        if self.method == "receive":
            cue_id = data["answers"]["CUE__c"]
            url = "{}/services/data/v41.0/sobjects/Account/CUE__c/{}".format(instance_url, cue_id)

            response = requests.request("GET", url, headers=headers)
            data_response = json.loads(response.text)
            if response.status_code == 200:
                school_id = data_response["Id"]
                school_name = data_response["Name"]
                school_sector = data_response["Sector__c"]
                school_locality = data_response["C_digo_localidad__c"]

                return {"status_code":response.status_code,
                        "school_id": school_id,
                        "school_name":school_name,
                        "school_sector":school_sector,
                        "school_locality":school_locality}

            else:
                return {"status_code":400, "message":"CUE not found"}

        else:  # Means SEND method
            # Call method to check if create or update object in SalesForce
            return SalesForceTasks().validate_data(token, data, instance_url, salesforce_object, username)

    def validate_cue_by_user(self, token, instance_url, salesforce_object, data, username):  # pylint: disable=too-many-arguments
        """
        Method that look for CUE id in Historial Escula by user.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}

        if self.method == "receive":
            url = "{}/services/data/v41.0/query/".format(instance_url)
            # Get school data using SOQL in order to be displayed in the required forms.
            querystring = {"q":"SELECT Escuela__r.Name, Escuela__r.CUE__c, Escuela__r.Id FROM Historial_escuela__c WHERE username__c='{}'"  # pylint: disable=line-too-long
                               .format(username)}
            response = requests.request("GET", url, headers=headers, params=querystring)
            salesforce_response = json.loads(response.text)

            if response.status_code == 200:
                school_id = salesforce_response["records"][0]["Escuela__r"]["Id"]
                school_name = salesforce_response["records"][0]["Escuela__r"]["Name"]
                school_cue = salesforce_response["records"][0]["Escuela__r"]["CUE__c"]

                return {"status_code":response.status_code,
                        "school_name":school_name,
                        "school_cue":school_cue,
                        "school_id":school_id}

            else:
                return {"status_code":400, "message":"USER not found", "success": False}

        if self.method == "POST":
            # Call method to check if create or update object in SalesForce
            return SalesForceTasks().validate_data(token, data, instance_url, salesforce_object, username)

    def validate_by_project(self, token, instance_url, salesforce_object, data, username):  # pylint: disable=too-many-arguments
        """
        Method that look a project by user and CUE.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}

        if self.method == "receive":
            url = "{}/services/data/v41.0/query/".format(instance_url)

            # We need to do two queries due to in Proyectos object there is not a relationship with
            # Historial_Escuela, which is the object where SalesForce handled username,
            # this would be solved adding a foreign key in Proyectos with Historial_Escuela in order
            # to save one query here.
            query_one = {"q":"SELECT Escuela__r.CUE__c FROM Historial_escuela__c WHERE username__c='{}'".format(username)}  # pylint: disable=line-too-long
            response = requests.request("GET", url, headers=headers, params=query_one)
            salesforce_response = json.loads(response.text)
            cue = salesforce_response["records"][0]["Escuela__r"]["CUE__c"]

            query_two = {"q":"SELECT Id, project_title__c FROM Proyectos__c WHERE CUE__c='{}'".format(cue)}
            response = requests.request("GET", url, headers=headers, params=query_two)
            salesforce_response = json.loads(response.text)

            if response.status_code == 200:
                project_title = salesforce_response["records"][0]["project_title__c"]
                project_id = salesforce_response["records"][0]["Id"]

                return {"status_code":response.status_code,
                        "project_title":project_title,
                        "project_id": project_id}

            else:
                return {"status_code":400, "message":"USER not found", "success": False}

        if self.method == "send":
            # Call method to check if create or update object in SalesForce
            if salesforce_object == "Objetivo__c":
                return SalesForceTasks().objectives(token, data, instance_url, salesforce_object)
            else:
                return SalesForceTasks().validate_data(token, data, instance_url, salesforce_object, username)

    def summary(self, token, instance_url, username):
        """
        Method that send only a get to the whole Proyecto object.
        """
        headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}

        url = "{}/services/data/v41.0/query".format(instance_url)

        query_one = {"q":"SELECT Escuela__r.CUE__c FROM Historial_escuela__c WHERE username__c='{}'".format(username)}
        response = requests.request("GET", url, headers=headers, params=query_one)
        salesforce_response = json.loads(response.text)
        cue = salesforce_response["records"][0]["Escuela__r"]["CUE__c"]

        query_two = {"q":"SELECT project_title__c, tic_dimension_1__c FROM Proyectos__c WHERE CUE__c='{}'".format(cue)}
        response = requests.request("GET", url, headers=headers, params=query_two)
        salesforce_response = json.loads(response.text)

        if response.status_code == 200:
            project_title = salesforce_response["records"][0]["project_title__c"]
            tic_dimension_1__c = salesforce_response["records"][0]["tic_dimension_1__c"]

            return {"status_code":response.status_code, "project_title":project_title,
                    "tic_dimension_1": tic_dimension_1__c}
