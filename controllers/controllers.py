# -*- coding: utf-8 -*-
# from odoo import http


# class CertificatesManagement/(http.Controller):
#     @http.route('/certificates_management//certificates_management//', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/certificates_management//certificates_management//objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('certificates_management/.listing', {
#             'root': '/certificates_management//certificates_management/',
#             'objects': http.request.env['certificates_management/.certificates_management/'].search([]),
#         })

#     @http.route('/certificates_management//certificates_management//objects/<model("certificates_management/.certificates_management/"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('certificates_management/.object', {
#             'object': obj
#         })
