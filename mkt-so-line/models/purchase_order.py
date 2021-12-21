# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def get_view_purchase_order_line(self):
        self.ensure_one()

        return {
            'name': 'Détail',
            'res_model': 'purchase.order.line',
            'view_mode': 'tree,pivot',
            'views': [
                (self.env.ref('mkt-so-line.view_purchase_order_line_mkt_tree').id, 'tree'),
                (self.env.ref('mkt-so-line.view_purchase_order_line_mkt_pivot').id, 'pivot'),
            ],
            'type': 'ir.actions.act_window',
            'domain': [('order_id', '=', self.id)],
            'context': {'group_by': 'product_template_id'},
            'target': 'self',
        }
