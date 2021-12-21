# -*- coding: utf-8 -*-
# Part of Probuse Consulting Service Pvt. Ltd. See LICENSE file for full copyright and licensing details.

import base64
import xlrd
from odoo import tools
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class JournalEntryImport(models.TransientModel):

    _name = 'journal.entry.import'
    
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

    journal_map = fields.Boolean(string="Journal Mapping")
    account_map = fields.Boolean(string="Account Mapping")
    partner_map = fields.Boolean(string="Partner Mapping")

    @api.multi
    def journal_item(self):
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
        while(row < number_of_rows):
            journal_name = sheet.cell(row, 0).value
            if not journal_name:
                raise ValidationError('Entry Id is not found at row number %s ' % int(row+1))
            jn_domain = [('company_id', '=', self.company_id.id)]
            cell_no = 4
            if self.journal_map:
                jn_domain += ['|', ('code', '=', sheet.cell(row, 3).value), ('name', '=', sheet.cell(row, 4).value)]
                cell_no = 5
            else:
                jn_domain += [('name', '=', sheet.cell(row, 3).value)]
            journal = journal_obj.search(jn_domain)
            if not journal:
                raise ValidationError('Journal is not found at row number %s ' % int(row+1))
            journal_ref = sheet.cell(row, 1).value
            if not journal_ref:
                raise ValidationError('Reference is not found at row number %s ' % int(row+1))
            journal_date = sheet.cell(row, 2).value
            if not journal_date:
                raise ValidationError('Date is not found at row number %s ' % int(row+1))

            journal_id = False
            if journal_name in excel_dict:
                journal_id = excel_dict[journal_name]
                journal_lists.append(journal_id.id)
            else:
                journal_entry_vals = {
                    'journal_id': journal.id,
                    'date': journal_date,
                    'ref': journal_ref,
                    'company_id': self.company_id.id
                }

                journal_id = accountmove_obj.create(journal_entry_vals)
                excel_dict.update({journal_name: journal_id})
                journal_lists.append(journal_id.id)

            acc_domain = []
            part_cell = 5
            codev1 = tools.ustr(sheet.cell(row, cell_no).value)
            if self.account_map:
                codev2 = tools.ustr(sheet.cell(row, cell_no+1).value)
                acc_domain += ['|', ('code', '=', codev1), ('code', '=', codev2)]
                part_cell = 7
            else:
                acc_domain += [('code', '=', codev1)]
            account_id = account_obj.search(acc_domain)

            if not account_id:
                raise ValidationError('Account Code is not found at row number %s ' % int(row+1))
            part_domain = []
            cell_no = 7
            if self.partner_map:
                part_domain += ['|', ('name', '=', sheet.cell(row, part_cell).value), ('name', '=', sheet.cell(row, part_cell + 1).value)]
                cell_no = 9
            else:
                part_domain += []
            partner_id = partner_obj.search([('name', '=', sheet.cell(row, part_cell).value)])
            analytic_id = analytic_obj.search([('name', '=', sheet.cell(row, cell_no+1).value)])

            cur = tools.ustr(sheet.cell(row, cell_no+4).value)
            currency_id = currency_obj.search([('name', '=', cur)])
            if not currency_id:
                raise ValidationError('Currency is not found at row number %s ' % int(row+1))
            if not sheet.cell(row, cell_no).value:
                raise ValidationError('Label is not found at row number %s ' % int(row+1))
            if not sheet.cell(row, cell_no+5).value:
                if not (sheet.cell(row, cell_no+5).value == 0):
                    raise ValidationError('Debit Amount is not found at row number %s ' % int(row+1))
            if not sheet.cell(row, cell_no+6).value:
                if not (sheet.cell(row, cell_no+6).value == 0):
                    raise ValidationError('Credit Amount is not found at row number %s ' % int(row+1))
            date_maturity = sheet.cell(row, cell_no+7).value

            #analytic tags
            tags_value = sheet.cell(row, cell_no+2).value
            tags_list = tags_value.split(',')
            tag_ids = account_analytic_tag_obj.search([('name', 'in', tags_list)])

            #tax ids
            tax_value = sheet.cell(row, cell_no+8).value
            tax_list = tax_value.split(',')
            tax_ids = account_tax_obj.search([('name', 'in', tax_list)])

            if journal_id:
                vals = {
                    'account_id': account_id.id,
                    'partner_id': partner_id.id,
                    'name': sheet.cell(row, cell_no).value,
                    'analytic_account_id': analytic_id.id,
                    'amount_currency': sheet.cell(row, cell_no+3).value,
                    'currency_id': currency_id.id,
                    'debit': sheet.cell(row, cell_no+5).value,
                    'credit': sheet.cell(row, cell_no+6).value,
                    'date_maturity': date_maturity,
                    'ref': journal_ref,
                    # 'date': create_date,
                    # 'move_id': journal_id.id,
                    'analytic_tag_ids': [(6, 0, tag_ids.ids)],
                    'tax_ids': [(6, 0, tax_ids.ids)],
                    }

#                 journal_id.write()
#                 account_move_line = accountmove_line_obj.create(vals)

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
