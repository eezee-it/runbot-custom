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

from openerp.models import TransientModel, api, Model
from openerp.exceptions import Warning
import logging
import os

_logger = logging.getLogger(__name__)


class RunbotRepo(Model):
    _inherit = 'runbot.repo'

    @api.multi
    def clean_branches(self):
        """
        This method will delete old branches or tags
        """
        branch = self.env['runbot.branch']
        build = self.env['runbot.build']

        for repo in self:
            if not os.path.isdir(os.path.join(repo.path)):
                os.makedirs(repo.path)
            if not os.path.isdir(os.path.join(repo.path, 'refs')):
                run(['git', 'clone', '--bare', repo.name, repo.path])
            else:
                # We fetch all the branches
                repo.git(['fetch', '-p', 'origin', '+refs/heads/*:refs/heads/*'])
                if repo.hosting == 'github':
                    # In the case where we use the Github Hosting, we can have
                    # the pull request in the references of Git.
                    repo.git(['fetch', '-p', 'origin', '+refs/pull/*/head:refs/pull/*'])
                # We fetch all the tags
                repo.git(['fetch', '-p', 'origin', '+refs/tags/*:refs/tags/*'])

            git_refs = repo.git([
                'for-each-ref', '--format', '%(refname)',
                'refs/heads', 'refs/pull', 'refs/tags'
            ])
            git_refs = git_refs.strip()

            branch_name_list = git_refs.split('\n')
            branch_recs = branch.search([('name', 'not in', branch_name_list), ('repo_id', '=', repo.id)])
            branch_ids = [branch.id for branch in branch_recs]
            branch_names = [branch.name for branch in branch_recs]
            _logger.info('Useless branch find for the repo %s %s', repo.name, branch_names)

            build_to_kill = build.search([('branch_id', 'in', branch_ids), ('pid', '!=', 0)])
            build_to_kill.kill()
            _logger.info('%s builds killed', len(build_to_kill))
            build_to_remove = build.search([('branch_id', 'in', branch_ids)])
            build_to_remove.unlink()
            _logger.info('%s builds removed', len(build_to_remove))

            branch_recs.unlink()
            _logger.info('%s branches removed', len(branch_recs))

    @api.model
    def cron_clean_branches(self):
        """
        Method called by the Cron
        """
        all_branch = self.search([])
        all_branch.clean_branches()