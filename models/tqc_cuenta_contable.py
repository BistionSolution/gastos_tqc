# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

import re, pyodbc

class cuentaContable(models.Model):
    _name = 'cuenta.contable.gastos'
    _description = 'Tipo de Liquidaciones'

    name = fields.Char()
    description = fields.Char()
    cuenta_contable = fields.Html()
    estado = fields.Char()
    centrocosto = fields.Many2one('hr.department')
    descripcioncentrocosto = fields.Char()

class cuentaContableSearch(models.Model):
    _name = 'cuenta.contable.search'
    _description = 'Buscar Liquidaciones'

    consulta = fields.Html()
    # def unlink(self):
    #     for record in self:
    #         if not (self.env.user.has_group('vacation_control.res_groups_administrator')):
    #             if record.state in ['aprobado', 'en_goce', 'gozado', 'suspend']:
    #                 raise UserError(_("No puedes eliminar registro ya calculados"))
    #         #     else:
    #         #         id_trabajador = record.vc_trabajador.id
    #         #         res = super(solicitudVacaciones, record).unlink()
    #         #         self.estado_cuenta(id_trabajador)
    #         # else:
    #         #     id_trabajador = record.vc_trabajador.id

class contableTransient(models.TransientModel):
    _name = 'cuenta.contable.transient'
    _description = 'Transient Cuenta contable'

    name = fields.Char("Cliente")
    consulta = fields.Html()