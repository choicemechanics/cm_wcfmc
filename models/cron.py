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
_logger = logging.getLogger(__name__)

from openerp import models, fields, api, _
from openerp import exceptions as odoo_exceptions
from .. import WhoCanFixMyCar, wcfmc_exceptions

class cm_cron(models.Model):
    _name = "cm.cron"

    def _get_email(self):
        return self.env["ir.config_parameter"].get_param("cm.wcfmc.email")

    def _get_password(self):
        return self.env["ir.config_parameter"].get_param("cm.wcfmc.password")

    def _get_auth_token(self):
        return self.env["ir.config_parameter"].get_param("cm.runscope_auth_token")
    
    @api.model
    def get_new_leads(self, ids=None):
        """ Gets jobs from WCFMC and creates POs for them """
        _logger.info("Running get new leads cron")

        # login to wcfmc and raise login exception
        try:
            wcfmc = WhoCanFixMyCar.WhoCanFixMyCar(self._get_email(), self._get_password())
        except wcfmc_exceptions.LoginError as e:
            if e.message == WhoCanFixMyCar.WCFMC_LOGIN_ERROR_EMAIL_PASSWORD_NOT_SET\
                or e.message == WhoCanFixMyCar.WCFMC_LOGIN_ERROR_LOGIN_WRONG:
                raise odoo_exceptions.UserError(_("Could not login to whocanfixmycar, please check the email " +\
                                        "and password in Settings > General Settings > WCFMC Settings. Error message: ") + e.message)

        # get job ids from find jobs page
        job_ids = wcfmc.get_find_job_ids()
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']

        # get details for each job
        for job_id in job_ids:

            # see if job already exists as lead in odoo
            existing_lead = lead_obj.search([('wcfmc_id', '=', int(job_id))])
            if existing_lead:
                continue

            job = wcfmc.get_job(job_id)

            # find existing partner using vehicle reg, or create new one
            partner_ids = partner_obj.search([('vehicle_registration', '=', job.vehicle_registration)])
            if not partner_ids:
                vals = {
                    'name': job.contact_first_name,
                    'vehicle_registration': job.vehicle_registration,
                }
                partner = partner_obj.create(vals)
            else:
                partner = partner_ids[0]

            # extract values and create the lead
            vals = {
                'name': job.service,
                'vehicle_registration': job.vehicle_registration,
                'wcfmc_id': job.wcfmc_id,
                'date_deadline': job.date,
                'make_model': job.make_model,
                'registration_year': job.registration_year,
                'city': job.city,
                'postcode': job.postcode,
                'description': '\n'.join(job.comments),
                'partner_id': partner.id,
            }
            lead_id = lead_obj.create(vals)
            _logger.info("Created lead for job: " + job_id)

        _logger.info("Finished get new leads cron")
        return True
    
    @api.model
    def update_quotations(self, ids=None):
        _logger.info("Running update quotations cron")
        _logger.info("Finished update quotations cron")
        return True

cm_cron()
