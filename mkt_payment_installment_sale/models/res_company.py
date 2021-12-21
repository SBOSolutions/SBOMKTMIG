# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResCompanyInherit(models.Model):
    _inherit = 'res.company'

    journal_PLF_id = fields.Many2one('account.journal', string='Journal PF')
