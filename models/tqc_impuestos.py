# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import re, pyodbc

class tqcImpuesto(models.Model):
    _name = 'tqc.impuestos'
    _description = 'Impuestos de TQC'

    name = fields.Char(string="Nombre")
    descripcion = fields.Char()
    impuesto = fields.Float()

    def name_get(self):  # agrega nombre al many2one relacionado
        result = []
        for rec in self:
            if rec.name:
                name = str(rec.name + ' - ' + str(rec.impuesto))
            else:
                name = rec.name
            result.append((rec.id, name))
        return result

    def load_impuestos(self):
        data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
        if data_base:
            sql_prime = """SELECT IMPUESTO AS external_id, 
                                IMPUESTO AS name,
                                DESCRIPCION AS descripcion,
                                CONVERT(decimal(10,2),IMPUESTO1) AS impuesto
                                FROM """ + data_base + """.IMPUESTO"""

            sql = """SELECT IMPUESTO AS external_id, 
                    IMPUESTO AS name,
                    DESCRIPCION AS descripcion,
                    IMPUESTO1 AS impuesto
                    FROM """ + data_base + """.IMPUESTO"""

            ip_conexion = "10.10.10.228"
            data_base = "TQC"
            user_bd = "vacaciones"
            pass_bd = "exvacaciones"

            table_bd = 'tqc.impuestos'

            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)

            cursor = connection.cursor()
            cursor.execute(sql_prime)
            idusers = cursor.fetchall()  # GUARDA TODOS LOS REGISTROS DE SQL
            campList = self.convert_sql(sql)  # lista de campos odoo
            # if company_table CONTAIN "EMPLEADO" then logic calculate states of the employees ('CES')
            nom_module = table_bd.replace(".", "_")

            for user in idusers:
                user[3] = (user[3]) / 100
                print("goes , ", user[3])
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