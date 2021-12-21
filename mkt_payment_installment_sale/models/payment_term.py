# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    installment_yesno = fields.Boolean(string='Installment')
    payment_mode = fields.Selection([
        ('CB', 'CB'),
        ('CHEQUE', 'Cheque'),
        ('LCR', 'LCR'),
        ('SEPA', 'SEPA'),
        ('VIR', 'Virement'),
    ], string='Mode de paiement (plf)')