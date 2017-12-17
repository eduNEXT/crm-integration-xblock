"""
SalesForce Varkey Integration Xblock.

This only works for Varkey purpose
"""

import json
import requests

from .salesforce_tasks import SalesForceTasks

class SalesForceVarkey():

	def __init__(self, method):
		self.method = method

	def validate_cue(self, token, instance_url, salesforce_object, data, username):
		headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}

		if self.method == "GET":
			cue_id = data["answers"]["CUE__c"]
			url = "{}/services/data/v41.0/sobjects/Account/CUE__c/{}".format(instance_url, cue_id)

			response = requests.request("GET", url, headers=headers)
			data_response = json.loads(response.text)
			if response.status_code == 200:
				school_id = data_response["Id"]
				school_name = data_response["Name"]
				school_sector = data_response["Sector__c"]
				school_locality = data_response["C_digo_localidad__c"]
				return {"status_code":response.status_code, "school_id": school_id, "school_name":school_name, "school_sector":school_sector, "school_locality":school_locality}

			else:
				return {"status_code":400, "message":"CUE not found"}

		else:
			# Call method to check if create or update object in SalesForce
			return SalesForceTasks().validate_data(token, data, instance_url, salesforce_object, username)

	def validate_cue_by_user(self, token, instance_url, salesforce_object, data, username):
		headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}
		
		# Note method is not the type of method for send to SalesForce (This is handle in validate_data)
		# This method check the event in JSinput. Get for DOM ready and POST for submit button.
		
		if self.method == "GET":
			url = "{}/services/data/v41.0/query/".format(instance_url)
			# Get school data using SOQL in order to be displayed in the required forms.
			querystring = {"q":"SELECT Escuela__r.Name, Escuela__r.CUE__c, Escuela__r.Id FROM Historial_escuela__c WHERE username__c='{}'".format(username)}
			response = requests.request("GET", url, headers=headers, params=querystring)
			salesforce_response = json.loads(response.text)
			if response.status_code == 200:
				school_id = salesforce_response["records"][0]["Escuela__r"]["Id"]
				school_name = salesforce_response["records"][0]["Escuela__r"]["Name"]
				school_cue = salesforce_response["records"][0]["Escuela__r"]["CUE__c"]
				return {"status_code":response.status_code, "school_name":school_name, "school_cue":school_cue, "school_id":school_id}

			else:
				return {"status_code":400, "message":"USER not found", "success": False}

		if self.method == "POST":
			# Call method to check if create or update object in SalesForce
			return SalesForceTasks().validate_data(token, data, instance_url, salesforce_object, username)
