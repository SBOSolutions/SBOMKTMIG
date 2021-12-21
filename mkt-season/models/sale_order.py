# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    season_id = fields.Many2one(string='Season',comodel_name='res.season',ondelete='restrict',)
    