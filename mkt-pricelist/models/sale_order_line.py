# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    def _get_recommended_selling_price(self):
        for record in self:
            search_more = True
            # case 1 search product + company_id
            for price_list_item in record.env['product.pricelist.item'].search([('company_id', '=', record.company_id.id), ('product_tmpl_id', '=', record.product_template_id.id)]):
                record.recommended_selling_price = price_list_item.recommended_selling_price

            if not record.recommended_selling_price:
                record.recommended_selling_price = 0
                
    recommended_selling_price = fields.Float('Recommended Selling Price', digits='Product Price', compute='_get_recommended_selling_price', check_company=True)