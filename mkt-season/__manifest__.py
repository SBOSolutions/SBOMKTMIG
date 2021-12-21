# -*- coding: utf-8 -*-
{
    'name': "mkt-season",

    'summary': """
        extend sales related (contact, price, crm) views and models""",

    'description': """
       extend sales related (contact, price, crm) views and models
    """,

    'author': "CTO IT Consulting",
    'website': "https://www.cto-it-consulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '14.0.0.2',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'sale_management',],

    # always loaded
    'data': [
        # security
        'security/ir.model.access.csv',
        # views
        'views/sale_order_views.xml',
        'views/product_template.xml',
        'views/season.xml',
    ],
}
