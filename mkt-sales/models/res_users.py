# -*- coding: utf-8 -*-

from odoo import api, fields, models


class resUsers(models.Model):
    _inherit = 'res.users'

    team_id = fields.Many2one(comodel_name='crm.team', string='Sales teams')