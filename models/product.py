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

from .. import ChoiceMechanics

class product_template(models.Model):
    _inherit = "product.template"
    
    wcfmc_job_name = fields.Char(string="WCFMC Job Name")

    _sql_constraints = [
	    ('wcfmc_job_name_unique', 'unique(wcfmc_job_name)', 'WCFMC Job Name must be unique')
	]

    @api.model
    def create(self, vals):
    	self._check_wcfmc_job_name_recognised(vals)
    	return super(product_template, self).create(vals)

    @api.multi
    def write(self, vals):
    	self._check_wcfmc_job_name_recognised(vals)
    	return super(product_template, self).write(vals)

    def _check_wcfmc_job_name_recognised(self, vals):
    	wcfmc_job_name = vals.get('wcfmc_job_name', '')
    	if wcfmc_job_name and wcfmc_job_name not in ChoiceMechanics.SERVICE_TERMS:
    		raise odoo_exceptions.except_orm(_("WCFMC Job Name Not Recognised"), \
    			_("Auto quoting for the WCFMC Job Name %s has not been implemented so you cannot create a product for it" % wcfmc_job_name))

product_template()
