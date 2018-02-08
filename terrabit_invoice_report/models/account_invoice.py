# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2018 Terrabit All Rights Reserved
#                    Terrabit <danila(@)terrabit(.)ro
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
from odoo import models, fields, api
class account_invoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def get_currencies(self):
        currencies = self.env['res.currency'].search([('active', '=', True)])
        return currencies
    def get_banks(self):
        accounts = self.env['account.journal'].search([('display_on_footer', '=', True),('type','=','bank')])
        return accounts