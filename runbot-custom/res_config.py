# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.fields import Boolean
from openerp.models import TransientModel, api
from openerp.exceptions import Warning

class RunbotConfigSettings(TransientModel):
    _inherit = 'runbot.config.settings'

    default_disable_job_10 = Boolean('Disable the creation of the database \'base\'')

    @api.model
    def get_default_parameters(self, fields):
        result = super(RunbotConfigSettings, self).get_default_parameters(fields)

        icp = self.env['ir.config_parameter']
        disable_job_10 = icp.get_param('runbot.disable_job_10', default='True')
        if disable_job_10 == 'False':
            disable_job_10 = False
        else:
            disable_job_10 = True

        result['default_disable_job_10'] = disable_job_10
        return result

    @api.multi
    def set_default_parameters(self):
        icp = self.env['ir.config_parameter']
        icp.set_param('runbot.disable_job_10', str(self[0].default_disable_job_10))