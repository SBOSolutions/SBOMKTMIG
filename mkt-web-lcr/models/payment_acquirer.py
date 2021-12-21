# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from uuid import uuid4

from odoo import api, exceptions, fields, models, _


class PaymentAcquirerInherit(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('lcr', 'LCR'), ('other', 'AUTRE')], ondelete={'lcr': 'set default', 'other': 'set default'})

    @api.model
    def other_s2s_form_process(self, data):
        """ Return a minimal token to allow proceeding to transaction creation. """
        payment_token = self.env['payment.token'].sudo().create({
            'acquirer_ref': uuid4(),
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id']),
            'name': 'AUTRE ACQ %s PID %s' % (str(data['acquirer_id']), str(data['partner_id'])),
        })
        return payment_token

    @api.model
    def lcr_s2s_form_process(self, data):
        """ Return a minimal token to allow proceeding to transaction creation. """
        payment_token = self.env['payment.token'].sudo().create({
            'acquirer_ref': uuid4(),
            'acquirer_id': int(data['acquirer_id']),
            'partner_id': int(data['partner_id']),
            'name': 'LCR ACQ %s PID %s' % (str(data['acquirer_id']), str(data['partner_id'])),
        })
        return payment_token


class PaymentTransactionInherit(models.Model):
    _inherit = 'payment.transaction'

    def lcr_create(self, values):
        """Automatically set the transaction as successful upon creation. """
        return {'date': datetime.now(), 'state': 'done'}

    def lcr_s2s_do_transaction(self, **kwargs):
        self.payment_token_id.active = False
        self.execute_callback()

    def other_create(self, values):
        """Automatically set the transaction as successful upon creation. """
        return {'date': datetime.now(), 'state': 'done'}

    def other_s2s_do_transaction(self, **kwargs):
        self.payment_token_id.active = False
        self.execute_callback()


class PaymentTokenInherit(models.Model):
    _inherit = 'payment.token'

    web_other_comment = fields.Text(string="Commentaire")