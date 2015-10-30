import requests
from xml.etree.ElementTree import fromstring

import cm_exceptions

# Map wcfmc service names to choice mechanics auto quote api. See GetQuote function
SERVICE_TERMS = {
    'Clutch Replacement': 'clutch'
}

def GetQuote(service, api_key, vehicle_registration, location):
    """ Do auto quote using CM's api. $Service will be mapped against SERVICE_TERMS """
    
    if service not in SERVICE_TERMS.keys():
        raise cm_exceptions.UnrecognisedService('Unrecognised service %s' % service)

    api_name = SERVICE_TERMS[service]

    if api_name == 'clutch':
        quote_request = requests.get('http://www.choicemobilemechanics.com/api/quote/clutch/' \
                            + '?key=%(api_key)s&numberplate=%(vehicle_registration)s&location=%(location)s'\
            % {
                'api_key': api_key,
                'vehicle_registration': vehicle_registration,
                'location': location,
            })

        quote_xml = quote_request.content
        quote_element = fromstring(quote_xml)
        budget_kit = quote_element.findall('.//BudgetKit')
        genuine_kit = quote_element.findall('.//GenuineKit')
        kit = budget_kit if budget_kit else genuine_kit
        kit_total_price_raw = kit[0].findall('TotalPrice')[0]
        return float(kit_total_price_raw.text)
    else:
        raise NotImplementedError('Service %s recognised but not implemented' % service)
