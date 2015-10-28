import requests
from bs4 import BeautifulSoup
from datetime import date

from Job import Job
import wcfmc_exceptions

WCFMC_LOGIN_URL = 'https://www.whocanfixmycar.com/login'
WCFMC_GET_JOBS_URL = 'https://www.whocanfixmycar.com/find-jobs?page='
WCFMC_JOBS_WON_URL = 'https://www.whocanfixmycar.com/mechanic/jobs?tab=jobs-won&?page='
WCFMC_JOBS_NOT_WON_URL = 'https://www.whocanfixmycar.com/mechanic/jobs?tab=not-won-jobs&page='
WCFMC_JOB_URL = 'https://www.whocanfixmycar.com/mechanic/jobs/'
WCFMC_JOB_APPLICATION_URL = 'https://www.whocanfixmycar.com/mechanic/jobs/%s/apply'
WCFMC_REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36'}

WCFMC_LOGIN_ERROR_EMAIL_PASSWORD_NOT_SET = 'email or password not set'
WCFMC_LOGIN_ERROR_LOGIN_WRONG = 'wrong email or password'

class WhoCanFixMyCar():
	""" Data scraper for whocanfixmycar.com """

	def __init__(self, email, password):
		if not email or not password:
			raise wcfmc_exceptions.LoginError(WCFMC_LOGIN_ERROR_EMAIL_PASSWORD_NOT_SET)
		self.session = requests.Session()
		self._login(email, password)

	def _login(self, email, password):
		login = self.session.post(WCFMC_LOGIN_URL, data={'email': email, 'password': password}, headers=WCFMC_REQUEST_HEADERS)
		if 'log out' not in login.content.lower():
			raise wcfmc_exceptions.LoginError(WCFMC_LOGIN_ERROR_LOGIN_WRONG)

	def _get_job_ids(self, url, page_number=1):
		""" Get's list of job ids from the url at page_number """
		# load find a job at page_number
		jobs_request = self.session.get(url + str(page_number), headers=WCFMC_REQUEST_HEADERS)
		soup = BeautifulSoup(jobs_request.text)
		job_ids = []

		# get all job ids and return as a list
		job_elements = soup.findAll('div', attrs={'class': 'card_job'})
		for job_element in job_elements:
			job_id = job_element.find('a', attrs={'class': 'card__title'}).get('href').split('/')[3]
			job_ids.append(job_id)
		return job_ids

	def get_find_job_ids(self, page_number=1):
		return self._get_job_ids(WCFMC_GET_JOBS_URL, page_number)

	def get_jobs_won_ids(self, page_number=1):
		return self._get_job_ids(WCFMC_JOBS_WON_URL, page_number)

	def get_jobs_not_won_ids(self, page_number=1):
		return self._get_job_ids(WCFMC_JOBS_NOT_WON_URL, page_number)

	def get_job(self, job_id):
		""" Returns a Job object populated with job data for specified job_id """
		# load job page for job_id
		job_request = self.session.get(WCFMC_JOB_URL + str(job_id), headers=WCFMC_REQUEST_HEADERS)
		soup = BeautifulSoup(job_request.text)
		job_element = soup.find('div', attrs={'class': 'card'})

		# extract data from soup
		job_date_raw = job_element.find('div', attrs={'class': 'card__date'}).text
		if ':' in job_date_raw:
			job_date = date.today()
		else:
			job_date = date(*map(lambda date_part: int(date_part), reversed(job_date_raw.split('/'))))
		
		job_service = job_element.find(text='service').parent.nextSibling.nextSibling.text
		job_vehicle_registration = job_element.find(text='registration').parent.nextSibling.nextSibling.text
		job_make_model = job_element.find(text='make & model').parent.nextSibling.nextSibling.text
		job_registration_year = job_element.find(text='registration year').parent.nextSibling.nextSibling.text

		job_location_raw = job_element.find(text='location').parent.nextSibling.nextSibling.text
		job_city, job_postcode = job_location_raw.split(', ')

		job_contact_first_name = soup.find(text='driver').parent.nextSibling.nextSibling.text
		comments = job_element.findAll('div', attrs={'class': 'col-sm-6'})[1].findAll('p')
		if len(comments):
			job_comment = [comment.text for comment in comments]
		else:
			job_comment = []

		return Job(job_id, job_date, job_service, job_vehicle_registration, job_make_model, job_registration_year, job_city, \
					job_postcode, job_contact_first_name, job_comment)

	def apply_for_job(self, job_id, message, quote):
		""" Apply for a job on whocanfixmycar.com """
		raise NotImplemented('This method has not yet been tested and may cost the account owner money')
		# TODO: Remove hard coded sub account id
		data = {
			'message': message,
			'childMechanic': '3124',
			'quote': str(quote),
		}
		url = WCFMC_JOB_APPLICATION_URL % job_id
		self.session.post(url, data=data, headers=WCFMC_REQUEST_HEADERS)
