from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _default_sale_line_domain(self): #TODO
        # """ This is only used for delivered quantity of SO line based on analytic line, and timesheet
            # (see sale_timesheet). This can be override to allow further customization.
        # """
        # return [('qty_delivered_method', '=', 'analytic')]
        return []

    cert_o_line = fields.Many2one('certificates.order.line', string='Certificate Order Item', domain=lambda self: self._default_sale_line_domain())