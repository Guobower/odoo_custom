# -*- coding: utf-8 -*-
# ©  2017 Terrabit
# See README.rst file on addons root folder for license details
{
    "name": "Terrabit Invoice Print",
    'version': '10.0.1.0.0',
    "author": "Terrabit, Dan Stoica",
    "website": "www.terrabit.ro",
    "description": """

Functionalitati:
----------------

 - Tiparirea facturii conform legislatiei
    - mosteneste account.report_invoice
    - varianta de tiparire in engleza
 
 - Print invoice according to romanian legislation
    - inherits account.report_invoice
    - english print

    """,
    "category": "Accounting",
    "depends": ['account', 'sale','l10n_ro_config','l10n_ro_invoice_report'],

    "data": [ 'views/report_invoice.xml'],
    "active": False,
    "installable": True,
}
