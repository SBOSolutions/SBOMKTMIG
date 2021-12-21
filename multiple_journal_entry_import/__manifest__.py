# -*- coding: utf-8 -*-
# Part of VISIOHUB
{
    'name': 'Journal Entries Import - Multiple',
    'version': '1.2',
    'license': 'Other proprietary',
    'summary': """This module allow you to import multiple journal entries from excel file.""",
    'description': """
Odoo Multiple Journal Entry Import.
This module import journal entries from excel file
Journal Entry Import from Excel
Import Journal Items
Import Items
Import journal
journal entry import
import journal
import journal entry odoo
import journal items
journal items import
journal import
journal entries import
import journal entries
opening entry import
opening balance import
partner balance import
journal entry excel import
journal items excel import

    """,
    'author': 'VISIOHUB',
    'category': 'Accounting',
    'depends': [
                'account',
                ],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'wizard/import_excel_wizard.xml',
        'views/import_format_view.xml',
    ],
    'installable': True,
    'application': False,
}
