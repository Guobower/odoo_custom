# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details



# http://sip1.rovoice.com/billing/api/invoices_get?u=admin&from=1483221600&till=1515103200&lang=en


from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
import requests
from urllib2 import Request, urlopen
from lxml import etree
import datetime


class invoice_import_xml(models.TransientModel):
    _name = 'invoice.import.xml'
    _description = "Terrabit Import Invoice From XML"

    server = fields.Selection([('sip1.rovoice.com', 'sip1.rovoice.com'),
                               ('ws.rovoice.com', 'ws.rovoice.com'),
                               ('sip2.rovoice.com', 'sip2.rovoice.com')], string='Server', required=True, )
    from_date = fields.Datetime(string='From Date', required=True, )
    to_date = fields.Datetime(string="To Date", required=True, )
    date_invoice = fields.Date(string="Invoice Date", required=True, )
    user = fields.Char(default='admin', string="User", required=True, )
    lang = fields.Char(default='en', string="Lang", required=True, )
    account_id = fields.Many2one('account.account', string='Account',
                                 required=True, domain=[('deprecated', '=', False)])

    currency_id = fields.Many2one('res.currency')

    def do_import(self):
        headers = {
            "User-Agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)",
            "Content-Type": "application/xml;",
        }
        epoch = datetime.datetime.fromtimestamp(0)
        dt = fields.Datetime.from_string(self.from_date)
        from_date = int((dt - epoch).total_seconds())
        dt = fields.Datetime.from_string(self.to_date)
        to_date = int((dt - epoch).total_seconds())

        cod = 'u=%s&from=%s&till=%s&lang=%s' % (self.user, from_date, to_date, self.lang)
        url = 'http://%s/billing/api/invoices_get?%s' % (self.server, cod)


        #url = 'http://sip1.rovoice.com/billing/api/invoices_get?u=admin&from=1483221600&till=1515103200&lang=en'
        #url = 'http://ws.rovoice.com/billing/api/invoices_get?u=admin&from=1514764800&till=1517011200&lang=en'
        #url = 'http://sip2.rovoice.com/billing/api/invoices_get?u=admin&from=1514764800&till=1517011200&lang=en'

        request = Request(url, headers=headers)
        response = urlopen(request)
        status_code = response.getcode()
        comment = 'Interval : %s - %s' % (self.from_date, self.to_date)

        invoices = self.env['account.invoice']
        if status_code == 200:
            rawfile = response.read()

            dom = etree.fromstring(rawfile)
            dom_invoices = dom.findall('Invoice')
            if not dom_invoices:
                raise Warning(rawfile)


            for dom_invoice in dom_invoices:
                user_id = dom_invoice.get('agreementnumber')
                number = dom_invoice.get('number')

                invoice = self.env['account.invoice'].search([('name', '=', number)])
                if not invoice:
                    customer = self.env['res.partner'].search([('ref', '=', user_id)], limit=1)
                    if not customer:
                        # customer = self.env['res.partner'].create({'ref': user_id, 'name': user_id, 'customer': True})
                        continue
                    values = {'name': number,
                              'partner_id': customer.id,
                              'date_invoice': self.date_invoice,
                              'invoice_line_ids': []}

                    dom_products = dom_invoice.findall('Product')
                    for dom_product in dom_products:
                        name = dom_product.find('Name')
                        product = self.env['product.product'].search([('name', '=', name.text)], limit=1)
                        if not product:
                            product = self.env['product.product'].create({'name': name.text})
                        #quantity = dom_product.find('Quantity')
                        #quantity = 1.0
                        price = dom_product.find('Price').text

                        from_currency = self.currency_id.with_context(date=self.date_invoice)
                        price_unit = from_currency.compute(float(price), self.env.user.company_id.currency_id)

                        account = self.account_id

                        values['invoice_line_ids'] += [(0, 0, {
                            'name': name.text,
                            'product_id': product.id,
                            #'quantity': quantity.text,
                            'price_unit': price_unit,
                            'account_id': account.id,
                            'comment':comment,
                            'invoice_line_tax_ids': [(6, 0, ([rec.id for rec in product.taxes_id]))],
                        })]


                    invoice = self.env['account.invoice'].create(values)
                    invoices |= invoice
        if invoices:
            action = self.env.ref('account.action_invoice_tree1').read()[0]
            action['domain'] = "[('id','in', [" + ','.join(map(str, invoices.ids)) + "])]"
            return action

