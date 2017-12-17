import json
import requests


class SalesForceTasks():
	def validate_data(self, token, data, instance_url, salesforce_object, username):
		"""
		TODO: Explain how works DATOS ESTABLECIMIENTOS and other forms
		"""
		headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}

		# Since the first does not has the project created still. We validate if object exists by user
		# in other forms we validate by project id DONT FORGOT DO THIS VALIDATION

		url = "{}/services/data/v41.0/query/".format(instance_url)

		# We use here SOQL (SalesForce Object Query Language) due to SalesForce does not
		# let search a value different to the id for custom objects.
		querystring = {"q":"SELECT Escuela__r.CUE__c FROM Historial_escuela__c WHERE username__c='{}'".format(username, salesforce_object)}
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

	def patch(self, token, data, id_object, instance_url, salesforce_object):
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

	def post(self, token, data, instance_url, salesforce_object, username):
		headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}
		url = "{}/services/data/v41.0/sobjects/{}".format(instance_url, salesforce_object)
		# Remove unnecessary objects from the dict. TODO: Do it from JS
		# del data["objeto"]
		if salesforce_object == "Historial_escuela__c":
			# Remove unnecessary objects from the dict
			del data["answers"]["CUE__c"]
			# We add user object
			data["answers"]["username__c"] = username # Only for Datos Establecimientos
		
		payload = json.dumps(data["answers"])
		response = requests.request("POST", url, data=payload, headers=headers)
		return {"success":True}
