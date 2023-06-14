# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import re, pyodbc

database = 'TQCBKP2'
userbd = "TQC"
passbd = "extqc"
class tqcImpuesto(models.Model):
    _name = 'tqc.impuestos'
    _description = 'Impuestos de TQC'

    impuesto = fields.Char(string='Codigo')
    descripcion = fields.Char(string="Descripcion")
    impuesto1 = fields.Float(string="Valor")
    def name_get(self):  # agrega nombre al many2one relacionado
        result = []
        for rec in self:
            name = rec.descripcion
            result.append((rec.id, name))
        return result

    def load_impuestos(self):
        data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
        prefix_table = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.prefix_table')
        if data_base:
            sql = """SELECT IMPUESTO AS external_id, 
                    IMPUESTO AS impuesto,
                    DESCRIPCION AS descripcion,
                    IMPUESTO1 AS impuesto1
                    FROM """ + prefix_table + """.IMPUESTO"""

            ip_conexion = "10.10.10.228"
            data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
            user_bd = userbd
            pass_bd = passbd

            table_bd = 'tqc.impuestos'

            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)

            cursor = connection.cursor()
            cursor.execute(sql)
            idusers = cursor.fetchall()  # GUARDA TODOS LOS REGISTROS DE SQL
            campList = self.convert_sql(sql)  # lista de campos odoo
            # if company_table CONTAIN "EMPLEADO" then logic calculate states of the employees ('CES')
            nom_module = table_bd.replace(".", "_")

            for user in idusers:
                variJson = {}
                existId = True
                sumNom = "{}.{}".format(nom_module, user[0])  # (nombre modulo) + (id del sql)
                try:
                    id_register = self.env.ref(sumNom).id
                except ValueError:
                    existId = False

                # SI EXISTE ACTUALIZA
                if existId:
                    # ACTUALIZA REGISTRO
                    no_register = False

                    for j in range(len(campList)):
                        if j == 0:
                            continue
                        variJson['{}'.format(campList[j])] = user[j]

                    if not no_register:
                        self.env[table_bd].browse(id_register).write(variJson)
                        self.env.cr.commit()

                # si no encuentra crea registro
                else:
                    no_register = False  # PARA REGISTRAR
                    for i in range(len(campList)):  # recorre y relaciona los campos y datos para trasladar datos
                        if i == 0:
                            continue
                        variJson['{}'.format(campList[i])] = user[i]

                    # si no llega a true y sigue falso continua la creacion
                    if not no_register:
                        original_id = self.env[table_bd].create(variJson).id
                        # Si funciona
                        self.env["ir.model.data"].create(
                            {'name': user[0], 'module': nom_module, 'model': table_bd, 'res_id': original_id})
                        self.env.cr.commit()

    def convert_sql(self, frase):  # separa la frase para sacar los nombre de los campos de odoo
        variJson = []
        frase_express = frase.replace("SELECT", "").replace("WHERE", "$").replace("FROM", "$").replace("\n",
                                                                                                       "").replace("\r",
                                                                                                                   "")
        parte_frase = re.split(r'[$]', frase_express)
        variables = parte_frase[0].replace(" AS ", ",").replace(" ", "")
        campos = re.split(r'[,\s]\s*', variables)
        cant = int(len(campos) / 2)
        for i in range(cant):
            variJson.append(campos[(i * 2) + 1])

        # AHORA PARA CADA BASE DE DATOS, CADA EMPRESA
        empresa_bd = parte_frase[1].replace(" ", "")
        return variJson