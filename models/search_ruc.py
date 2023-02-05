# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import re, pyodbc

class tqcSearchRuc(models.TransientModel):
    _name = 'tqc.searchruc'
    _description = 'buscar cliente'

    name = fields.Char("Ruc")
    consulta = fields.Html()
