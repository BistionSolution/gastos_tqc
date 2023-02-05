# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import re, pyodbc

class tqcSearchClient(models.TransientModel):
    _name = 'tqc.searchclient'
    _description = 'buscar cliente'

    name = fields.Char("Cliente")
    consulta = fields.Html()