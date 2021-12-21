# -*- coding: utf-8 -*-

from odoo import api, fields, models


class AccountMoveLineInherit(models.Model):
    _inherit = 'account.move.line'

    product_template_id = fields.Many2one('product.template', string='Template de produit', store=True, related='product_id.product_tmpl_id')
    is_configurable_product = fields.Boolean('Is the product configurable?', related="product_template_id.has_configurable_attributes")
    product_template_attribute_value_ids = fields.Many2many(related='product_id.product_template_attribute_value_ids', readonly=True)
    product_no_variant_attribute_value_ids = fields.Many2many('product.template.attribute.value', string="Extra Values", ondelete='restrict')
