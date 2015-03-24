# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright Eezee-it
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
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import openerp.tools as tools
import threading
import traceback
import os
import time
import openerp
import logging
from openerp import SUPERUSER_ID
from openerp.addons.runbot.runbot import RunbotController
from openerp.fields import Boolean
from openerp.models import Model, api

_logger = logging.getLogger(__name__)


def grep(filename, string):
    if os.path.isfile(filename):
        return open(filename).read().find(string) != -1
    return False

def now():
    return time.strftime(openerp.tools.DEFAULT_SERVER_DATETIME_FORMAT)

class RunbotRepo(Model):
    _inherit = 'runbot.repo'

    install_chart_account = Boolean('Install the chart account', default=True,
                                    help="Install the chart account according the country of the company")

class RunbotBuild(Model):
    _inherit = "runbot.build"

    disable_base_log = Boolean('Disable Base Log')

    def job_10_test_base(self, cr, uid, build, lock_path, log_path):
        disable_job = self.pool.get('ir.config_parameter').get_param(cr, uid, 'runbot.disable_job_10', default='True')
        if disable_job == 'True':
            _logger.info('Job 10 disable')
            print build
            self.write(cr, SUPERUSER_ID, build.id, {'disable_base_log': True})
            build.checkout()
            return
        _logger.info('Job 10 enable')
        super(RunbotBuild, self).job_10_test_base(cr, uid, build, lock_path, log_path)

    def job_15_install_all(self, cr, uid, build, lock_path, log_path):
        build._log('install_all', 'Start install all modules')
        self.pg_createdb(cr, uid, "%s-all" % build.dest)
        cmd, mods = build.cmd()
        if grep(build.server("tools/config.py"), "test-enable"):
            cmd.append("--test-enable")
        cmd += ['-d', '%s-all' % build.dest, '-i', mods, '--without-demo=all', '--stop-after-init', '--log-level=test', '--max-cron-threads=0']
        # reset job_start to an accurate job_20 job_time
        build.write({'job_start': now()})
        return self.spawn(cmd, lock_path, log_path, cpu_limit=2100)

    def job_20_test_all(self, cr, uid, build, lock_path, log_path):
        build._log('test_all', 'Start test all modules')
        cmd, mods = build.cmd()
        if grep(build.server("tools/config.py"), "test-enable"):
            cmd.append("--test-enable")
        cmd += ['-d', '%s-all' % build.dest, '-i', mods, '--stop-after-init', '--log-level=test', '--max-cron-threads=0']
        # reset job_start to an accurate job_20 job_time
        build.write({'job_start': now()})
        return self.spawn(cmd, lock_path, log_path, cpu_limit=2100)

    def job_25_install_chart_account(self, cr, uid, build, lock_path, log_path):
        # Check if this job must be ignored
        if not build.repo_id.install_chart_account:
            _logger.debug("Ignore chart account installation")
            return

        build._log('test_chart_account', 'Start install chart account')

        db = openerp.sql_db.db_connect('%s-all' % build.dest)
        threading.current_thread().dbname = '%s-all' % build.dest
        build_cr = db.cursor()

        try:
            build_cr.execute("SELECT id FROM ir_module_module WHERE state = 'installed' AND name = 'account'")
            if build_cr.fetchone():
                _logger.debug("Start importing")
                tools.convert_file(build_cr, 'runbot-custom', 'account_post_install.yml', {})
                build_cr.commit()
                _logger.debug("End importing")
        except:
            _logger.error("Error during chart account installation:\n %s" % traceback.format_exc())
            build.write({'result': 'ko', 'state': 'done'})
            pass

        build_cr.close()
        threading.current_thread().dbname = cr.dbname
        return

class Controller(RunbotController):
    def build_info(self, build):
        real_build = build.duplicate_id if build.state == 'duplicate' else build

        result = super(Controller, self).build_info(build)
        result['disable_base_log'] = real_build.disable_base_log

        return result
