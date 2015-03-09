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
from openerp.osv import osv
import os
import time
import openerp

def grep(filename, string):
    if os.path.isfile(filename):
        return open(filename).read().find(string) != -1
    return False

def now():
    return time.strftime(openerp.tools.DEFAULT_SERVER_DATETIME_FORMAT)

class RunbotBuild(osv.osv):
    _inherit = "runbot.build"

    def job_10_test_base(self, cr, uid, build, lock_path, log_path):
        disable_job = self.pool.get('ir.config_parameter').get_param(cr, uid, 'runbot.disable_job_10', default='True')
        if disable_job == 'True':
            return
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
        build._log('test_chart_account', 'Start install chart account')

        db = openerp.sql_db.db_connect('%s-all' % build.dest)
        threading.current_thread().dbname = '%s-all' % build.dest
        build_cr = db.cursor()

        try:
            build_cr.execute("SELECT id FROM ir_module_module WHERE state = 'installed' AND name = 'account'")
            if build_cr.fetchone():
                print 'Start importing'
                tools.convert_file(build_cr, 'runbot-custom', 'account_post_install.yml', {})
                build_cr.commit()
                print 'End importing'
        except:
            build.write({'result': 'ko', 'state': 'done'})
            pass

        build_cr.close()
        threading.current_thread().dbname = cr.dbname
        return