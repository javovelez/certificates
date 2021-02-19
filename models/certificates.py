from odoo import api, models, fields 
from datetime import datetime, timedelta


class certificates(models.Model):
    
    _name = 'certificates.certificates'
    _description ='Certificados Timsa'
    _order = 'write_date desc'

    oc_id = fields.Many2one(string='Orden de compra',
        comodel_name='certificates.ordencompra',
        ondelete='restrict'
        )
    order_line = fields.One2many('certificates.order.line', 
        string='Order Lines', auto_join=True,  
        inverse_name='certificate_id'
        )
    subc_ol_ids = fields.One2many(string='subc_ol', 
        comodel_name='certificates.subc_ol', 
        inverse_name='certificate_id'
        )
    

    #user_id #TODO equipos de venta y vendedor

    name = fields.Char(string='Certificado', required=True)
    ruta = fields.Char(
        string='Ruta al certificado'
    )
    
    recepcion = fields.Char(string='Recepción')
    state = fields.Selection(
        string='Estado',
        selection=[
            ('draft', 'Borrador'), 
            ('sent', 'Enviado'), 
            ('delayed', 'Demorado'), 
            ('to_invoice', 'Para facturar'), 
            ('invoiced', 'Facturado')
            ],
        readonly=True,
        copy=False,
        index=True,
        default='draft'
        )
    validity_date = fields.Datetime(string='Fecha próximo reclamo', 
        required=False, index=True, 
        copy=False, default=fields.Datetime.now, 
        help="Fecha en la que se consultará el estado debido a demoras en respuestas"
        ) # Cambié required a false hasta que entienda emejor como usar el atributo states
    is_expired = fields.Boolean(compute='_compute_is_expired', string="Is expired")



    user_id = fields.Many2one(
        'res.users', string='Confeccionado por', index=True, tracking=2, default=lambda self: self.env.user,
        )#TODO domain=lambda self: [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)]
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
            'sale': [('delayed', False)]
            },
        )
    currency_id = fields.Many2one("res.currency", 
        string="Moneda",
        )


    company_id = fields.Many2one('res.company', 'Company',
        required=True, index=True, 
        default=lambda self: self.env.company
        )

    def action_certificate_send(self): #TODO
        return
    def _compute_is_expired(self): #TODO
        return

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
    def _compute_amount(self): #TODO
        """
        Compute the amounts of the SO line.
        """
        return True
        # for line in self:
        #     price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        #     taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_shipping_id)
        #     line.update({
        #         'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
        #         'price_total': taxes['total_included'],
        #         'price_subtotal': taxes['total_excluded'],
        #     })
        #     if self.env.context.get('import_file', False) and not self.env.user.user_has_groups('account.group_account_manager'):
        #         line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

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
        ('delayed', 'Demorado'), 
        ('to_invoice', 'Para facturar'), 
        ('invoiced', 'Facturado')],
        related='certificate_id.state', 
        string='Estado del certificado', 
        readonly=True, copy=False, store=True, default='draft')
    



