# -*- coding: utf-8 -*-

from odoo import models, fields, api

    
class ResPartner(models.Model):
    _inherit = 'res.partner'

    group_orders = fields.Selection(
        string='Grouper les Commandes',
        default='no_grouped',
        selection=[('grouped', 'Groupé'), ('no_grouped', 'Non groupé'),])
    