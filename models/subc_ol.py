from odoo import models, fields


class SubcontratistaOrderLine(models.Model):
    _name = 'certificate.subc_ol'
    _description ='Pedidos a Subcontratistas (order Line)'
    certificate_id = fields.Many2one(
        'certificate', 
        string='Certificado TIMSA', 
        required=True, 
        ondelete='cascade', 
        inverse_name='subc_ol_ids'
        
        )
    cert_name = fields.Char(
        'Certificado',
        related='certificate_id.name',
    )
    
    partes = fields.Char(string='Partes', help='En qué partes trabajó la Subcontratista')
    subcontractor_id = fields.Many2one(
        string='subcontratista',
        comodel_name='certificate.subcontractor',
        )

    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Servicio'
        )  # Unrequired company

    quantity = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float('Monto', required=True, digits='Product Price', default=0.0)
