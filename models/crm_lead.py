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

class crm_lead(models.Model):
    _inherit = "crm.lead"
    
    wcfmc_id = fields.Integer(string="WCFMC ID")
    car_registration = fields.Char(string="Car Registration")
    make_model = fields.Char(string="Model")
    fuel = fields.Selection([('petrol', 'Petrol'),('diesel', 'Diesel')], string='Fuel')
    transmission = fields.Selection([('manual', 'Manual'),('automatic', 'Automatic')], string='Transmission')
    registration_year = fields.Integer(string="Registration Year")
    city = fields.Char(string="City")
    postcode = fields.Char(string="Postcode")


    @api.model
    def create(self, vals):
        if vals.get('partner_id',False):
            product_tmpl_obj = self.env['product.template']
            product_obj = self.env['product.product']
            postcode_obj = self.env['cm.postcode']
            sale_obj = self.env['sale.order']
            sale_line_obj = self.env['sale.order.line']
            stage_obj = self.env['crm.stage']
            stage_ids = stage_obj.search([('name', '=', "Quoted")])
            if vals.get('name'):
                prod_ids = product_tmpl_obj.search([('wcfmc_job_name', '=', vals.get('name'))])
            if vals.get('postcode'):
                postcode_ids = postcode_obj.search([('part_1', '=', vals.get('postcode')[:3])])
            if vals.get('wcfmc_id',False) and not vals.get('text',False) and prod_ids and postcode_ids:
                vals = { 
                    'wcfmc_id' : vals.get('wcfmc_id'),
                    'partner_id' : vals.get('partner_id'),
                    'partner_shipping_id' : vals.get('partner_id'),
                    'name' : self.env['ir.sequence'].next_by_code('sale.order')
                    }
                order_id = sale_obj.create(vals)
                if prod_ids and order_id:
                    product_id = product_obj.search([('product_tmpl_id', '=', prod_ids[0].id)])
                    order_line_vals = {
                        'product_id': product_id[0].id,
                        'price_unit' : 1,
                        'product_uom_qty' : 1,
                        'product_uom' : product_id[0].product_tmpl_id.uom_id.id,
                        'order_id' : order_id[0].id,
                        'name' : product_id[0].product_tmpl_id.name
                        }
                    order_line_id = sale_line_obj.create(order_line_vals)
                    if stage_ids:
                        self.write({'stage_id' : stage_ids[0].id})
                    self._cr.commit()
        return super(crm_lead, self).create(vals)
        
        
crm_lead()
    
