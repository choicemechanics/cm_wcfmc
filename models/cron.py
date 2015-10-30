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
import datetime

from openerp import models, fields, api, _
from openerp import exceptions as odoo_exceptions
from .. import WhoCanFixMyCar, wcfmc_exceptions

_logger = logging.getLogger(__name__)

class cm_cron(models.Model):
    _name = "cm.cron"
    wcfmc = None

    def _get_email(self):
        return self.env["ir.config_parameter"].get_param("cm.wcfmc.email")

    def _get_password(self):
        return self.env["ir.config_parameter"].get_param("cm.wcfmc.password")

    def _get_auth_token(self):
        return self.env["ir.config_parameter"].get_param("cm.runscope_auth_token")

    def _get_email_create_date(self):
        """ 
        Returns the create date for the cm.wcfmc.email field. This is used as the earliest date
        for which to get jobs from wcfmc, otherwise this module would download the entire wcfmc db!
        """
        date_str = self.env['ir.config_parameter'].search([('key', '=', 'cm.wcfmc.email')]).create_date
        return datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()

    def get_wcfmc_instance(self):
        """ Factory for WhoCanFixMyCar instance. Returns cached instance if exists """
        if self.wcfmc:
            return self.wcfmc
        else:
            return WhoCanFixMyCar.WhoCanFixMyCar(self._get_email(), self._get_password())
    
    @api.model
    def get_new_leads(self, ids=None):
        """ Gets jobs from WCFMC and creates POs for them """
        _logger.info("Running get new leads cron")

        # login to wcfmc and raise login exception
        try:
            self.wcfmc = self.get_wcfmc_instance()
        except wcfmc_exceptions.LoginError as e:
            if e.message == WhoCanFixMyCar.WCFMC_LOGIN_ERROR_EMAIL_PASSWORD_NOT_SET\
                or e.message == WhoCanFixMyCar.WCFMC_LOGIN_ERROR_LOGIN_WRONG:
                raise odoo_exceptions.except_orm(_("Could not log in"), _("Could not login to whocanfixmycar, please check the email " +\
                                        "and password in Settings > Configuration > WCFMC Settings. Error message: ") + e.message)

        # get all new job ids
        lead_obj = self.env['crm.lead']
        partner_obj = self.env['res.partner']

        page_number = 1
        wcfmc_ids = []
        earliest_date = self._get_email_create_date()
        stop_fetching = False

        while not stop_fetching:
            _logger.info("Fetching wcfmc ids from page " + str(page_number))

            # save job ids only for new jobs. Stop fetching once we recognise a job, or the jobs are older than the earliest_date
            latest_wcfmc_ids, hit_earliest_date = self.wcfmc.get_latest_wcfmc_ids(page_number, earliest_date)
            latest_wcfmc_ids_with_lead = [lead.wcfmc_id for lead in lead_obj.search([('wcfmc_id', 'in', latest_wcfmc_ids)])]
            latest_wcfmc_ids_without_lead = [wcfmc_id for wcfmc_id in latest_wcfmc_ids if wcfmc_id not in latest_wcfmc_ids_with_lead]
            wcfmc_ids += latest_wcfmc_ids_without_lead

            if len(latest_wcfmc_ids_with_lead) > 0 or hit_earliest_date:
                stop_fetching = True
            else:
                page_number += 1

        # get details for each job
        for wcfmc_id in set(wcfmc_ids):

            # see if job already exists as lead in odoo
            existing_lead = lead_obj.search([('wcfmc_id', '=', wcfmc_id)])
            if existing_lead:
                continue

            job = self.wcfmc.get_job(wcfmc_id)

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
                'type': 'opportunity',
                'name': job.service,
                'vehicle_registration': job.vehicle_registration,
                'wcfmc_id': job.wcfmc_id,
                'wcfmc_date': job.date,
                'date_deadline': job.date,
                'make_model': job.make_model,
                'registration_year': job.registration_year,
                'wcfmc_city': job.city,
                'postcode': job.postcode,
                'description': '\n'.join(job.comments),
                'partner_id': partner.id,
            }
            lead_id = lead_obj.create(vals)
            self.env.cr.commit()
            _logger.info("Created lead for job: " + str(wcfmc_id))

        self.wcfmc = None
        _logger.info("Finished get new leads cron")
        return True
    
    @api.model
    def update_quotations(self, ids=None):
        _logger.info("Running update quotations cron")
        _logger.info("Finished update quotations cron")
        return True

cm_cron()
