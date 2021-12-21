# -*- coding: utf-8 -*-
{
    'name': "mkt-invoice",

    'summary': """
        extend account move model report""",

    'description': """
       extend account move model report link, with OCA addon
    """,

    'author': "SBO Solutions",
    'website': "https://www.sbosolutions.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'stock_picking_invoice_link'],

    # always loaded
    'data': [
        'report/account_move.xml'
    ],
}
