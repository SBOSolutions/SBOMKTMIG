# -*- coding: utf-8 -*-
# Copyright 2021 CTO IT Consuling
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api
from odoo import SUPERUSER_ID
from os import path
import logging

logger = logging.getLogger('Create Season')

def migrate(cr, v):

    with api.Environment.manage():
        uid = SUPERUSER_ID
        ctx = api.Environment(cr, uid, {})['res.users'].context_get()
        env = api.Environment(cr, uid, ctx)

        seasons = env['product.template'].search([
            ('season', '!=', False)
        ]).mapped('season')
        for season in seasons:
            Season = env['res.season'].search([
                ('name', '=', season)
            ])
            if not Season:
                season = env['res.season'].create({
                    'name':season
                })
        product_templates = env['product.template'].search([
            ('season', '!=', False)
        ])
        for product_tmpl in product_templates:
            season = env['res.season'].search([
                ('name', '=', product_tmpl.season)
            ])
            if season:
                product_tmpl.season_id = season.id
        sale_orders = env['sale.order'].search([
            ('season', '!=', False)
        ])
        for order in sale_orders:
            season = env['res.season'].search([
                ('name', '=', product_tmpl.season)
            ])
            if season:
                order.season_id = season.id