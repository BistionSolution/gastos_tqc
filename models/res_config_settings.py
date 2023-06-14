from datetime import datetime, date, timedelta, time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

import re, pyodbc

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    data_base_gastos= fields.Char("Base de datos")
    prefix_table = fields.Char("Prefijo tabla")
    max_serie = fields.Integer("Serie máximo caracteres")
    min_serie = fields.Integer("Serie minimo caracteres")
    pass_user_gastos = fields.Char("Contraseña")

    @api.model
    def set_values(self):
        self.env['ir.config_parameter'].sudo().set_param('gastos_tqc.data_base_gastos', self.data_base_gastos)
        self.env['ir.config_parameter'].sudo().set_param('gastos_tqc.prefix_table', self.prefix_table)
        self.env['ir.config_parameter'].sudo().set_param('gastos_tqc.pass_user_gastos', self.pass_user_gastos)
        self.env['ir.config_parameter'].sudo().set_param('gastos_tqc.max_serie', self.max_serie)
        self.env['ir.config_parameter'].sudo().set_param('gastos_tqc.min_serie', self.min_serie)
        super(ResConfigSettings, self).set_values()

    @api.model
    def get_values(self):
        val = self.env['ir.config_parameter'].sudo()
        res = super(ResConfigSettings, self).get_values()
        res['data_base_gastos'] = val.get_param('gastos_tqc.data_base_gastos')
        res['prefix_table'] = val.get_param('gastos_tqc.prefix_table')
        res['pass_user_gastos'] = val.get_param('gastos_tqc.pass_user_gastos')
        res['max_serie'] = val.get_param('gastos_tqc.max_serie')
        res['min_serie'] = val.get_param('gastos_tqc.min_serie')
        return res

    def action_calcular(self):
        val = self.env['ir.config_parameter'].sudo()
        new_pass = val.get_param('gastos_tqc.pass_user_gastos')
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group("gastos_tqc.res_groups_employee_gastos"):
                self.env['res.users'].browse(user.id).write({'password': new_pass})
