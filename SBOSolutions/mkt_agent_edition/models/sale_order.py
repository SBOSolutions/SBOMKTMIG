# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    ref_cmd = fields.Char('Référence Livraison Commande')

    def _get_matrix(self, product_template, is_for_report= False):
        """Return the matrix of the given product, updated with current SOLines quantities.

        :param product.template product_template:
        :return: matrix to display
        :rtype dict:
        """
        def has_ptavs(line, sorted_attr_ids):
            # TODO instead of sorting on ids, use odoo-defined order for matrix ?
            ptav = line.product_template_attribute_value_ids.ids
            pnav = line.product_no_variant_attribute_value_ids.ids
            pav = pnav + ptav
            pav.sort()
            return pav == sorted_attr_ids
        matrix = product_template._get_template_matrix(
            company_id=self.company_id,
            currency_id=self.currency_id,
            display_extra_price=True)
        if self.order_line:
            lines = matrix['matrix']
            order_lines = self.order_line.filtered(lambda line: line.product_template_id == product_template) 
            if is_for_report:
                matrix['product_tmpl_id'] = order_lines.product_template_id.id
                matrix['picture'] = order_lines.product_template_id.image_128
            for line in lines:
                for cell in line:
                    if not cell.get('name', False):
                        line = order_lines.filtered(lambda line: has_ptavs(line, cell['ptav_ids']))
                        if line:
                            cell.update({
                                'qty': int(sum(line.mapped('product_uom_qty'))),
                                'total_price': line.price_subtotal
                            })
 
        if is_for_report:
            matrix['header'][0]['name'] = ''
            if self.partner_id and self.partner_id.property_account_position_id:
                if self.partner_id.property_account_position_id.is_out_eu:
                    matrix['header'][0]['name'] = 'Code douanier • 0000000000 Made in France'
            matrix['header'].append({'name': ''})

        elem_list_position = []

        # Patch add total_qty from matrix
        cpt = 0
        for element in matrix['matrix']:
            total_qty = 0
            for dict_item in element:
                if not dict_item.get('name', False) and dict_item.get('qty', False):
                    total_qty += dict_item['qty']

            if total_qty == 0:
                elem_list_position.append(cpt)
            if is_for_report:
                element.append({'total_qty': total_qty, 'is_last': True})
            cpt += 1

        if elem_list_position:
            elem_list_position = sorted(elem_list_position, reverse=True)

        if is_for_report:
            for index in elem_list_position:
                del matrix['matrix'][index]

        return matrix
    
    def check_is_0(self,line):
        i = 0
        nb_cell = 0
        for cell in line:
            if not cell.get('name', False):
                nb_cell += 1
                if cell.get('qty') == 0:
                    i += 1
        if i == nb_cell:
            return True

    def get_report_matrixes(self):
        """Reporting method.

        :return: array of matrices to display in the report
        :rtype: list
        """
        matrixes = []
        if self.report_grids:
            grid_configured_templates = self.order_line.filtered('is_configurable_product').product_template_id.filtered(lambda ptmpl: ptmpl.product_add_mode == 'matrix')
            for template in grid_configured_templates:
                if len(self.order_line.filtered(lambda line: line.product_template_id == template)) > 0:
                    # TODO do we really want the whole matrix even if there isn't a lot of lines ??
                    matrixes.append(self._get_matrix(template, True))
                    for matrix in matrixes:
                        for line in matrix['matrix']:
                            if self.check_is_0(line):
                                line.clear()
        return matrixes

    def exist_table_with_no_matrix(self):
        if self.order_line.filtered(lambda l: l.product_template_id.product_add_mode != 'matrix'):
            return True
        return False


