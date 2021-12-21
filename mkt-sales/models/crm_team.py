# -*- coding: utf-8 -*-

from odoo import models, fields, api


class CrmTeam(models.Model):
    _inherit = 'crm.team'
    
    agent_name = fields.Char(string='Nom du representant')
    
    
    
    