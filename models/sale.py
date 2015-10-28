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

class sale_order(models.Model):
    _inherit = "sale.order"
    
    wcfmc_id = fields.Integer(string="WCFMC ID")
    vehicle_registration = fields.Char(string="Car Registration")
    make_model = fields.Char(string="Model")
    fuel = fields.Selection([('petrol', 'Petrol'),('diesel', 'Diesel')], string='Fuel')
    transmission = fields.Selection([('manual', 'Manual'),('automatic', 'Automatic')], string='Transmission')
    registration_year = fields.Integer(string="Registration Year")
    city = fields.Char(string="City")
    postcode = fields.Char(string="Postcode")

    @api.model
    def create(self, vals):
        """ Send quotation to WCFMC """
        so = super(sale_order, self).create(vals)
        if vals.get('wcfmc_id') and so.state == 'draft':
            wcfmc_id = vals.get('wcfmc_id')

            # construct message get quote total
            quote = str(so.amount_total)
            message = self.env["ir.config_parameter"].get_param("cm.wcfmc.quote_message")
            if not message:
                raise odoo_exceptions.UserError(_("Please set a WCFMC quote message in Settings > General Settings > WCFMC Settings"))
            message = message.replace('{price}', str(so.amount_total))
            message = message.replace('{name}', so.partner_id.name)
            message = message.replace('{wcfmc_id}', str(so.wcfmc_id))
            message = message.replace('{service}', so.order_line[0].product_id[0].name) 
            message = message.replace('{vehicle_registration}', so.vehicle_registration)
            message = message.replace('{make_model}', so.make_model)
            message = message.replace('{registration_year}', str(so.registration_year))
            message = message.replace('{city}', so.city)
            message = message.replace('{postcode}', so.postcode)

            wcfmc = self.env['cm.cron'].get_wcfmc_instance()
            wcfmc.apply_for_job(wcfmc_id, message, quote)
            
            so.state = 'sent'
        return so
        
sale_order()
