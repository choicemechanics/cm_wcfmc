# -*- encoding: utf-8 -*-
##############################################################################
#    Copyright (c) 2015 - Present Teckzilla Software Solutions Pvt. Ltd. All Rights Reserved
#    Author: [Teckzilla Software Solutions]  <[sales@teckzilla.net]>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of the GNU General Public License is available at:
#    <http://www.gnu.org/licenses/gpl.html>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp import exceptions as odoo_exceptions

from .. import wcfmc_exceptions
from .. import ZohoCreatorCrm
from .. import Quote

class sale_order(models.Model):
    _inherit = "sale.order"
    
    # wcfmc fields
    wcfmc_id = fields.Integer(string="WCFMC ID")
    wcfmc_date = fields.Date(string="WCFMC Date")
    vehicle_registration = fields.Char(string="Vehicle Registration")
    make_model = fields.Char(string="Make and Model")
    fuel = fields.Selection([('petrol', 'Petrol'),('diesel', 'Diesel')], string='Fuel')
    transmission = fields.Selection([('manual', 'Manual'),('automatic', 'Automatic')], string='Transmission')
    registration_year = fields.Integer(string="Registration Year")
    city = fields.Char(string="City")
    postcode = fields.Char(string="Postcode")
    branch_id = fields.Many2one('cm.branch', string="Branch")

    # quote fields
    budget_option = fields.Boolean("Budget Available")
    budget_kit_name = fields.Char("Budget Kit Name")
    budget_kit_type = fields.Char("Budget Kit Type")
    budget_parts_cost = fields.Float("Budget Parts Total")
    budget_parts_retail = fields.Float("Budget Parts Retail")
    budget_margin = fields.Float("Budget Margin")
    budget_bearing_name = fields.Char("Budget Bearing Name")
    budget_bearing_retail = fields.Float("Budget Bearing Retail")
    budget_bearing_cost = fields.Float("Budget Bearing Cost")

    genuine_option = fields.Boolean("Genuine Available")
    genuine_kit_name = fields.Char("Genuine Kit Name")
    genuine_kit_type = fields.Char("Genuine Kit Type")
    genuine_parts_cost = fields.Float("Genuine Parts Cost")
    genuine_parts_retail = fields.Float("Genuine Parts Retail")
    genuine_margin = fields.Float("Genuine Margin")
    genuine_bearing_name = fields.Char("Genuine Bearing Name")
    genuine_bearing_retail = fields.Float("Genuine Bearing Retail")
    genuine_bearing_cost = fields.Float("Genuine Bearing Cost")

    bearing_type = fields.Char("Bearing Type")
    labour_rate = fields.Float("Labour Rate")
    labour_hours = fields.Float("Labour Hours")
    approx_milage = fields.Integer("Approx Milage")

    flywheel_option = fields.Boolean("Flywheel Available")
    flywheel_cost = fields.Boolean("Flywheel Cost")
    flywheel_retail = fields.Boolean("Flywheel Retail")
    flywheel_margin = fields.Boolean("Flywheel Margin")

    quote_cost = fields.Float(compute='compute_quote_cost')
    quote_total = fields.Float(compute='compute_quote_total')
    quote_margin = fields.Float(compute='compute_quote_margin')

    # zoho fields
    zoho_quote_id = fields.Char("Zoho Quote ID")

    def compute_quote_cost(self):
        if self.budget_option:
            self.quote_cost = self.budget_parts_cost
        else:
            self.quote_cost = self.genuine_parts_cost

    def compute_quote_total(self):
        if self.budget_option:
            self.quote_total = self.budget_parts_retail
        else:
            self.quote_total = self.genuine_parts_retail

    def compute_quote_margin(self):
        if self.budget_option:
            self.quote_margin = self.budget_margin
        else:
            self.quote_margin = self.genuine_margin

    @api.multi
    def action_upload(self):
        for so in self:
            if so.can_upload():
                so.wcfmc_upload()
                so.zoho_upload()
                self.state = 'sent'
            else:
                raise odoo_exceptions.except_orm(_("Missing WCFMC Data"),\
                    _("Only quotations in state draft and with the following fields filled can be uploaded to WhoCanFixMyCar:\n\n"\
                        + "\n - WCFMC ID"\
                        + "\n - Vehicle Registration"\
                        + "\n - Make and Model"\
                        + "\n - Registration Year"\
                        + "\n - City"\
                        + "\n - Postcode"))

    def can_upload(self):
        return (self.wcfmc_id != 0 and self.state == 'draft' and len(self.order_line) > 0\
                and self.name and self.vehicle_registration and self.make_model and self.registration_year\
                and self.city and self.postcode)

    def wcfmc_upload(self):
        """ Send quotation to WCFMC """
        if self.can_upload():
            wcfmc_id = self.wcfmc_id

            # construct message get quote total
            quote = self.amount_total
            message = self.env["ir.config_parameter"].get_param("cm.wcfmc.quote_message")
            if not message:
                raise odoo_exceptions.except_orm(_("Quote Message Missing"),\
                    _("Please set a WCFMC quote message in Settings > Configuration > WCFMC Settings"))
            message = message.replace('{price}', '%.2f' % round(quote, 2))
            message = message.replace('{name}', self.partner_id.name)
            message = message.replace('{wcfmc_id}', str(self.wcfmc_id))
            message = message.replace('{vehicle_registration}', self.vehicle_registration)
            message = message.replace('{make_model}', self.make_model)
            message = message.replace('{registration_year}', str(self.registration_year))
            message = message.replace('{city}', self.city)
            message = message.replace('{postcode}', self.postcode)

            try:
                wcfmc = self.env['cm.cron'].get_wcfmc_instance()
                phone = wcfmc.apply_for_job(wcfmc_id, message, quote, self.branch_id.wcfmc_account_id.wcfmc_id)
                self.partner_id.phone = phone
            except wcfmc_exceptions.LoginError as e:
                raise odoo_exceptions.except_orm(_("WhoCanFixMyCar login information missing"), \
                    _("The log in information for WhoCanFixMyCar is missing. Please enter it in Settings > Configuration > WCFMC Settings"))
                
            self.message_post(_("Uploaded to WhoCanFixMyCar"))

    def zoho_upload(self):
        if self.can_upload():
            runscope_auth_token = self.env["ir.config_parameter"].get_param("cm.runscope_auth_token")
            if not runscope_auth_token:
                raise odoo_exceptions.except_orm(_("Missing Runscope Auth Token"), _("Please set the Runscope Auth Token field in Settings > Configuration > WCFMC Settings"))
            try:
                # create the active quote
                zccrm = ZohoCreatorCrm.ZohoCreatorCrm(runscope_auth_token)
                zoho_quote_id = zccrm.create_active_quote(self.order_line[0].product_id.wcfmc_job_name,\
                    self.vehicle_registration, self.wcfmc_id, self.wcfmc_date, self.partner_id.name, self.partner_id.phone, self.branch_id.name, self.make_model, self.quote_cost, \
                    self.quote_total, self.quote_margin, self.bearing_type, self.genuine_parts_cost, self.genuine_parts_retail, self.labour_hours, \
                    self.labour_rate, self.approx_milage, self.budget_option, self.budget_parts_cost, self.budget_parts_retail, self.budget_parts_retail, \
                    self.budget_margin, self.flywheel_option, self.flywheel_cost, self.flywheel_retail, self.flywheel_margin)
                self.zoho_quote_id = zoho_quote_id

                # add the kit to quote parts
                if self.genuine_option:
                    kit_name = self.genuine_kit_name
                    kit_retail = self.genuine_parts_retail
                    kit_cost = self.genuine_parts_cost
                    kit_type = self.genuine_kit_type

                    kit_bearing_name = self.genuine_bearing_name
                    kit_bearing_retail = self.genuine_bearing_retail
                    kit_bearing_cost = self.genuine_bearing_cost
                else:
                    kit_name = self.budget_kit_name
                    kit_retail = self.budget_parts_retail
                    kit_cost = self.budget_parts_cost
                    kit_type = self.budget_kit_type

                    kit_bearing_name = self.budget_bearing_name
                    kit_bearing_retail = self.budget_bearing_retail
                    kit_bearing_cost = self.budget_bearing_cost

                zccrm.add_parts_to_quote(zoho_quote_id, kit_name, kit_retail, kit_cost)
                if kit_type == "2 Piece":
                    zccrm.add_parts_to_quote(zoho_quote_id, kit_bearing_name, kit_bearing_retail, kit_bearing_cost)

                self.message_post(_("Uploaded to Zoho Creator"))
            except ValueError as e:
                self.message_post(_("Upload to Zoho Creator failed: ") + str(e))

sale_order()
