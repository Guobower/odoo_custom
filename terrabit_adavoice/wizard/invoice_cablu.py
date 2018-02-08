# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details


from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import requests
from urllib2 import Request, urlopen
from lxml import etree
import datetime
from dateutil.relativedelta import relativedelta

class invoice_cablu(models.TransientModel):
    _name = 'invoice.cablu'

    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _description = "Terrabit Import Invoice Cablu"

    from_date = fields.Date(string='From Date', required=True, )
    to_date = fields.Date(string="To Date", required=True, )

    product_id = fields.Many2one('product.product')

    user_id = fields.Many2one('res.user')

    baza = fields.Float()
    pret = fields.Float()
    abonati = fields.Integer()


    @api.model
    def default_get(self, fields_list):
        res = super(invoice_cablu, self).default_get(fields_list)
        today = fields.Date.context_today(self)
        today = fields.Date.from_string(today)

        from_date =  (today + relativedelta(day=01, months=-1, days=0))
        to_date =   (today + relativedelta(day=01, months=0, days=-1))


        res['user_id'] = self.env.user.id
        res['from_date'] = fields.Date.to_string(from_date)
        res['to_date'] = fields.Date.to_string(to_date)
        return res

    @api.multi
    def do_make_pdf(self):
        invoices = self.env['account.invoice'].search([
            ('date_invoice', '>=', self.from_date),
            ('date_invoice', '<=', self.to_date),
            ('state','in',['open','paid'])
        ], )

        abonati = 0.0
        pret = 11
        baza = 0.0

        if invoices:
            lines =  self.env['account.invoice.line'].search([('invoice_id','in',invoices.ids),
                                                              ('product_id','=',self.product_id.id)])


            for line in lines:
                abonati += line.quantity
                baza += line.price_subtotal
        if abonati > 0:
            pret = baza/abonati
        self.write({'baza':baza, 'pret':pret, 'abonati':abonati})
        records = self
        report = self.env['report'].get_action(records, 'terrabit_adavoice.terrabit_invoice_cablu')
        return report


    @api.multi
    def action_send_mail(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.get_object_reference('terrabit_adavoice', 'email_template_cablu')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict()
        ctx.update({
            'default_model': 'invoice.cablu',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
          #  'custom_layout': "sale.mail_template_data_notification_email_sale_order"
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
