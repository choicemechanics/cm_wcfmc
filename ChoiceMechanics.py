import requests
from xml.etree.ElementTree import fromstring
import datetime

def zoho_create_active_quote(runscope_auth_token, type, vehicle_registration, date_time, first_name, branch, make_model, total_cost, total_price, \
        margin, bearing_type, genuine_parts_cost, genuine_parts_retail, labour_hours, labour_rate, approx_milage, budget_option, buget_parts_cost, \
        budget_parts_retail, budget_total, budget_margin, flywheel_option, flywheel_cost, flywheel_retail, flywheel_margin):
    """
    Add a quote to zoho creator using the New_Quote form:
    https://creator.zoho.com/appbuilder/choicemobilemechanics/crm/form/New_Quote/edit
    """
    if not runscope_auth_token:
        raise ValueError("Missing runscope_auth_token")
    url = "https://creator-zoho-com-2hi73fdvwkzz.runscope.net/api/choicemobilemechanics/xml/crm/form/New_Quote/record/add/";
    post_data = {
        'authtoken': runscope_auth_token,
        'scope': 'creatorapi',
        'Number_Plate': vehicle_registration,
        'Time_Date': datetime.datetime.strptime(date_time, '%Y-%m-%d').strftime('%d-%b-%Y %H:%M:%S'),
        'Source_Type': 'WCFMC', 
        'Incoming_Source': 'WCFMC',
        'Contacted_Email': 'Yes',
        'Contacted_Phone': 'No',
        'Type': 'Clutch',
        'First_Name': first_name,
        'Location': branch,
        'Vehicle_Reg': vehicle_registration,
        'Vehicle_Type': make_model,
        'Bearing_Type': bearing_type,
        'Cost_Parts': genuine_parts_cost,
        'Retail_Parts': genuine_parts_retail,
        'Labour_Hours': labour_hours,
        'Labour_Rate': labour_rate,
        'Approx_Mileage': approx_milage,
        'Total_Cost': total_cost,
        'Quote_Total': total_price,
        'Margin': margin,
        'Budget_Option': budget_option and 'Yes' or 'No',
        'Budget_Parts_Cost': buget_parts_cost,
        'Budget_Parts_Retail': budget_parts_retail,
        'Budget_Costs': budget_parts_retail,
        'Budget_Total': budget_parts_retail,
        'Budget_Margin': budget_margin,
        'Flywheel': flywheel_option and 'Yes' or 'No',
        'Flywheel_Cost': flywheel_cost,
        'Flywheel_Retail': flywheel_retail,
        'Flywheel_Total': flywheel_retail,
        'Flywheel_Margin': flywheel_margin,
        'Quote_Method': 'Website',
        'Quoted_By': 'Website',
        'Status': 'Quoted'
    }
    create_active_quote_request = requests.post(url, post_data)
    if 'An error has occurred.' in create_active_quote_request.content:
        raise ValueError("An error occured communicating with runscope. Check the auth token field in the WCFMC settings")
    element = fromstring(create_active_quote_request.content)
    status = element.find('.//status').text
    if status == 'Success':
        return True
    else:
        raise ValueError(status)
