# -*- coding: utf-8 -*-

from odoo import models, fields, api, SUPERUSER_ID

    
class AccountMove(models.Model):
    _inherit = 'account.move'    
        
    def bulk_invoice_validate_send_email(self):
        if self.env.su:
            # sending mail in sudo was meant for it being sent from superuser
            self = self.with_user(SUPERUSER_ID)
        for invoice in self.filtered(lambda x: x.move_type == 'out_invoice'):
            # send template only on customer invoice
            # subscribe the partner to the invoice
            if invoice.partner_id not in invoice.message_partner_ids:
                invoice.message_subscribe([invoice.partner_id.id])
            template_id = self._find_mail_template(force_confirmation_template=True)
            invoice.with_context(force_send=True).message_post_with_template(
                template_id,
                composition_mode="comment" if len(self) == 1 else 'mass_mail',
                email_layout_xmlid="mail.mail_notification_light"
                )
        return True
    
    def _find_mail_template(self, force_confirmation_template=False):
        template_id = False
        if force_confirmation_template or (self.state == 'draft' and not self.env.context.get('proforma', False)):
            template_id = int(self.env['ir.config_parameter'].sudo().get_param('invoice.default_email_template'))
            template_id = self.env['mail.template'].search([('id', '=', template_id)]).id
            if not template_id:
                template_id = self.env['ir.model.data'].xmlid_to_res_id('account.email_template_edi_invoice', raise_if_not_found=False)
        if not template_id:
            template_id = self.env['ir.model.data'].xmlid_to_res_id('account.email_template_edi_invoice', raise_if_not_found=False)

        return template_id

