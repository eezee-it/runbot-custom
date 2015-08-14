# -*- encoding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2010-2015 Eezee-It (<http://www.eezee-it.com>).
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
import openerp.tools as tools
import threading
import traceback
import openerp
import logging
from openerp import models, api, fields

_logger = logging.getLogger(__name__)


class RunbotRepo(models.Model):
    _inherit = 'runbot.repo'

    install_chart_account = fields.Boolean('Install the chart account', default=True,
                                    help="Install the chart account according the country of the company")


class RunbotBuild(models.Model):
    _inherit = "runbot.build"

    def job_25_install_chart_account(self, cr, uid, build, lock_path, log_path):
        """
        Install the chart of account only if the module account is installed AND the flag "Install Char of Account"
        is checked on the repo
        """
        # Check if this job must be ignored
        if not build.repo_id.install_chart_account:
            _logger.debug("Ignore chart account installation")
            return

        build._log('test_chart_account', 'Start install chart account')

        # Create a new cursor to the new DB
        db = openerp.sql_db.db_connect('%s-all' % build.dest)
        threading.current_thread().dbname = '%s-all' % build.dest
        build_cr = db.cursor()

        try:
            # Check if the module account is installed
            build_cr.execute("SELECT id FROM ir_module_module WHERE state = 'installed' AND name = 'account'")
            if build_cr.fetchone():
                _logger.debug("Start importing")
                # Launch the account_post_install yaml file
                tools.convert_file(build_cr, 'runbot-custom', 'account_post_install.yml', {})
                build_cr.commit()
                _logger.debug("End importing")
        except:
            _logger.error("Error during chart account installation:\n %s" % traceback.format_exc())
            build.write({'result': 'ko', 'state': 'done'})
            pass

        # Close and restore the new cursor
        build_cr.close()
        threading.current_thread().dbname = cr.dbname
        return

