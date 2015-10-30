import requests
from xml.etree.ElementTree import fromstring

import cm_exceptions

# Map wcfmc service names to choice mechanics auto quote api. See GetQuote function
SERVICE_TERMS = {
    'Clutch Replacement': 'clutch'
}

class Quote():
    """ Represents a repair quote from choice mechanics API """

    vehicle_registration = None
    location = None
    service = None

    def __init__(self, api_key, vehicle_registration, location, service):
        """ Do auto quote using CM's api. $Service will be mapped against SERVICE_TERMS """

        self.api_key = api_key
        self.vehicle_registration = vehicle_registration
        self.location = location
        self.service = service

        self._get_quote_from_cm_api()

    def _get_quote_from_cm_api(self):
        """ Queries the CM api for a quote and saves the information on the self """
        if self.service not in SERVICE_TERMS.keys():
            raise cm_exceptions.UnrecognisedService('Unrecognised service %s' % self.service)

        api_name = SERVICE_TERMS[self.service]

        if api_name == 'clutch':
            quote_request = requests.get('http://www.choicemobilemechanics.com/api/quote/clutch/' \
                                + '?key=%(api_key)s&numberplate=%(vehicle_registration)s&location=%(location)s'\
                % {
                    'api_key': self.api_key,
                    'vehicle_registration': self.vehicle_registration,
                    'location': self.location,
                })

            if 'This vehicle has not been looked up correctly' in quote_request.content:
                raise ValueError('Look up failed (This vehicle has not been looked up correctly)')

            quote_xml = quote_request.content
            quote_element = fromstring(quote_xml)

            # extract kit
            budget_kit_element = quote_element.find('.//BudgetKit')
            genuine_kit_element = quote_element.find('.//GenuineKit')

            if str(budget_kit_element) == 'None' and str(genuine_kit_element) == 'None': # normal None check is not supported by xml lib
                raise cm_exceptions.NoKitPriceError()

            self.budget_option = bool(budget_kit_element)
            if self.budget_option:
                self.budget_parts_cost = float(budget_kit_element.find('.//TotalCost').text or '0')
                self.budget_parts_retail = float(budget_kit_element.find('.//TotalPrice').text or '0')
                self.budget_margin = float(budget_kit_element.find('.//TotalMargin').text or '0')
            else:
                self.budget_parts_cost = 0
                self.budget_parts_retail = 0
                self.budget_margin = 0

            self.genuine_option = bool(genuine_kit_element)
            if self.genuine_option:
                self.genuine_parts_cost = float(genuine_kit_element.find('.//TotalCost').text or '0')
                self.genuine_parts_retail = float(genuine_kit_element.find('.//TotalPrice').text or '0')
                self.genuine_margin = float(genuine_kit_element.find('.//TotalMargin').text or '0')
            else:
                self.genuine_parts_cost = 0
                self.genuine_parts_retail = 0
                self.genuine_margin = 0
                
            # extract quote details
            self.quote_details = quote_element.find('.//QuoteDetails')
            self.bearing_type = self.quote_details.find('BearingType').text or ''
            self.labour_rate = self.quote_details.find('LabourRate').text or ''
            self.labour_hours = self.quote_details.find('LabourTime').text or ''
            self.approx_milage = self.quote_details.find('Mileage').text or ''

            # extract flywheel information
            flywheel_element = quote_element.find('.//Flywheel')
            self.flywheel_option = (flywheel_element.find('.//DualMass').text != '0') # True if dual mass is not 0
            if self.flywheel_option:
                self.flywheel_cost = float(flywheel_element.find('.//TotalCost').text or '0')
                self.flywheel_retail = float(flywheel_element.find('.//TotalPrice').text or '0')
                self.flywheel_margin = float(flywheel_element.find('.//TotalMargin').text or '0')
            else:
                self.flywheel_cost = 0
                self.flywheel_retail = 0
                self.flywheel_margin = 0

        else:
            raise NotImplementedError('Service %s recognised but not implemented' % service)
