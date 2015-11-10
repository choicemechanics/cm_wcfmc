import requests
from xml.etree.ElementTree import fromstring
import datetime

class ZohoCreatorCrm():
    """ Used to interact with the Zoho Creator CRM """

    def __init__(self, runscope_auth_token):
        """ check and cache the runscope auth token """
        if not runscope_auth_token:
            raise ValueError("Missing runscope_auth_token")
        self.runscope_auth_token = runscope_auth_token

    def _check_request_result(self, request):
        """ 
        Check the response returned from the server for common errors 
        Returns a tuple with the xml element and the status field text from the response
        """
        if 'An error has occurred.' in request.content:
            raise ValueError("An error occured communicating with runscope. Check the auth token field in the WCFMC settings")

        response_element = fromstring(request.content)
        return (response_element, response_element.find('.//status').text)

    def create_active_quote(self, type, vehicle_registration, wcfmc_id, date_time, first_name, phone, branch, make_model, total_cost, total_price, \
        margin, bearing_type, genuine_parts_cost, genuine_parts_retail, labour_hours, labour_rate, approx_milage, budget_option, budget_parts_cost, \
        budget_parts_retail, budget_total, budget_margin, flywheel_option, flywheel_cost, flywheel_retail, flywheel_margin):
        """
        Add a quote to zoho creator using the New_Quote form:
        https://creator.zoho.com/appbuilder/choicemobilemechanics/crm/form/New_Quote/edit
        Returns the ID of the created quote
        """

        # map some data between the api and zoho
        if bearing_type == 'CSC':
            bearing_type_zoho = 'Slave Cylinder'
        else:
            bearing_type_zoho = 'Bearing'

        url = "https://creator-zoho-com-2hi73fdvwkzz.runscope.net/api/choicemobilemechanics/xml/crm/form/New_Quote/record/add/";
        post_data = {
            'authtoken': self.runscope_auth_token,
            'scope': 'creatorapi',
            'Number_Plate': vehicle_registration,
            'Time_Date': datetime.datetime.strptime(date_time, '%Y-%m-%d').strftime('%d-%b-%Y %H:%M:%S'),
            'Source_Type': 'WCFMC', 
            'Lead_ID': wcfmc_id,
            'Incoming_Source': 'WCFMC',
            'Contacted_Email': 'Yes',
            'Contacted_Phone': 'No',
            'Type': 'Clutch',
            'First_Name': first_name,
            'Telephone': phone or '',
            'Location': branch,
            'Vehicle_Reg': vehicle_registration,
            'Vehicle_Type': make_model,
            'Bearing_Type': bearing_type_zoho,
            'Cost_Parts': genuine_parts_cost,
            'Retail_Parts': genuine_parts_retail,
            'Labour_Hours': labour_hours,
            'Labour_Rate': labour_rate,
            'Approx_Mileage': approx_milage,
            'Total_Cost': total_cost,
            'Quote_Total': total_price,
            'Margin': margin,
            'Budget_Option': budget_option and 'Yes' or 'No',
            'Budget_Parts_Cost': budget_parts_cost,
            'Budget_Parts_Retail': budget_parts_retail,
            'Budget_Costs': budget_parts_retail,
            'Budget_Total': budget_total,
            'Budget_Margin': budget_margin,
            'Flywheel': flywheel_option and 'Yes' or 'No',
            'Flywheel_Cost': flywheel_cost or '0',
            'Flywheel_Retail': flywheel_retail or '0',
            'Flywheel_Total': flywheel_retail or '0',
            'Flywheel_Margin': flywheel_margin or '0',
            'Quote_Method': 'Website',
            'Quoted_By': 'Website',
            'Status': 'Quoted'
        }
        create_active_quote_request = requests.post(url, post_data)
        response_element, status = self._check_request_result(create_active_quote_request)
        if status == 'Success':
            # get id from returned xml
            id_element = response_element.find('.//field[@name="ID"]')
            return id_element.find('value').text
        else:
            raise ValueError(status)

    def add_parts_to_quote(self, quote_id, kit_name, kit_price_retail, kit_cost):
        """ Add a parts order to the quote using the Quote_Parts form """
        url = "https://creator-zoho-com-2hi73fdvwkzz.runscope.net/api/choicemobilemechanics/xml/crm/form/Quote_Parts/record/add/";
        post_data = {
            'authtoken': self.runscope_auth_token,
            'scope': 'creatorapi',
            'Parts_ID': quote_id,
            'Supplier': 'Euro Car Parts',
            'Description': kit_name,
            'Discount': '37.5',
            'Price': kit_price_retail,
            'Cost_Price': kit_cost,
            'Quantity': '1',
        }
        add_parts_to_quote_request = requests.post(url, post_data)
        response_element, status = self._check_request_result(add_parts_to_quote_request)
        if status != 'Success':
            raise ValueError(status)
