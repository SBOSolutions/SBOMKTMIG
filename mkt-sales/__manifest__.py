# -*- coding: utf-8 -*-
{
    'name': "mkt-sales",

    'summary': """
        extend sales related (contact, price, crm) views and models""",

    'description': """
       extend sales related (contact, price, crm) views and models
    """,

    'author': "SBO Solutions",
    'website': "https://www.sbosolutions.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'crm', 'contacts', 'sale_management',],

    # always loaded
    'data': [
        'views/crm_team_views.xml',
        'views/res_partner_views.xml',
        'views/res_users_view.xml',
        'views/mail_layout_template.xml',
        'views/sale_order_views.xml',
    ],
}
