# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ImportFormat(models.Model):
    _name = 'import.format'
    _description = 'Import Format'

    name = fields.Char(required=True, default='/')
    company_id = fields.Many2one('res.company', 'Company', required=True,)
    journal_lines = fields.One2many('journal.line', 'format_id', 'Journal Lines')
    partner_lines = fields.One2many('partner.line', 'format_id', 'Partner Lines')
    account_lines = fields.One2many('account.line', 'format_id', 'Account Lines')

    @api.model
    def create(self, vals):
        if vals.get('name') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('import.format')
        res = super(ImportFormat, self).create(vals)
        return res


class JournalLine(models.Model):
    _name = 'journal.line'
    _description = 'Journal Line'

    ext_name = fields.Char(required=True)
    odoo_name = fields.Char(required=True)
    format_id = fields.Many2one('import.format', 'Format', ondelete="cascade")

class PartnerLine(models.Model):
    _name = 'partner.line'
    _description = 'Partner Line'

    ext_name = fields.Char(required=True)
    odoo_name = fields.Char(required=True)
    format_id = fields.Many2one('import.format', 'Format', ondelete="cascade")

class AccountLine(models.Model):
    _name = 'account.line'
    _description = 'Account Line'

    ext_name = fields.Char(required=True)
    odoo_name = fields.Char(required=True)
    format_id = fields.Many2one('import.format', 'Format', ondelete="cascade")
