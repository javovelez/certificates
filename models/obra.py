from odoo import api, fields, models
from datetime import datetime, timedelta

class obra(models.Model):
    _name = 'obra'
    _description ='Obras en ejecución'
    _order = 'write_date desc'
    oc_ids = fields.Many2many(
        string='Órdenes de compra',
        comodel_name='certificate.ordencompra')
    
    cert_ids = fields.One2many(
        string='Certificados',
        comodel_name='certificate',
        inverse_name='Obra_id')

    team_id = fields.Many2one(
        'crm.team', 'Equipo')
         #change_default=True
         #default='_get_default_team',