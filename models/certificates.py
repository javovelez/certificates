from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

class certificates(models.Model):
    
    _name = 'certificates.certificates'
    _description ='Certificados Timsa'
    _order = 'write_date desc'

    oc_id = fields.Many2one(
        string='Orden de compra',
        comodel_name='certificates.ordencompra',
        ondelete='restrict'
        )
    subc_ol_ids = fields.One2many(
        string='subc_ol', 
        comodel_name='certificates.subc_ol', 
        inverse_name='certificate_id'
        )
    ruta = fields.Char(
        string='Ruta al certificado'
        )
    recepcion = fields.Char(string='Recepción')

    #user_id #TODO equipos de venta y vendedor

    name = fields.Char(string='Certificado', required=True)
    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'), 
            ('sent', 'Enviado'), 
            ('to_invoice', 'Para facturar'), 
            ('invoiced', 'Facturado')
            ],
        readonly=True,
        copy=False,
        index=True,
        default='draft'
        )
    validity_date = fields.Datetime(
        string='Fecha próximo reclamo', 
        required=False, index=True, 
        copy=False, default=fields.Datetime.now, 
        help="Fecha en la que se consultará el estado debido a demoras en respuestas"
        ) # Cambié required a false hasta que entienda emejor como usar el atributo states
    is_expired = fields.Boolean(
        compute='_compute_is_expired', 
        string="Is expired"
        )

    user_id = fields.Many2one(
        'res.users', string='Confeccionado por', index=True, 
        tracking=2, default=lambda self: self.env.user,
        )#TODO domain=lambda self: 
         # [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)]
    partner_id = fields.Many2one(
        'res.partner', string='Cliente', 
        required=False, index=True, 
        ) # #TODO tracking=1, Para que sea seguido en el chatter, el número representa el orden cuando se cambian múltiples campos traquedados
         #         states={'draft': [('readonly', False)], # 'sent': [('readonly', False)]},
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True, required=False,
        states={
            'draft': [('readonly', False)],
            'sent': [('readonly', False)],
            },
        )
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        )

    currency_id = fields.Many2one(
        "res.currency", string="Moneda",
        required=True
        )
    analytic_account_id = fields.Many2one(
        'account.analytic.account', 'Analytic Account',
        readonly=True, copy=False,  # Unrequired company
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help="The analytic account related to a sales order.")

    order_line = fields.One2many(
        'certificates.order.line', 
        string='Order Lines', auto_join=True,  
        inverse_name='certificate_id'
        )

    invoice_ids = fields.Many2many(
        "account.move", string='Invoices', 
        compute="_get_invoiced", readonly=True, 
        copy=False, search="_search_invoice_ids"
        )
    invoice_status = fields.Selection([
        ('upselling', 'Upselling Opportunity'),
        ('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Invoice Status', compute='_get_invoice_status', 
        store=True, readonly=True)


    invoice_ids = fields.Many2many(
        "account.move", string='Invoices', 
        compute="_get_invoiced", readonly=True, copy=False, 
        search="_search_invoice_ids")
    invoice_status = fields.Selection([
        ('invoiced', 'Facturado'),
        ('to invoice', 'A facturar'),
        ('no', 'Nada que facturar')
        ], string='Estado de factura', compute='_get_invoice_status', 
        store=True, readonly=True
        )

    note = fields.Text('Terms and conditions')

    amount_untaxed = fields.Monetary(
        string='Untaxed Amount', store=True, 
        readonly=True, compute='_amount_all', 
        tracking=5
        )
    amount_by_group = fields.Binary(
        string="Tax amount by group", 
        compute='_amount_by_group', 
        help="type: [(name, amount, base, formated amount, formated base)]"
        )
    amount_tax = fields.Monetary(
        string='Taxes', store=True, 
        readonly=True, compute='_amount_all'
        )
    amount_total = fields.Monetary(
        string='Total', store=True, 
        readonly=True, compute='_amount_all', 
        tracking=4
        )
    currency_rate = fields.Float(
        "Currency Rate", compute='_compute_currency_rate',
         compute_sudo=True, store=True, digits=(12, 6),
          readonly=True, 
          help='The rate of the currency to the currency of rate 1 applicable at the date of the order'
          )

    company_id = fields.Many2one(
        'res.company', 'Company',
        required=True, index=True, 
        default=lambda self: self.env.company
        )
    team_id = fields.Many2one(
        'crm.team', 'Sales Team',
        change_default=True)
        #default='_get_default_team',

    def action_certificate_send(self): #TODO
        self.state = 'sent'
        return

    def _compute_is_expired(self): #TODO
        return

    def _get_invoiced(self): #TODO
        return

    def _search_invoice_ids(self): #TODO
        return

    def _get_invoice_status(self): #TODO
        return

    @api.depends('order_line.price_total') 
    def _amount_all(self):#TODO
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })
        return 
    
    def _amount_by_group(self):
         return
    #     for order in self:
    #         # Hacemos esto para disponer de fecha del pedido y cia para calcular
    #         # impuesto con código python (por ej. para ARBA).
    #         # lo correcto seria que esto este en un modulo que dependa de l10n_ar_account_withholding, pero queremos
    #         # evitar ese modulo adicional por ahora
    #         date_order = order.date_order or fields.Date.context_today(order)
    #         order = order.with_context(invoice_date=date_order)
    #         if order.vat_discriminated:
    #             super(SaleOrder, order)._amount_by_group()
    #         else:
    #             currency = order.currency_id or order.company_id.currency_id
    #             fmt = partial(formatLang, self.with_context(lang=order.partner_id.lang).env, currency_obj=currency)
    #             res = {}
    #             for line in order.order_line:
    #                 price_reduce = line.price_unit * (1.0 - line.discount / 100.0)
    #                 taxes = line.report_tax_id.compute_all(
    #                     price_reduce, quantity=line.product_uom_qty, product=line.product_id,
    #                     partner=order.partner_shipping_id)['taxes']
    #                 for tax in line.report_tax_id:
    #                     group = tax.tax_group_id
    #                     res.setdefault(group, {'amount': 0.0, 'base': 0.0})
    #                     for t in taxes:
    #                         if t['id'] == tax.id or t['id'] in tax.children_tax_ids.ids:
    #                             res[group]['amount'] += t['amount']
    #                             res[group]['base'] += t['base']
    #             res = sorted(res.items(), key=lambda l: l[0].sequence)
    #             order.amount_by_group = [(
    #                 l[0].name, l[1]['amount'], l[1]['base'],
    #                 fmt(l[1]['amount']), fmt(l[1]['base']),
    #                 len(res),
    #             ) for l in res]

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        """
        Update the following fields when the partner is changed:
        - Pricelist
        - Payment terms
        - Invoice address
        - Delivery address
        - Sales Team
        """
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
            })
            return
        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.uid
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms') and self.env.company.invoice_terms:
            values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)
        


    @api.depends('company_id')
    def _compute_currency_rate(self):
        # for order in self:
        #     if not order.company_id:
        #         order.currency_rate = order.currency_id.with_context(date=order.date_order).rate or 1.0
        #         continue
        #     elif order.company_id.currency_id and order.currency_id:  # the following crashes if any one is undefined
        #         order.currency_rate = self.env['res.currency']._get_conversion_rate(order.company_id.currency_id, order.currency_id, order.company_id, order.date_order)
        #     else:
        #         order.currency_rate = 1.0
        return

    @api.model
    def _get_default_team(self):
        return #self.env['crm.team']._get_default_team_id()

    def _create_invoices(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        if not self.env['account.move'].check_access_rights('create', False):
            try:
                self.check_access_rights('write')
                self.check_access_rule('write')
            except AccessError:
                return self.env['account.move']

        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')

        # 1) Create invoices.
        invoice_vals_list = []
        for order in self:
            pending_section = None

            # Invoice values.
            invoice_vals = order._prepare_invoice()

            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if line.display_type != 'line_note' and float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if line.qty_to_invoice > 0 or (line.qty_to_invoice < 0 and final) or line.display_type == 'line_note':
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_invoice_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_invoice_line()))

            if not invoice_vals['invoice_line_ids']:
                raise UserError(_('There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(_(
                'There is no invoiceable line. If a product has a Delivered quantities invoicing policy, please make sure that a quantity has been delivered.'))

        # 2) Manage 'grouped' parameter: group by (partner_id, currency_id).
        if not grouped:
            new_invoice_vals_list = []
            invoice_grouping_keys = self._get_invoice_grouping_keys()
            for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: [x.get(grouping_key) for grouping_key in invoice_grouping_keys]):
                origins = set()
                payment_refs = set()
                refs = set()
                ref_invoice_vals = None
                for invoice_vals in invoices:
                    if not ref_invoice_vals:
                        ref_invoice_vals = invoice_vals
                    else:
                        ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                    origins.add(invoice_vals['invoice_origin'])
                    payment_refs.add(invoice_vals['invoice_payment_ref'])
                    refs.add(invoice_vals['ref'])
                ref_invoice_vals.update({
                    'ref': ', '.join(refs)[:2000],
                    'invoice_origin': ', '.join(origins),
                    'invoice_payment_ref': len(payment_refs) == 1 and payment_refs.pop() or False,
                })
                new_invoice_vals_list.append(ref_invoice_vals)
            invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.

        # As part of the invoice creation, we make sure the sequence of multiple SO do not interfere
        # in a single invoice. Example:
        # SO 1:
        # - Section A (sequence: 10)
        # - Product A (sequence: 11)
        # SO 2:
        # - Section B (sequence: 10)
        # - Product B (sequence: 11)
        #
        # If SO 1 & 2 are grouped in the same invoice, the result will be:
        # - Section A (sequence: 10)
        # - Section B (sequence: 10)
        # - Product A (sequence: 11)
        # - Product B (sequence: 11)
        #
        # Resequencing should be safe, however we resequence only if there are less invoices than
        # orders, meaning a grouping might have been done. This could also mean that only a part
        # of the selected SO are invoiceable, but resequencing in this case shouldn't be an issue.
        if len(invoice_vals_list) < len(self):
            SaleOrderLine = self.env['sale.order.line']
            for invoice in invoice_vals_list:
                sequence = 1
                for line in invoice['invoice_line_ids']:
                    line[2]['sequence'] = SaleOrderLine._get_invoice_line_sequence(new=sequence, old=line[2]['sequence'])
                    sequence += 1

        # Manage the creation of invoices in sudo because a salesperson must be able to generate an invoice from a
        # sale order without "billing" access rights. However, he should not be able to create an invoice from scratch.
        moves = self.env['account.move'].sudo().with_context(default_type='out_invoice').create(invoice_vals_list)

        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        if final:
            moves.sudo().filtered(lambda m: m.amount_total < 0).action_switch_invoice_into_refund_credit_note()
        for move in moves:
            move.message_post_with_view('mail.message_origin_link',
                values={'self': move, 'origin': move.line_ids.mapped('sale_line_ids.order_id')},
                subtype_id=self.env.ref('mail.mt_note').id
            )
        return moves


