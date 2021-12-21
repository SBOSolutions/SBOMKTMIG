# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'mail.activity.type'

    ref = fields.Char(string='Référence interne')