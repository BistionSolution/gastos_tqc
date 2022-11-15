# -*- coding: utf-8 -*-
# from odoo import http


# class GastosTqc(http.Controller):
#     @http.route('/gastos_tqc/gastos_tqc', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/gastos_tqc/gastos_tqc/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('gastos_tqc.listing', {
#             'root': '/gastos_tqc/gastos_tqc',
#             'objects': http.request.env['gastos_tqc.gastos_tqc'].search([]),
#         })

#     @http.route('/gastos_tqc/gastos_tqc/objects/<model("gastos_tqc.gastos_tqc"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('gastos_tqc.object', {
#             'object': obj
#         })
