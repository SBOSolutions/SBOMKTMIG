# -*- coding: utf-8 -*-
{
    'name': "report_matrix",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Webedoo",
    'website': "https://www.webdoo.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale_management', 'sale_product_matrix', 'purchase_product_matrix', 'account', 'mkt-pricelist'],

    # always loaded
    'data': [
        'views/assets_backend.xml',
        'reports/matrix_templates.xml',
        'reports/sale_order_report.xml',
        'reports/purchase_order_report.xml',
        'reports/purchase_quotation_report.xml',
        'reports/account_move_report.xml',
        'reports/external_layout_standard.xml',
        'views/sale_order.xml',
        'views/account_fiscal_position.xml',
    ],
}
