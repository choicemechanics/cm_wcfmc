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

import logging

from openerp import models, fields, api, _
from openerp import exceptions as odoo_exceptions

from .. import wcfmc_exceptions
from .. import cm_exceptions
from .. import Quote

_logger = logging.getLogger(__name__)

class crm_lead(models.Model):
    _inherit = "crm.lead"
    
    wcfmc_id = fields.Integer(string="WCFMC ID")
    wcfmc_date = fields.Date(string="WCFMC Date")
    vehicle_registration = fields.Char(string="Vehicle Registration")
    make_model = fields.Char(string="Make and Model")
    fuel = fields.Selection([('petrol', 'Petrol'),('diesel', 'Diesel')], string='Fuel')
    transmission = fields.Selection([('manual', 'Manual'),('automatic', 'Automatic')], string='Transmission')
    registration_year = fields.Integer(string="Registration Year")
    wcfmc_city = fields.Char(string="City")
    postcode = fields.Char(string="Postcode")
    branch_id = fields.Many2one('cm.branch', string="Branch")

    @api.model
    def create(self, vals):
        """ 
        Automatically quote leads within served postcode area and with
        products whose wcfmc_job_name field matches the lead name
        and if there are no comments
        """
        sale_order = None
        stage_obj = self.env['crm.case.stage']
        product_tmpl_obj = self.env['product.template']
        product_obj = self.env['product.product']
        postcode_obj = self.env['cm.postcode']
        sale_obj = self.env['sale.order']
        sale_line_obj = self.env['sale.order.line']
        message = None

        # Is lead qualified? (within postcode range and for offered services)
        if vals.get('postcode') and vals.get('name'):
            qualified_stage_ids = stage_obj.search([('name', '=', 'Qualified')])
            if not qualified_stage_ids:
                raise wcfmc_exceptions.LeadStageError("Missing Qualified stage")

            # find postcodes that match exactly the first two letters, or the first three letters
            postcode_ids = postcode_obj.search([('area', 'in', [vals.get('postcode')[:2], vals.get('postcode')[:3]])])
            product_ids = product_tmpl_obj.search([('wcfmc_job_name', '=', vals.get('name'))])
            
            # Lead is qualified
            if postcode_ids and product_ids:

                # set stage to qualified
                vals['stage_id'] = qualified_stage_ids[0].id
                message = _('Lead automatically qualified because we serve the postcode and product')

                # get branch for postcode
                branch = [postcode.branch_ids[0] for postcode in postcode_ids if postcode.branch_ids][0]
                vals['branch_id'] = branch.id

                # Can we auto quote?
                if vals.get('partner_id') and vals.get('name') and vals.get('postcode') and vals.get('wcfmc_id'):
                    quoted_stage_ids = stage_obj.search([('name', '=', "Quoted")])
                    if not quoted_stage_ids:
                        raise wcfmc_exceptions.LeadStageError("Missing Quoted stage")

                    # We can auto quote (no comment)
                    if not vals.get('description'):

                        # get price from api
                        api_key = self.env['ir.config_parameter'].get_param('cm.api_key')
                        if not api_key:
                            raise odoo_exceptions.except_orm(_("Missing Choice Mechanics API Key"), \
                                    _("Please set the Choice Mechanics API Key field in Settings > Configuration > WCFMC Settings"))

                        try:
                            quote = Quote.Quote(api_key, vals['vehicle_registration'], branch.name, vals['name'])
                        except cm_exceptions.NoKitPriceError:
                            quote = None
                            message = _("Tried to auto quote but no kit price found found from API lookup")
                        except ValueError:
                            raise odoo_exceptions.except_orm(_("Unrecognised Vehicle Registration"), \
                                    _("The vehicle registration %s could not be recognised by the auto quote API") % vals['vehicle_registration'])

                        if quote:
                            # choose budget or genuine for quote price
                            if quote.budget_option:
                                price = quote.budget_parts_retail
                            else:
                                price = quote.genuine_parts_retail

                            # create the sale.order (quotation)
                            sale_order_vals = {
                                'name' : self.env['ir.sequence'].next_by_code('sale.order'),
                                'wcfmc_id' : vals.get('wcfmc_id'),
                                'wcfmc_date': vals.get('wcfmc_date'),
                                'vehicle_registration': vals.get('vehicle_registration'),
                                'partner_id' : vals.get('partner_id'),
                                'partner_shipping_id' : vals.get('partner_id'),
                                'city': vals.get('wcfmc_city'),
                                'make_model': vals.get('make_model'),
                                'registration_year': vals.get('registration_year'),
                                'postcode': vals.get('postcode'),
                                'branch_id': vals.get('branch_id'),
                                'fuel': vals.get('fuel'),
                                'transmission': vals.get('transmission'),

                                # quote vals
                                'budget_option': quote.budget_option,
                                'budget_kit_name': quote.budget_kit_name,
                                'budget_kit_type': quote.budget_kit_type,
                                'budget_parts_cost': quote.budget_parts_cost,
                                'budget_parts_retail': quote.budget_parts_retail,
                                'budget_margin': quote.budget_margin,
                                'budget_bearing_name': quote.budget_bearing_name,
                                'budget_bearing_retail': quote.budget_bearing_retail,
                                'budget_bearing_cost': quote.budget_bearing_cost,

                                'genuine_option': quote.genuine_option,
                                'genuine_kit_name': quote.genuine_kit_name,
                                'genuine_kit_type': quote.genuine_kit_type,
                                'genuine_parts_cost': quote.genuine_parts_cost,
                                'genuine_parts_retail': quote.genuine_parts_retail,
                                'genuine_margin': quote.genuine_margin,
                                'genuine_bearing_name': quote.genuine_bearing_name,
                                'genuine_bearing_retail': quote.genuine_bearing_retail,
                                'genuine_bearing_cost': quote.genuine_bearing_cost,

                                'bearing_type': quote.bearing_type,
                                'labour_rate': quote.labour_rate,
                                'labour_hours': quote.labour_hours,
                                'approx_milage': quote.approx_milage,

                                'flywheel_option': quote.flywheel_option,
                            }
                            sale_order = sale_obj.create(sale_order_vals)

                            # create the sale.order lines
                            product_id = product_obj.search([('product_tmpl_id', '=', product_ids[0].id)])
                            sale_order_line_vals = {
                                'product_id': product_id[0].id,
                                'price_unit' : price,
                                'product_uom_qty' : 1,
                                'product_uom' : product_id[0].product_tmpl_id.uom_id.id,
                                'order_id' : sale_order[0].id,
                                'name' : product_id[0].product_tmpl_id.name,
                            }
                            sale_order_line_id = sale_line_obj.create(sale_order_line_vals)

                            # trigger upload to wcfmc and zoho
                            sale_order.action_upload()

                            # set lead stage to quoted
                            if quoted_stage_ids:
                                vals['stage_id'] = quoted_stage_ids[0].id

                            message = _('Lead auto quoted: %s') % sale_order.name
                            _logger.info('Created quotation for job: ' + str(vals['wcfmc_id']))

        # create the lead
        lead = super(crm_lead, self).create(vals)
        lead.message_post(message)

        # link sale.order with crm.lead
        if sale_order:
            sale_order.opportunity_id = lead.id

        return lead
        
crm_lead()
