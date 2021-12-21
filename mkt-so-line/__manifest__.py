# -*- coding: utf-8 -*-
{
    'name': "mkt-so-line",

    'summary': """
        extend sales order / purchase order lines view""",

    'description': """
        extend sales order / purchase order lines view,
    """,

    'author': "SBO Solutions",
    'website': "https://www.sbosolutions.fr",

    # for the full list
    'category': '',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'purchase'],

    # always loaded
    'data': [
        'views/sale_order_line_view.xml',
        'views/sale_order.xml',
        'views/purchase_order.xml',
        'views/purchase_order_line_view.xml'
    ],
}
