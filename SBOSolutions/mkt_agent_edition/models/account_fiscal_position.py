# -*- coding: utf-8 -*-
import json
from odoo import api, fields, models, _


class AccountFiscalPositionInherit(models.Model):
    _inherit = 'account.fiscal.position'

    is_out_eu = fields.Boolean('N\'est pas dans l\'europe ?')
