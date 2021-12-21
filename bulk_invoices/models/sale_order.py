# -*- coding: utf-8 -*-

from odoo import models, fields, api

    
class SaleOrder(models.Model):
    _inherit = 'sale.order'    
    
    def bulk_invoiced(self):
        companies = self.env['res.company'].search([
            ('is_group_orders_possible', '=', True)
        ])
        for company in companies:
            self.env.company = company
            orders = self.env['sale.order'].with_company(company).search([
                ('invoice_status', '=', 'to invoice')
            ])
            bulk_orders_ids = []
            for order in orders:
                if order.partner_id.group_orders == 'grouped' or order.partner_id.parent_id.group_orders == 'grouped':
                    bulk_orders_ids.append(order.id)
                if order.partner_id.group_orders == 'no_grouped' or order.partner_id.parent_id.group_orders == 'no_grouped':
                    invoice = order.with_company(company)._create_invoices()
                    invoice.action_post()
                    invoice.bulk_invoice_validate_send_email()
            if bulk_orders_ids:
                orders = self.env['sale.order'].browse(bulk_orders_ids)
                invoices = orders.with_company(company)._create_invoices()
                invoices.action_post()
                invoices.bulk_invoice_validate_send_email()
