import requests
from xml.etree.ElementTree import fromstring

def GetQuoteClutch(api_key, vehicle_registration, location):
    """ Retrive the total price for a clutch quote from the choice mechanics api """
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
