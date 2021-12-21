# -*- coding: utf-8 -*-
{
    'name': "mkt-web-lcr",

    'summary': """
        extend lcr payment option""",

    'description': """
       extend lcr payment option
    """,

    'author': "SBO Solutions",
    'website': "https://www.sbosolutions.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Website/Website',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'website_sale'],

    # always loaded
    'data': [
        'views/payment_template.xml',
        'views/res_partner.xml',
        'views/lcr_form_view.xml',
        'data/payment_mkt_web_data.xml',
    ],
}
