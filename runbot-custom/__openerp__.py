# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright Eezee-It
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
{
    "name": "Runbot Custom",
    "version": "0.1",
    "author": "Eezee-It",
    "category": "Base",
    "website": "http://www.eezee-it.com",
    "description": "When using a profile loading the company country, if you install this module, "
                   "(Put after the profile installation)"
                   "it will install the country chart of account",
    "depends": ["base","runbot"],
    "init_xml": [],
    "demo_xml": [],
    "data": [
        'res_config_view.xml',
        'runbot_repo.xml',
    ],
    "active": False,
    "installable": True
}