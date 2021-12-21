# -*- coding: utf-8 -*-

from odoo import models, fields, api

    
class ResCompany(models.Model):
    _inherit = 'res.company'

    is_group_orders_possible = fields.Boolean(string='Possibilité de regrouper les commandes')
    