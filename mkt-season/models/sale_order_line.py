# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderline(models.Model):
    _inherit = 'sale.order.line'

    season = fields.Char(related='product_id.season_id.name')