# -*- coding: utf-8 -*-
import os

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from xlrd import open_workbook
import base64
from io import StringIO

try:
    import xlrd
    try:
        from xlrd import xlsx
    except ImportError:
        xlsx = None
except ImportError:
    xlrd = xlsx = None

class DeleteLineInSoWizard(models.TransientModel):
    _name = 'delete_line_in_so.wizard'
    _description = 'Update sale order lines and purchase lines'

    @api.onchange('product_ids_file')
    def on_change_import_xlsx(self):
        if self.product_ids_file:
            wb = open_workbook(file_contents=base64.decodebytes(self.product_ids_file))
            # Read file and get record after first range information
            ids_list = []
            for s in wb.sheets():
                for row in range(1, s.nrows):
                    for col in range(s.ncols):
                        try:
                            pt_id = int(s.cell_value(row, col))
                            if self.env['product.product'].browse(pt_id):
                                ids_list.append(pt_id)
                        except ValueError:
                            pass

            if ids_list:
                self.products_ids = [(6, 0, ids_list)]

    def generate_activity(self, model, message, res_id):
        model_id = self.env['ir.model'].search([('model', '=', model)])
        activity_type = self.env['mail.activity.type'].search([('ref', '=', 'todo')])
        self.env['mail.activity'].create({
            'note': message,
            'res_model': model,
            'res_model_id': model_id.id,
            'activity_type_id': activity_type.id,
            'user_id': self.env.user.id,
            'res_id': res_id,  # here add the channel you created.
        })

    def clear_lines_in_so_pu(self):
        self.ensure_one()
        if self.sales_orders_lines_ids:
            oder_id_pass_notif = []
            for line in self.sales_orders_lines_ids:
                # Search stock move from picking_id and product_id
                for move in line.move_ids:
                    move.state = 'draft'
                    move.unlink()

                line.write({
                    'state': 'cancel',
                    'product_uom_qty': 0
                })
                if line.order_id.id not in oder_id_pass_notif:
                    self.generate_activity('sale.order', 'Envoyer la notification de modification du devis', line.order_id.id)
                    oder_id_pass_notif.append(line.order_id.id)

                line.unlink()

        if self.purchases_orders_lines_ids:
            update_purchase_order = []
            oder_id_pass_notif = []

            for line in self.purchases_orders_lines_ids:
                state = line.order_id.state
                update_purchase_order.append({'order_id': line.order_id.id, 'state': state, 'order_line_id': line.id})
                if line.order_id.id not in oder_id_pass_notif:
                    self.generate_activity('purchase.order', 'Envoyer la notification de modification de la commande', line.order_id.id)
                    oder_id_pass_notif.append(line.order_id.id)

            for item in update_purchase_order:
                self.env['purchase.order'].browse(item['order_id']).state = 'draft'
                record = self.env['purchase.order.line'].browse(item['order_line_id'])
                for move in record.move_ids:
                    move.state = 'draft'
                    move.unlink()
                record.unlink()
                self.env['purchase.order'].browse(item['order_id']).state = item['state']

    products_ids = fields.Many2many('product.product', string='Produits')
    sales_orders_lines_ids = fields.Many2many('sale.order.line', string='Devis')
    purchases_orders_lines_ids = fields.Many2many('purchase.order.line', string='Achats')
    product_ids_file = fields.Binary(attachment=False, string='Fichier d\'articles')


