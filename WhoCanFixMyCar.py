import requests
from bs4 import BeautifulSoup
from datetime import date
import datetime

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

	def _get_wcfmc_ids(self, url, page_number=1, earliest_date=None):
		""" Get's list of job ids from the url at page_number. 

		Args:
			page_number: the ?page= param on the whocanfixmycar find jobs page
			earliest_date: ignore all jobs whose date is before earliest_date
		"""
		# load find a job at page_number
		jobs_request = self.session.get(url + str(page_number), headers=WCFMC_REQUEST_HEADERS)
		self._check_request_response(jobs_request)
		soup = BeautifulSoup(jobs_request.text)
		wcfmc_ids = []
		hit_earliest_date = False

		# get all job ids and return as a list
		job_elements = soup.findAll('div', attrs={'class': 'card_job'})

		for job_element in job_elements:
			# get date and skip if job date is before earliest job date
			job_date_raw = job_element.find('div', attrs={'class': 'card__date'}).text
			job_date = self._parse_job_date(job_date_raw)
			if earliest_date and job_date < earliest_date:
				hit_earliest_date = True
				continue

			wcfmc_id = int(job_element.find('a', attrs={'class': 'card__title'}).get('href').split('/')[3])
			wcfmc_ids.append(wcfmc_id)
		return (wcfmc_ids, hit_earliest_date)

	def _check_request_response(self, request):
		""" Check the request for any issues and raise the appropriate errors """
		request_content = request.content.lower()

		# check for "Job Check" state
		if request.history and request.history[0].status_code == 302 and request.url == 'https://www.whocanfixmycar.com/mechanic/job-confirmation'\
			and 'job check' in request_content:
			raise wcfmc_exceptions.JobCheckError()

		return request

	def get_latest_wcfmc_ids(self, page_number=1, earliest_date=None):
		return self._get_wcfmc_ids(WCFMC_GET_JOBS_URL, page_number=page_number, earliest_date=earliest_date)

	def get_jobs_won_ids(self, page_number=1, earliest_date=None):
		return self._get_wcfmc_ids(WCFMC_JOBS_WON_URL, page_number=page_number, earliest_date=earliest_date)

	def get_jobs_not_won_ids(self, page_number=1, earliest_date=None):
		return self._get_wcfmc_ids(WCFMC_JOBS_NOT_WON_URL, page_number=page_number, earliest_date=earliest_date)

	def _parse_job_date(self, job_date_raw):
		""" Parses the raw string format date from wcfmc into datetime.date """
		if ':' in job_date_raw: # today (eg 17:35)
			return date.today()
		elif job_date_raw == 'Yesterday': # yesterday (eg 'Yesterday')
			return datetime.date.fromordinal(datetime.date.today().toordinal()-1)
		else: # before yesterday (eg 27/10/2015)
			return date(*map(lambda date_part: int(date_part), reversed(job_date_raw.split('/'))))

	def get_job(self, wcfmc_id):
		""" Returns a Job object populated with job data for specified wcfmc_id """
		# load job page for wcfmc_id
		job_request = self.session.get(WCFMC_JOB_URL + str(wcfmc_id), headers=WCFMC_REQUEST_HEADERS)
		self._check_request_response(job_request)
		soup = BeautifulSoup(job_request.text)
		job_element = soup.find('div', attrs={'class': 'card'})

		# extract data from soup
		job_date_raw = job_element.find('div', attrs={'class': 'card__date'}).text
		job_date = self._parse_job_date(job_date_raw)
		
		job_service = job_element.find(text='service').parent.nextSibling.nextSibling.text
		job_vehicle_registration = job_element.find(text='registration').parent.nextSibling.nextSibling.text
		job_make_model = job_element.find(text='make & model').parent.nextSibling.nextSibling.text
		job_registration_year = job_element.find(text='registration year').parent.nextSibling.nextSibling.text

		job_location_raw = job_element.find(text='location').parent.nextSibling.nextSibling.text
		job_city, job_postcode = job_location_raw.split(', ')

		# get phone - might not exist
		try:
			job_contact_phone = soup.find('a', {'href': lambda tel: tel.startswith('tel:')}).get('href').replace('tel:', '')
		except Exception as e:
			job_contact_phone = ''

		job_contact_first_name = soup.find(text='driver').parent.nextSibling.nextSibling.text
		comments = job_element.findAll('div', attrs={'class': 'col-sm-6'})[1].findAll('p')
		if len(comments):
			job_comment = [comment.text for comment in comments]
		else:
			job_comment = []

		return Job(wcfmc_id, job_date, job_service, job_vehicle_registration, job_make_model, job_registration_year, job_city, \
					job_postcode, job_contact_first_name, job_contact_phone, job_comment)

	def apply_for_job(self, wcfmc_id, message, quote, wcfmc_account_id):
		""" Apply for a job on whocanfixmycar.com, return contact's phone number """
		raise NotImplementedError('This method has not yet been tested and may cost the account owner money')
		data = {
			'message': message,
			'childMechanic': wcfmc_account_id,
			'quote': str(quote),
		}
		url = WCFMC_JOB_APPLICATION_URL % str(wcfmc_id)
		application_request = self.session.post(url, data=data, headers=WCFMC_REQUEST_HEADERS)
		if application_request.status_code == 200:
			job = self.get_job(wcfmc_id)
			return job.contact_phone
		else:
			raise ValueError("An error occured while applying for the job on wcfmc - the request returned status code " + \
					str(application_request.status_code))

	def get_accounts(self, job_ids=None):
		""" Get WCFMC accounts. Returns a list of tuples like [(id, name), ... ] """
		# get a job id so we can load the page to get the list of accounts
		if not job_ids:
			job_ids = self.get_latest_wcfmc_ids()[0]
		job_id = job_ids[0]
		job_request = self.session.get(WCFMC_JOB_URL + str(job_id), headers=WCFMC_REQUEST_HEADERS)
		self._check_request_response(job_request)
		soup = BeautifulSoup(job_request.text)
		account_select_element = soup.find('select', attrs={'name': 'childMechanic'})
		account_select_option_elements = account_select_element.findAll('option')
		accounts = []
		for option in account_select_option_elements:
			account_id = option['value']
			account_name = option.text
			accounts.append((account_id, account_name))
		return accounts
