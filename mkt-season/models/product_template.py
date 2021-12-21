# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    season_id = fields.Many2one(string='Season',comodel_name='res.season',ondelete='restrict',)
    