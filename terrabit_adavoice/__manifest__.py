# -*- coding: utf-8 -*-
# ©  2018 Terrabit
# See README.rst file on addons root folder for license details

{
    "name": "Deltatech Ada Voice",
    "version": "1.0",
    "author": "Dorin Hongu",
    "website": "",
    "description": """
    
Ajustari:
--------- 
http://wiki.kolmisoft.com/index.php/Main_Page

       
    """,

    "category": "Generic Modules",
    "depends": ['account'],

    "data": [
        'wizard/invoice_import_xml_view.xml',
        'wizard/invoice_cablu_view.xml',
        'views/cablu_template.xml',
        'data/mail_template_data.xml'
    ],

    "active": False,
    "installable": True,
    'application': True,
}


