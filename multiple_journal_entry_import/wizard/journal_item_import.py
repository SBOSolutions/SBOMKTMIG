# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
from datetime import datetime
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class JournalEntryImport(models.TransientModel):
    _name = 'journal.entry.import'
    _description = 'Journal Entry Import'

    files = fields.Binary(
        string="Import Excel File"
    )
    datas_fname = fields.Char(
        'Import File Name'
    )
    company_id = fields.Many2one(
        'res.company',
        required=True,
        string='Company',
    )

    journal_table = fields.Binary(string="Journal Table")
    account_table = fields.Binary(string="Account Table")
    partner_table = fields.Binary(string="Partner Table")
    date_option = fields.Selection([
        ('%Y%m%d', 'YYYYMMDD'), ('%Y%d%m', 'YYYYDDMM'),
        ('%d%m%Y', 'DDMMYYYY'), ('%m%d%Y', 'MMDDYYYY'),
        ('%m-%d-%Y', 'MM-DD-YYYY'), ('%d/%m/%Y', 'DD/MM/YYYY')
    ], string="Date Format", required=True)
    dec_option = fields.Selection([('dot', '.'), ('coma', ',')], string="Decimal Format", required=True)

    def _import_tables(self):
        jn_lst = []
        ac_lst = []
        pt_lst = []
        if self.journal_table:
            try:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.journal_table))
                Sheet_name = workbook.sheet_names()
                sheet = workbook.sheet_by_name(Sheet_name[0])
                number_of_rows = sheet.nrows
                row = 1
                while(row < number_of_rows):
                    ext_name = tools.ustr(sheet.cell(row, 0).value)
                    odoo_name = tools.ustr(sheet.cell(row, 1).value)
                    jn_lst.append((0, 0, {'ext_name': ext_name, 'odoo_name': odoo_name}))
                    row += 1
            except:
                raise ValidationError("Please select .xls/xlsx file...")
        if self.partner_table:
            try:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.partner_table))
                Sheet_name = workbook.sheet_names()
                sheet = workbook.sheet_by_name(Sheet_name[0])
                number_of_rows = sheet.nrows
                row = 1
                while(row < number_of_rows):
                    ext_name = tools.ustr(sheet.cell(row, 0).value)
                    odoo_name = tools.ustr(sheet.cell(row, 1).value)
                    pt_lst.append((0, 0, {'ext_name': ext_name, 'odoo_name': odoo_name}))
                    row += 1
            except:
                raise ValidationError("Please select .xls/xlsx file...")
        if self.account_table:
            try:
                workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.account_table))
                Sheet_name = workbook.sheet_names()
                sheet = workbook.sheet_by_name(Sheet_name[0])
                number_of_rows = sheet.nrows
                row = 1
                while(row < number_of_rows):
                    ext_name = tools.ustr(sheet.cell(row, 0).value)
                    odoo_name = tools.ustr(sheet.cell(row, 1).value)
                    ac_lst.append((0, 0, {'ext_name': ext_name, 'odoo_name': odoo_name}))
                    row += 1
            except:
                raise ValidationError("Please select .xls/xlsx file...")
        if jn_lst or pt_lst or ac_lst:
            self.env['import.format'].create({
                'name': '/',
                'company_id': self.company_id.id,
                'journal_lines': jn_lst,
                'partner_lines': pt_lst,
                'account_lines': ac_lst
            })
        return True

    def journal_item(self):
        self._import_tables()
        item_lines = []
        journal_lists = []
        partner_obj = self.env['res.partner']
        accountmove_obj = self.env['account.move']
        journal_obj = self.env['account.journal']
        accountmove_line_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        analytic_obj = self.env['account.analytic.account']
        currency_obj = self.env['res.currency']
        account_analytic_tag_obj = self.env['account.analytic.tag']
        account_tax_obj = self.env['account.tax']
        try:
            workbook = xlrd.open_workbook(file_contents=base64.decodestring(self.files))
        except:
            print('here')
            raise ValidationError("Please select .xls/xlsx file...")
        Sheet_name = workbook.sheet_names()
        sheet = workbook.sheet_by_name(Sheet_name[0])
        number_of_rows = sheet.nrows

        row = 1
        journal_id = False
        excel_dict = {}
        tags_list = tax_list = []
        # move_lines = []
        move_dict = {}
        format_id = self.env['import.format'].search([('company_id', '=', self.company_id.id)], limit=1)
        journal_lines = format_id.journal_lines
        partner_lines = format_id.partner_lines
        account_lines = format_id.account_lines

        while(row < number_of_rows):

            journal_name = sheet.cell(row, 0).value
            if not journal_name:
                raise ValidationError('Entry Id is not found at row number %s ' % int(row+1))
            journal_code = sheet.cell(row, 3).value
            line = journal_lines.filtered(lambda x: x.ext_name.lower() == journal_code.lower())
            journal = journal_obj.search(['|', ('name', '=', journal_code), ('name', '=', line.odoo_name), ('company_id', '=', self.company_id.id)])
            if not journal:
                raise ValidationError('Journal is not found at row number %s ' % int(row+1))

            journal_ref = sheet.cell(row, 1).value
            if not journal_ref:
                raise ValidationError('Reference is not found at row number %s ' % int(row+1))
            journal_date = sheet.cell(row, 2).value
            if not journal_date:
                raise ValidationError('Date is not found at row number %s ' % int(row+1))

            dt = datetime.strptime(journal_date, self.date_option)

            partner_code = sheet.cell(row, 5).value
            line = partner_lines.filtered(lambda x: x.ext_name.lower() == partner_code.lower())
            partner_domain = [('name', '=', partner_code)]
            if line:
                partner_domain = ['|', ('name', '=', partner_code), ('name', '=', line.odoo_name)]
            partner_id = partner_obj.search(partner_domain, limit=1)

            journal_id = False
            if journal_name in excel_dict:
                journal_id = excel_dict[journal_name]
                journal_lists.append(journal_id.id)
            else:
                journal_entry_vals = {
                    'journal_id': journal.id,
                    'date': dt.strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'ref': journal_ref,
                    'company_id': self.company_id.id,
                    'partner_id': partner_id.id,
                }

                journal_id = accountmove_obj.create(journal_entry_vals)
                excel_dict.update({journal_name: journal_id})
                journal_lists.append(journal_id.id)
            account_code = tools.ustr(sheet.cell(row, 4).value)
            line = account_lines.filtered(lambda x: x.ext_name.lower() == account_code.lower())
            account_id = account_obj.search(['|', ('code', '=', account_code), ('code', '=', line.odoo_name)])
            if not account_id:
                raise ValidationError('Account Code is not found at row number %s ' % int(row+1))

            analytic_id = analytic_obj.search([('name', '=', sheet.cell(row, 7).value)])

            cur = tools.ustr(sheet.cell(row, 10).value)
            currency_id = currency_obj.search([('name', '=', cur)])
            if not currency_id:
                raise ValidationError('Currency is not found at row number %s ' % int(row+1))
            if not sheet.cell(row, 6).value:
                raise ValidationError('Label is not found at row number %s ' % int(row+1))
            if not sheet.cell(row, 11).value:
                if not (sheet.cell(row, 11).value == 0):
                    raise ValidationError('Debit Amount is not found at row number %s ' % int(row+1))
            if not sheet.cell(row, 12).value:
                if not (sheet.cell(row, 12).value == 0):
                    raise ValidationError('Credit Amount is not found at row number %s ' % int(row+1))
            date_maturity = str(sheet.cell(row, 13).value)
            date_maturity = date_maturity.split('.')[0] if '.' in date_maturity else date_maturity
            dt = datetime.strptime(date_maturity, self.date_option)

            #analytic tags
            tags_value = sheet.cell(row, 8).value
            amount_curr = sheet.cell(row, 9).value
            tags_list = tags_value.split(',')
            tag_ids = account_analytic_tag_obj.search([('name', 'in', tags_list)])

            #tax ids
            tax_value = sheet.cell(row, 14).value
            tax_list = tax_value.split(',')
            tax_ids = account_tax_obj.search([('name', 'in', tax_list)])

            debit = sheet.cell(row, 11).value
            credit = sheet.cell(row, 12).value
            if self.dec_option == 'coma':
                debit = str(debit).replace(',', '.')
                credit = str(credit).replace(',', '.')
                amount_curr = str(amount_curr).replace(',', '.')

            if journal_id:
                vals = {
                    'account_id': account_id.id,
                    'partner_id': partner_id.id,
                    'name': sheet.cell(row, 6).value,
                    'analytic_account_id': analytic_id.id,
                    'amount_currency': float(amount_curr) if amount_curr else 0.0,
                    'currency_id': currency_id.id if currency_id.id != self.company_id.currency_id.id else False,
                    'debit': float(debit),
                    'credit': float(credit),
                    'date_maturity': dt.strftime(DEFAULT_SERVER_DATE_FORMAT),
                    'ref': journal_ref,
                    # 'date' : create_date,
                    # 'move_id': journal_id.id,
                    'analytic_tag_ids': [(6, 0, tag_ids.ids)],
                    'tax_ids': [(6, 0, tax_ids.ids)],
                    }
                # journal_id.write()
                # account_move_line = accountmove_line_obj.create(vals)

                if journal_id not in move_dict:
                    move_dict[journal_id] = [(0, 0, vals)]
                else:
                    move_dict[journal_id].append((0, 0, vals))

                row = row + 1
        if move_dict:
            for move in move_dict:
                move.write({'line_ids': move_dict[move]})
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['domain'] = [('id', 'in', journal_lists)]
        action['context'] = {}
        return action

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
