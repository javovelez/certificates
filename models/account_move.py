# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models



class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    sale_line_ids = fields.Many2many(
        'certificate.order.line',
        'cert_order_line_invoice_rel',
        'invoice_line_id', 'certificate_line_id',
        string='Sales Order Lines', readonly=True, copy=False)