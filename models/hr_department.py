# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import re, pyodbc

class hrDepartment(models.Model):
    _inherit = 'hr.department'

    def name_get(self):  # agrega nombre al many2one relacionado
        result = []
        for rec in self:
            if rec.id_integrador:
                name = str(rec.id_integrador + ' - ' + rec.name)
            else:
                name = rec.name
            result.append((rec.id, name))
        return result

