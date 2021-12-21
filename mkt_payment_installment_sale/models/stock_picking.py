# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    installment_status = fields.Selection(string='installment status',related='sale_id.installment_status')


    # def button_validate(self):
    #     if not self.installment_status == 'received':
    #         raise UserError('Plan de financement non reçu impossible d\'expedier la marchandise')
    #     res = super(StockPicking,self).button_validate()
    #     return res