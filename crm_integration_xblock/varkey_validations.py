"""
SalesForce Varkey Integration Xblock.

This only works for Varkey purpose
"""

import json

from .salesforce_tasks import SalesForce


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

    def __init__(self, token, instance_url, username, method, initial):  # pylint: disable=too-many-arguments
        """
        Each time a form is displayed we show an info automatically. For show
        this info we set the method "receive" from the jsinput, if the user
        click submit we set the method "send" in the jsinput.
        """
        self.token = token
        self.instance_url = instance_url
        self.username = username
        self.method = method
        self.initial = initial
        self.salesforce = SalesForce(token, instance_url)

    def validate(self, data):
        """
        Mandatory method. For Varkey case handles the way
        wich method to execute in order to validate the forms.
        """
        salesforce_object = self.initial["object_sf"]

        if salesforce_object == "Historial_escuela__c":
            return self._validate_cue(data)

        if salesforce_object == "Proyectos__c":
            return self._validate_cue_by_user(data)

        if salesforce_object == "Objetivo__c":
            return self._validate_by_project(data)

        if salesforce_object == "Resumen":
            return self._summary()

    def _validate_cue(self, data):
        """
        Method that look for CUE id in Account object.
        """
        decide = self._send_or_receive(self.method)

        if decide:
            cue_id = data["answers"]["CUE__c"]
            response = self.salesforce.get("Account/CUE__c", data, id_object=cue_id)
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

        else:
            return self._update_or_create(data)

    def _validate_cue_by_user(self, data):
        """
        Method that look for CUE id in Historial Escula by user.
        """
        decide = self._send_or_receive(self.method)

        if decide:
            response = self.salesforce.query("SELECT Escuela__r.Name, Escuela__r.CUE__c, Escuela__r.Id FROM Historial_escuela__c WHERE username__c='{}'".format(self.username))  # pylint: disable=line-too-long
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
        else:
            return self._update_or_create(data)

    def _validate_by_project(self, data):
        """
        Method that look a project by user and CUE.
        """
        decide = self._send_or_receive(self.method)

        if decide:
            response = self.salesforce.query("SELECT Id, project_title__c FROM Proyectos__c WHERE project_id__c='{}'".format(self.username))  # pylint: disable=line-too-long
            salesforce_response = json.loads(response.text)

            if response.status_code == 200:
                project_title = salesforce_response["records"][0]["project_title__c"]
                project_id = salesforce_response["records"][0]["Id"]

                return {"status_code":response.status_code,
                        "project_title":project_title,
                        "project_id": project_id}

            else:
                return {"status_code":400, "message":"USER not found", "success": False}

        else:
            # Objetivo__c object does not need to validate if update or create
            # since SalesForce's bulk endpoint handles this in the background.
            salesforce_object = self.initial["object_sf"]

            if salesforce_object == "Objetivo__c":
                return self.salesforce.bulk(salesforce_object, data)
            else:
                return self._update_or_create(data)

    def _summary(self):
        """
        Method that send only a GET request to the whole Proyecto object.
        """
        response = self.salesforce.query("SELECT Id, project_title__c FROM Proyectos__c WHERE project_id__c='{}'".format(self.username))  # pylint: disable=line-too-long
        salesforce_response = json.loads(response.text)

        if response.status_code == 200:
            project_title = salesforce_response["records"][0]["project_title__c"]

            return {"status_code":response.status_code, "project_title":project_title,}

    def _send_or_receive(self, method):
        """
        This simple method handles if Varkey are sending or getting info.
        Could be present in each validations inside the methods of SalesForceVarkey
        but in future "send" or "receive" method could become more complex.
        """
        if method == "receive":
            return True
        if method == "send":
            return False

    def _update_or_create(self, data):
        """
        Check if update or create the record in any
        of the objects in Varkey.
        """
        salesforce_object = self.initial["object_sf"]

        # SalesForce returns error if in the payload
        # exists fields that does not belong to the object.
        data["answers"].pop("CUE__c", None)

        response = self.salesforce.query("SELECT Escuela__r.CUE__c FROM Historial_escuela__c WHERE project_id__c='{}'".format(self.username))  # pylint: disable=line-too-long
        salesforce_response = json.loads(response.text)

        # Since in Varkey there are two objects to create or update
        # we need to check which of them we are consulting.
        if salesforce_object == "Proyectos__c":
            response = self.salesforce.query("SELECT Id FROM {} WHERE project_id__c='{}'".format(salesforce_object, self.username))  # pylint: disable=line-too-long
            salesforce_response = json.loads(response.text)

        total_objects = salesforce_response["totalSize"]

        # If there are 0 objects means there is not a project yet. Proceed to create it.
        if total_objects == 0:
            username = self.username
            data["answers"]["project_id__c"] = username
            response = self.salesforce.create(salesforce_object, data["answers"])
            return response

        if total_objects == 1:  # Exists the object
            # Remove these values from the dict due to SalesForce does not
            # let patch protected fields.
            data["answers"].pop("Escuela__c", None)
            attribute_url = salesforce_response["records"][0]["attributes"]["url"]
            where_to_patch = attribute_url.split("/")[6]
            response = self.salesforce.update(salesforce_object, data["answers"], where_to_patch)
            return response
