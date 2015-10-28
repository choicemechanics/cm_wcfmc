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
        if vals.get('wcfmc_id',False):
            wcfmc = vals.get('wcfmc_id',False)
        return super(sale_order, self).create(vals)
        
sale_order()
    
