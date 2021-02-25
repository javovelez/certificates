from odoo import models, fields

class subcontratista(models.Model):
    _name = 'certificate.subcontractor'
    _description ='Subcontratistas'

    name =fields.Char(string='Subcontratista', required=True)
    # invoice_id