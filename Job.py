import re
import datetime

class Job():
	""" Represents a job on the WCFMC website """
	def __init__(self, wcfmc_id, date, service, vehicle_registration, make_model, registration_year, city, postcode, contact_first_name, comments):
		if not isinstance(wcfmc_id, int):
			raise TypeError("wcfmc_id should be int")
		if not isinstance(date, datetime.date):
			raise TypeError("Date should be datetime.date")

		self.wcfmc_id = wcfmc_id
		self.date = date
		self.service = service
		self.vehicle_registration = re.sub(r'[\W_]+', '', vehicle_registration).upper() # keep only letters and numbers
		self.make_model = make_model
		self.registration_year = re.sub("[^0-9]", '', registration_year) # keep only numbers
		self.city = city
		self.postcode = re.sub(r'[\W_]+', '', postcode).upper() # keep only letters and numbers
		self.contact_first_name = contact_first_name
		self.comments = comments

	def __str__(self):
		return str(self.wcfmc_id) + ': ' + self.service + ' on ' + self.vehicle_registration + ' for ' + self.contact_first_name + \
				' in ' + self.city + ', ' + self.postcode
