# -*- coding: utf-8 -*-

from odoo import models, fields, api



class SaleOrder(models.Model):
    _inherit = 'sale.order'

    display_stock_matrice = fields.Selection(
        string='Choice the stock to display',
        selection=[('available', 'available'), ('virtual', 'virtual')],
        default='available'
    )
    
    @api.onchange('grid_product_tmpl_id', 'display_stock_matrice')
    def _set_grid_up(self):
        """Save locally the matrix of the given product.template, to be used by the matrix configurator."""
        return super(SaleOrder, self)._set_grid_up()

    def _get_matrix(self, product_template):
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
            display_extra_price=True,
            stock_display=self.display_stock_matrice)
        import pdb; pdb.set_trace()
        if self.order_line:
            lines = matrix['matrix']
            order_lines = self.order_line.filtered(lambda line: line.product_template_id == product_template)
            for line in lines:
                for cell in line:
                    if not cell.get('name', False):
                        line = order_lines.filtered(lambda line: has_ptavs(line, cell['ptav_ids']))
                        if line:
                            cell.update({
                                'qty': sum(line.mapped('product_uom_qty'))
                            })
        return matrix