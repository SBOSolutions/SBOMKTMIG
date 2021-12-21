{
	'name': 'MKT Installment Option for Sale',

	'summary': '''Payment Installment option -  In this module, Payment Installment option has been added for Sale.
	and completly refactor and adapt for MKT needs bu SBO Solutions - Module from Techspawn Solutions''',

	'description': '''This module helps to manage installment payments in Odoo. ''',

	'author': "Techspawn Solutions - fork and refactor by SBO Solutions",
	'website': "https://www.sbo-solutions.fr",

	'version': '14.0.0.2',
	'license': "OPL-1",
	#'currency': 'USD',
	#'price': 39.00,

	'depends': ['base', 'sale', 'account', 'sale_management', 'stock', 'mail'],

	'data': ['security/ir.model.access.csv',
			'views/sale_views.xml',
			'views/invoice_views.xml',
			'views/sale_report.xml',
			'views/invoice_report.xml',
			'views/stock_picking.xml',
			'views/payment_term.xml',
   			'data/mail_template.xml',
			'views/res_company.xml',
	],
	'images':['static/description/main.gif'
	 ],
}
