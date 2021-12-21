# -*- coding: utf-8 -*-
{
    'name': "mkt-stock",

    'summary': """
        extend stock related""",

    'description': """
       extend stock related
    """,

    'author': "SBO Solutions",
    'website': "https://www.sbosolutions.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'security/account_security.xml',
        'views/stock_picking_view.xml',
        'report/stock_report_views.xml',
        'data/stock_picking_email_template.xml',
    ],
}
