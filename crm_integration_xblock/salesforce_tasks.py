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
		querystring = {"q":"SELECT username__c FROM Historial_escuela__c WHERE username__c='{}'".format(username)}
		response = requests.request("GET", url, headers=headers, params=querystring)
		salesforce_response = json.loads(response.text)

		# SalesForce gives a total size object response which tell us how many records there are
		# in the object. If the total size is equals one, means there is already a data school created
		# by the user, and we procced to patch request, if not, create it.
		total_objects = salesforce_response["totalSize"]
		print total_objects, "OBJETOS TOTALES"
		if total_objects == 1:
			# SalesForce does not return explicity the id of the object queried. It returns a url
			# with the ID, example: /services/data/v41.0/sobjects/Historial_escuela__c/a16W0000000r3DAIAY
			# We split this URL and get the ID, due to make another request to the SF API it would not be
			# the most efficient.
			attribute_url = salesforce_response["records"][0]["attributes"]["url"]
			id_object = attribute_url.split("/")[6]
			print data, "DATAAA"
			# Remove Escuela__c field due to is a not editable field. SalesForce
			# returns error if find an not editable object in the data for patch methods.
			del data["answers"]["Escuela__c"]
			del data["answers"]["CUE__c"]
			return self.patch(token, data, id_object, instance_url, salesforce_object)

		if total_objects == 0:
			return self.post(token, data, instance_url, salesforce_object, username)


	def patch(self, token, data, id_object, instance_url, salesforce_object):
		headers = {"authorization": "Bearer {}".format(token), "content-type": "application/json",}
		where_to_patch = id_object
		url = "{}/services/data/v41.0/sobjects/{}/{}".format(instance_url, salesforce_object, where_to_patch)
		payload = json.dumps(data["answers"])
		response = requests.request("PATCH", url, data=payload, headers=headers)
		print response.status_code, "RESPUESTA DE PATCH"

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
		del data["objeto"]
		del data["answers"]["CUE__c"]
		# We add user object
		data["answers"]["username__c"] = username

		payload = json.dumps(data["answers"])
		response = requests.request("POST", url, data=payload, headers=headers)
		return {"success":True}
