class WcfmcRequestException(Exception):
	""" Base class for any request exceptions """
	pass

class LoginError(WcfmcRequestException):
	""" Used when WCFMC login fails. Check message for more information """
	pass

class JobCheckError(WcfmcRequestException):
	""" 
	Raised when the wcfmc account is in 'Job Check' state, meaning all pages redirect to the job check page. 
	We can't get data from the site in this stage, so any request to wcfmc.com that redirects to this page 
	will raise this error
	"""
	pass

class LeadStageError(Exception):
	""" Used when a lead stage is missing """
	pass
