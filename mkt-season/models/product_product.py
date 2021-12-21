# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.osv import expression
import re

class ProductProduct(models.Model):
    _inherit = 'product.product'


    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     res = super(ProductProduct, self)._name_search(
    #         name, args=None, operator='ilike', limit=100, name_get_uid=None)
    #     import pdb; pdb.set_trace()
    #     if name:
    #         positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
    #         if operator in positive_operators:
    #             product_template_attribute_value_ids = self.env['product.template.attribute.value'].search([
    #                 ('name', 'ilike', name)
    #             ]).ids
    #             if product_template_attribute_value_ids:
    #                 product_ids = list(self._search(
    #                     [('product_template_attribute_value_ids', 'in', product_template_attribute_value_ids)
    #                      ] + args, limit=limit, access_rights_uid=name_get_uid))
    #                 res.extend(product_ids)
    #     return res
