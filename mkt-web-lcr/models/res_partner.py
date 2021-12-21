# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    web_iban = fields.Char('IBAN')
    web_bic_swift = fields.Char('BIC / SWIFT ')
    web_rib = fields.Binary('RIB')
    web_rib_name = fields.Char('RIB Filename')
