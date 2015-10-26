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


class postcode_config_settings(models.TransientModel):
    _name = "postcode.config.settings"
    _inherit = 'res.config.settings'
    
    wcfmc_username = fields.Char(string='User Name')
    wcfmc_password = fields.Char(string='Password')
    runscope_auth_token = fields.Text(string='Token')
    
    def get_default_wcfmc_username(self, cr, uid, ids, context=None):
        username = self.pool.get("ir.config_parameter").get_param(cr, uid, "postcode.wcfmc_username", context=context)
        return {'wcfmc_username': username}

    def set_wcfmc_username(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "postcode.wcfmc_username", record.wcfmc_username or '', context=context)
        
        
    def get_default_wcfmc_password(self, cr, uid, ids, context=None):
        username = self.pool.get("ir.config_parameter").get_param(cr, uid, "postcode.wcfmc_password", context=context)
        return {'wcfmc_password': username}

    def set_wcfmc_password(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "postcode.wcfmc_password", record.wcfmc_password or '', context=context)
        
        
        
    def get_default_runscope_auth_token(self, cr, uid, ids, context=None):
        username = self.pool.get("ir.config_parameter").get_param(cr, uid, "postcode.runscope_auth_token", context=context)
        return {'runscope_auth_token': username}

    def set_runscope_auth_token(self, cr, uid, ids, context=None):
        config_parameters = self.pool.get("ir.config_parameter")
        record = self.browse(cr, uid, ids[0], context=context)
        config_parameters.set_param(cr, uid, "postcode.runscope_auth_token", record.runscope_auth_token or '', context=context)
        
postcode_config_settings()