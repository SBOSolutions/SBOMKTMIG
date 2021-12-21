# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'sale.order.line'

    product_template_ref = fields.Char(string='Template article', related='product_id.product_tmpl_id.name')
    product_template_tags = fields.Many2many('product.template.attribute.value', related='product_id.product_template_attribute_value_ids')
