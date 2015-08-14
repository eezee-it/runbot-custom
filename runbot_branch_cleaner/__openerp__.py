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
{
    "name": "Runbot Branch Cleaner",
    "version": "0.1",
    "author": "Eezee-It",
    "category": "runbot",
    "website": "http://www.eezee-it.com",
    "description": """
    This module helps you to keep yours repo clean.

    Each day, the module will look for old branches and/or for old tags.
    Theses tags/branches will be deleted.
    """,
    "depends": ["base", "runbot"],
    "init_xml": [],
    "demo_xml": [],
    "data": [
        'runbot_repo.xml'
    ],
    "active": False,
    "installable": True
}