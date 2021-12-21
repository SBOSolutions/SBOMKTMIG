# -*- coding: utf-8 -*-
{
    'name': "mkt-product",

    'summary': """
        extend the product views and models""",

    'description': """
       extend the product views and models
    """,

    'author': "SBO Solutions",
    'website': "https://www.sbosolutions.fr",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': '',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product', 'purchase','mkt-season'],

    # always loaded
    'data': [
        'data/mail_activity_data.xml',
        'security/ir.model.access.csv',
        'security/product_template_rule.xml',
        'security/product_template_tag.xml',
        'views/product_product.xml',
        'views/product_template.xml',
        'views/product_template_tags.xml',
        'wizard/delete_lines_in_so.xml',
        'views/mail_activity_view.xml'
    ],
}
