from odoo import api, fields, models
from datetime import datetime, timedelta

class obra(models.Model):

    _name = 'obra'
    _description ='Obras en ejecución'
    _order = 'write_date desc'
    
    name = fields.Char(
        string='Nombre de Obra',
    )
    active=fields.Boolean(string='Estado',default=True)
    oc_ids = fields.Many2many(
        string='Órdenes de compra',
        comodel_name='certificate.ordencompra')
    
    cert_ids = fields.One2many(
        string='Certificados',
        comodel_name='certificate',
        inverse_name='obra_id')

    team_id = fields.Many2one(
        'crm.team', 'Equipo')
         #change_default=True
         #default='_get_default_team',

    user_id = fields.Many2one(
        'res.users', string='Usuario', index=True, 
        tracking=2, default=lambda self: self.env.user,
        )
    items_ids = fields.One2many(
        string='Items',
        comodel_name='item',
        inverse_name='obra_id'
        )
    partner_id = fields.Many2one(
        'res.partner', string='Cliente', 
        required=False, index=True, 
        ) # #TODO tracking=1, Para que sea seguido en el chatter, el número representa el orden cuando se cambian múltiples campos traquedados
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True, required=True,
        ) #        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},


class Items(models.Model):

    _name = 'item'
    _description ='Items a certificar'
    
    description = fields.Char(
        string='Descripción del item',
        help="Es la descripción que figurará en la factura"
        )
    
    obra_id = fields.Many2one(
        string='Obra',
        comodel_name='obra',
        ondelete='cascade'
        )
    