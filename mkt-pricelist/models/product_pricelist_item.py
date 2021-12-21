# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductPricelistItemInherit(models.Model):
    _inherit = 'product.pricelist.item'

    recommended_selling_price = fields.Float('Recommended Selling Price', digits='Product Price', check_company=True)