class certificatesOrderLine(models.Model):
    _name = "certificates.order.line"
    _description = 'Certificates Order Line'
    
    #@api.depends('state')
    def _compute_invoice_status(self): #TODO
            return True
        # precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # for line in self:
        #     if line.state not in ('sale', 'done'):
        #         line.invoice_status = 'no'
        #     elif not float_is_zero(line.qty_to_invoice, precision_digits=precision):
        #         line.invoice_status = 'to invoice'
        #     elif line.state == 'sale' and line.product_id.invoice_policy == 'order' and\
        #             float_compare(line.qty_delivered, line.product_uom_qty, precision_digits=precision) == 1:
        #         line.invoice_status = 'upselling'
        #     elif float_compare(line.qty_invoiced, line.product_uom_qty, precision_digits=precision) >= 0:
        #         line.invoice_status = 'invoiced'
        #     else:
        #         line.invoice_status = 'no'

    @api.depends('product_uom_qty','price_unit')
    def _compute_amount(self): 
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            taxes = line.tax_id.compute_all(line.price_unit, line.certificate_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.certificate_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.depends('product_id', 'certificate_id.state') #TODO
    def _compute_product_updatable(self):
        """
        Compute 
        """
        return True
        # for line in self:
        #     if line.state in ['done', 'cancel'] or (line.state == 'sale' and (line.qty_invoiced > 0 or line.qty_delivered > 0)):
        #         line.product_updatable = False
        #     else:
        #         line.product_updatable = True

    @api.depends('invoice_lines', 'invoice_lines.price_total', 'invoice_lines.move_id.state', 'invoice_lines.move_id.type')
    def _compute_untaxed_amount_invoiced(self): #TODO
        """ Compute the untaxed amount already invoiced from the sale order line, taking the refund attached
            the so line into account. This amount is computed as
                SUM(inv_line.price_subtotal) - SUM(ref_line.price_subtotal)
            where
                `inv_line` is a customer invoice line linked to the SO line
                `ref_line` is a customer credit note (refund) line linked to the SO line
        """
        # for line in self:
        #     amount_invoiced = 0.0
        #     for invoice_line in line.invoice_lines:
        #         if invoice_line.move_id.state == 'posted':
        #             invoice_date = invoice_line.move_id.invoice_date or fields.Date.today()
        #             if invoice_line.move_id.type == 'out_invoice':
        #                 amount_invoiced += invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
        #             elif invoice_line.move_id.type == 'out_refund':
        #                 amount_invoiced -= invoice_line.currency_id._convert(invoice_line.price_subtotal, line.currency_id, line.company_id, invoice_date)
        #     line.untaxed_amount_invoiced = amount_invoiced
        return
    
    certificate_id = fields.Many2one(
        'certificates.certificates',
        string='Certificate Reference', 
        required=True, ondelete='cascade', 
        index=True, 
        copy=False
        )
    name = fields.Text(
        string='Descripción',
        required=True
        )
    sequence = fields.Integer(string='Sequence', default=10)

    invoice_lines = fields.Many2many(
        'account.move.line', 
        'cert_order_line_invoice_rel', 
        'certificates_line_id', 
        'invoice_line_id', 
        string='Líneas de factura', 
        copy=False
        )
    invoice_status = fields.Selection(
        [('invoiced', 'Fully Invoiced'),
        ('to invoice', 'To Invoice'),
        ('no', 'Nothing to Invoice')
        ], string='Estado de factura',
        compute='_compute_invoice_status',
        store=True,
        readonly=True,
        default='no'
        )
    price_unit = fields.Float(
        'Precio unitario',
        required=True,
        digits='Product Price',
        default=0.0
        )

    price_subtotal = fields.Monetary(
        compute='_compute_amount',
        string='Subtotal',
        readonly=True, store=True
        )
    price_tax = fields.Float(
        compute='_compute_amount',
        string='Total impuestos', 
        readonly=True, 
        store=True
        )
    price_total = fields.Monetary(
        compute='_compute_amount', 
        string='Total', 
        readonly=True, 
        store=True
        )

    tax_id = fields.Many2many('account.tax', string='Impuestos',
        domain=['|', ('active', '=', False), ('active', '=', True)])

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Servicio',
        domain="[('sale_ok', '=', True)]",
        ondelete='restrict'
        )
    product_updatable = fields.Boolean(
        compute='_compute_product_updatable',
        string='Can Edit Product',
        readonly=True,
        default=True
        )
    product_uom_qty = fields.Float(
        string='Cantidad',
        digits='Product Unit of Measure',
        required=True,
        default=1.0
        )
    product_uom = fields.Many2one(
        'uom.uom', 
        string='Unidad de medida', 
        domain="[('category_id', '=', product_uom_category_id)]"
        )
    product_uom_category_id = fields.Many2one(
        related='product_id.uom_id.category_id', 
        readonly=True
        )

    currency_id = fields.Many2one('res.currency', string='Moneda')
    company_id = fields.Many2one(
        related='certificate_id.company_id',
        string='Company', store=True,
        readonly=True, index=True)

    
    order_partner_id = fields.Many2one(
        related='certificate_id.partner_id', 
        store=True, string='Cliente',
         readonly=False)
    analytic_tag_ids = fields.Many2many(
        'account.analytic.tag', 
        string='Etiquetas analíticas')
    analytic_line_ids = fields.One2many('account.analytic.line', 'cert_o_line', string="Analytic lines")

    state = fields.Selection([
        ('draft', 'Borrador'), 
        ('sent', 'Enviado'), 
        ('to_invoice', 'Para facturar'), 
        ('invoiced', 'Facturado')],
        related='certificate_id.state', 
        string='Estado del certificado', 
        readonly=True, copy=False, store=True, default='draft')
    



