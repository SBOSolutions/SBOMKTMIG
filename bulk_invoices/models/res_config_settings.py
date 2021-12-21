# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    invoice_template_id = fields.Many2one('mail.template', 'Email Template',
                                  domain="[('model', '=', 'account.move')]",
                                  config_parameter='invoice.default_email_template',
                                  default=lambda self: self.env.ref('account.email_template_edi_invoice', False))