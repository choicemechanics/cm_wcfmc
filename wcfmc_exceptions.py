class LoginError(Exception):
	""" Used when WCFMC login fails. Check message for more information """
	pass

class LeadStageError(Exception):
	""" Used when a lead stage is missing """
	pass
