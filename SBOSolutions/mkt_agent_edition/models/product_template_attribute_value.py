# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models

class ProductTemplateAttributeValue(models.Model):
    _inherit = "product.template.attribute.value"

    def _grid_header_cell(self, fro_currency, to_currency, company, display_extra=True):
        """Generate a header matrix cell for 1 or multiple attributes.

        :param res.currency fro_currency:
        :param res.currency to_currency:
        :param res.company company:
        :param bool display_extra: whether extra prices should be displayed in the cell
            True by default, used to avoid showing extra prices on purchases.
        :returns: cell with name (and price if any price_extra is defined on self)
        :rtype: dict
        """
        header_cell = {
            'name': ' • '.join([attr.name for attr in self]) if self else " "
        }  # The " " is to avoid having 'Not available' if the template has only one attribute line.
        extra_price = sum(self.mapped('price_extra')) if display_extra else 0
        if extra_price:
            sign = '+ ' if extra_price > 0 else '- '
            header_cell.update({
                "price": sign + self.env['ir.qweb.field.monetary'].value_to_html(
                    extra_price, {
                        'from_currency': fro_currency,
                        'display_currency': to_currency,
                        'company_id': company.id,
                        }
                    )
            })
        html_colors = self.filtered(lambda p: p.html_color).mapped('html_color')
        if html_colors:
            for html_color in html_colors:
                header_cell.update({
                'html_color': str(html_color)
            })
        return header_cell
