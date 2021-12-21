# -*- coding: utf-8 -*-

from odoo import models, fields, api
import itertools



class ProductTemplate(models.Model):
    _inherit = 'product.template'

    display_stock_matrice = fields.Selection(
        string='Choice the stock to display',
        selection=[('available', 'available'), ('virtual', 'vitual')],        
    )

    def _get_template_matrix(self, **kwargs):
        self.ensure_one()
        company_id = kwargs.get('company_id', None) or self.company_id or self.env.company
        currency_id = kwargs.get('currency_id', None) or self.currency_id
        display_extra = kwargs.get('display_extra_price', False)
        dispay_stock = kwargs.get('stock_display', False)
        attribute_lines = self.valid_product_template_attribute_line_ids

        Attrib = self.env['product.template.attribute.value']
        first_line_attributes = attribute_lines[0].product_template_value_ids._only_active()
        attribute_ids_by_line = [line.product_template_value_ids._only_active().ids for line in attribute_lines]

        header = [
            {
                "name": self.display_name,
            }
            ] + [
            attr._grid_header_cell(
                fro_currency=self.currency_id,
                to_currency=currency_id,
                company=company_id,
                display_extra=display_extra
            ) for attr in first_line_attributes]

        result = [[]]
        for pool in attribute_ids_by_line:
            result = [x + [y] for y in pool for x in result]
        args = [iter(result)] * len(first_line_attributes)
        rows = itertools.zip_longest(*args)

        matrix = []
        for row in rows:

            row_attributes = Attrib.browse(row[0][1:])
            row_header_cell = row_attributes._grid_header_cell(
                fro_currency=self.currency_id,
                to_currency=currency_id,
                company=company_id,
                display_extra=display_extra)
            result = [row_header_cell]
            for cell in row:
                combination = Attrib.browse(cell)
                product_id = self._get_variant_id_for_combination(combination)
                product = self.env['product.product'].browse(product_id)
                is_possible_combination = self._is_combination_possible(combination)
                cell.sort()
                result.append({
                        "ptav_ids": cell,
                        "qty": 0,
                        "qty_available": product.qty_available,
                        "virtual_available": product.virtual_available,
                        "is_possible_combination": is_possible_combination
                    })
            matrix.append(result)
        return {
            "header": header,
            "matrix": matrix,
        }
