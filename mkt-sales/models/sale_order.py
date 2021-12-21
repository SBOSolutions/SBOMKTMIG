# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    agentapp_name = fields.Char(string='N° commande agent')
    order_type = fields.Selection(string='Type de commande', selection=[('initial', 'Initiale'), ('restock', 'Reassort'),])
    is_email_sent = fields.Boolean(string="Email confim cde", readonly=True)



    def sh_send_mass_emails(self):
    
        sale_order_obj = self.env["sale.order"]
        active_ids = self.env.context.get("active_ids")
        if active_ids:
            for active_id in active_ids:
                search_so_rec = sale_order_obj.search(
                    [("id", "=", active_id)], limit=1)
                if search_so_rec:
                    template = False
                    template = self.env.ref(
                        "sale.mail_template_sale_confirmation",
                        raise_if_not_found=False
                    )
                    if template:
                        template.sudo().send_mail(
                            search_so_rec.id,
                            force_send=True,
                            raise_exception=False,
                            notif_layout="mkt-sales.sbo_mail_notification_light",
                        )
                        search_so_rec.is_email_sent = True
                    if search_so_rec.state == "draft":
                        search_so_rec.state = "sent"
# override complete std methode in order to send email without branding
    def action_quotation_send(self):
        ''' Opens a wizard to compose an email, with relevant mail template loaded by default '''
        self.ensure_one()
        template_id = self._find_mail_template()
        lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        if template.lang:
            lang = template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'custom_layout': "mkt-sales.sbo_mail_notification_light",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }
        result = super(SaleOrder,self).action_quotation_send()
        return result
