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

class cm_wcfmc_config_settings(models.TransientModel):
    _name = "cm.wcfmc.config.settings"
    _inherit = 'res.config.settings'
    
    wcfmc_email = fields.Char(string='Email')
    wcfmc_password = fields.Char(string='Password')
    api_key = fields.Char(string='Choice Mechanics API Key')
    runscope_auth_token = fields.Char(string='Runscope Auth Token')
    quote_message = fields.Text(string='Quote Message')
    
    def get_default_wcfmc_email(self, cr, uid, ids, context=None):
        email = self.pool.get("ir.config_parameter").get_param(cr, uid, "cm.wcfmc.email", context=context)
        return {'wcfmc_email': email}

    def set_wcfmc_email(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "cm.wcfmc.email", record.wcfmc_email or '', context=context)
        
    def get_default_wcfmc_password(self, cr, uid, ids, context=None):
        password = self.pool.get("ir.config_parameter").get_param(cr, uid, "cm.wcfmc.password", context=context)
        return {'wcfmc_password': password}

    def set_wcfmc_password(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "cm.wcfmc.password", record.wcfmc_password or '', context=context)
        
    def get_default_api_key(self, cr, uid, ids, context=None):
        api_key = self.pool.get("ir.config_parameter").get_param(cr, uid, "cm.api_key", context=context)
        return {'api_key': api_key}

    def set_api_key(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "cm.api_key", record.api_key or '', context=context)
        
    def get_default_quote_message(self, cr, uid, ids, context=None):
        quote_message = self.pool.get("ir.config_parameter").get_param(cr, uid, "cm.wcfmc.quote_message", context=context)
        return {'quote_message': quote_message}

    def set_quote_message(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "cm.wcfmc.quote_message", record.quote_message or '', context=context)

    def get_default_runscope_auth_token(self, cr, uid, ids, context=None):
        runscope_auth_token = self.pool.get("ir.config_parameter").get_param(cr, uid, "cm.runscope_auth_token", context=context)
        return {'runscope_auth_token': runscope_auth_token}

    def set_runscope_auth_token(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "cm.runscope_auth_token", record.runscope_auth_token or '', context=context)
        
cm_wcfmc_config_settings()
