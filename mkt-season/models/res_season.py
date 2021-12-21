# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResSeason(models.Model):
    _name = 'res.season'
    _description = "season model management"

    name = fields.Char(string='Saison')
    product_count = fields.Integer(
        '# Products', compute='_compute_product_count',
        help="The number of products under this season")
    
    def _compute_product_count(self):
        product_data = self.env['product.template'].read_group([('season_id', 'in', self.ids)], ['season_id'], ['season_id'])
        data = {product['season_id'][0]: product['season_id_count'] for product in product_data}
        for season in self:
            season.product_count = data.get(season.id, 0)