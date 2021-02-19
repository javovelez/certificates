from odoo import models, fields


class ordenCompra(models.Model):
    _name ='certificates.ordencompra'
    _description ='Certificado de subcontratista'
    name = fields.Char(string='Código OC', required=True)
    monto = fields.Integer(string='monto')
    certificados_ids = fields.One2many(
        string = 'Certificado asociado',
        comodel_name = 'certificates.certificates',
        inverse_name = 'oc_id',
    )

    

    
