# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.misc import formatLang, format_date, get_lang



class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    def _action_generate_backorder_wizard(self, show_transfers=False):
        return self.env['stock.backorder.confirmation'].process()

    def action_invoice_sent(self):
        self.ensure_one()
        template = self.env.ref('mkt-stock.email_template_mkt_return', raise_if_not_found=False)
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model="stock.picking",
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            default_is_log=False,
            custom_layout='mail.mail_notification_light',
        )
        return {
            'name': _('Bon de retour'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    is_delivery = fields.Boolean(string='OK Livraison', copy=False)
