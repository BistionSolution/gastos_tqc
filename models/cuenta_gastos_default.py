# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

import re, pyodbc

class cuentaDefault(models.Model):
    _name = 'cuenta.gastos.default'
    _description = 'Tipo de Liquidaciones'

    codigo = fields.Char()
    description = fields.Char()

    def name_get(self):  # agrega nombre al many2one relacionado
        result = []
        for rec in self:
            if rec.description:
                name = rec.description
            else:
                name = 'default description'
            result.append((rec.id, name))
        return result
