# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrderLineInherit(models.Model):
    _inherit = 'purchase.order.line'

    product_template_id = fields.Many2one('product.template', string='id template article', store=True, related='product_id.product_tmpl_id')
