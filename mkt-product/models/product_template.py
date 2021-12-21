# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    brand = fields.Char(string='Marque')
    tag_ids = fields.Many2many(
        comodel_name="product.template.tag",
        string="Tags",
        relation="product_template_product_tag_rel",
        column1="product_tmpl_id",
        column2="tag_id",)
    madein_id = fields.Many2one('res.country', string='Made in')
    licensed_id = fields.Many2one('res.partner', string='Licensed')
    composition = fields.Char(string='Composition')
    
    