# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    def get_view_sale_order_line(self):
        self.ensure_one()

        return {
            'name': 'Détail',
            'res_model': 'sale.order.line',
            'view_mode': 'tree,pivot',
            'views': [
                (self.env.ref('mkt-so-line.view_order_line_mkt_tree').id, 'tree'),
                (self.env.ref('mkt-so-line.view_order_line_mkt_pivot').id, 'pivot'),
            ],
            'type': 'ir.actions.act_window',
            'domain': [('order_id', '=', self.id)],
            'context': {'group_by': 'product_template_id'},
            'target': 'self',
        }
