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
    department_id = fields.Many2one('hr.department')
    active = fields.Boolean(default=True)

    def name_get(self):  # agrega nombre al many2one relacionado
        result = []
        for rec in self:
            if rec.description:
                name = rec.description
            else:
                name = 'default description'
            result.append((rec.id, name))
        return result

    def get_account_contable(self):
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
        prefix_table = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.prefix_table')
        if data_base:
            # Ingorar si prefix_table es minisculas o mayusculas y validar si es igual a 'TQC'
            sql = ""
            if prefix_table.lower() == 'tqc':
                sql = """select cen.CENTRO_COSTO,cen.CUENTA_CONTABLE,cta1.DESCRIPCION,cen.ESTADO from TQC.CENTRO_cuenta cen
    inner join TQC.CENTRO_COSTO cc1 on cc1.CENTRO_COSTO=cen.CENTRO_COSTO
    inner join TQC.CUENTA_CONTABLE cta1 on cta1.CUENTA_CONTABLE=cen.CUENTA_CONTABLE
    Where CTA1.ACEPTA_DATOS='S' AND CEN.ESTADO='A' AND CC1.ACEPTA_DATOS='S' AND (cen.CUENTA_CONTABLE in ('62.4.1.0.0.00.00','62.4.3.0.0.00.00','62.5.4.0.0.00.00','62.5.5.0.0.00.00','62.5.6.0.0.00.00','63.1.1.1.1.11.00','63.1.1.1.1.12.00','63.1.1.1.1.13.00','63.1.2.1.0.00.00','63.1.3.1.0.00.00','63.1.3.2.0.00.00','63.1.4.1.0.00.00','63.1.4.2.0.00.00','63.1.5.1.0.00.00','63.1.5.2.0.00.00','63.2.1.1.0.00.00','63.2.2.1.0.00.00','63.2.2.2.0.00.00','63.2.3.2.0.00.00','63.2.5.1.0.00.00','63.2.6.1.0.00.00','63.2.9.1.0.00.00','63.2.9.3.0.00.00','63.2.9.4.0.00.00','63.2.9.6.0.00.00','63.2.9.7.0.00.00','63.4.3.1.0.00.00','63.4.3.2.0.00.00','63.4.3.3.0.00.00','63.4.3.4.0.00.00','63.4.3.5.0.00.00','63.4.3.8.0.00.00','63.4.3.9.0.00.00','63.7.1.1.0.00.00','63.7.1.2.0.00.00','63.7.1.3.0.00.00','63.7.1.4.0.00.00','63.7.1.5.0.00.00','63.7.1.6.0.00.00','63.7.1.7.0.00.00','63.7.1.8.0.00.00','63.7.1.9.0.00.00','63.7.2.1.0.00.00','63.7.3.1.0.00.00','63.7.3.3.0.00.00','63.7.3.4.0.00.00','63.7.3.5.0.00.00','63.7.4.1.0.00.00','63.7.4.2.0.00.00','63.7.4.3.0.00.00','63.7.4.4.0.00.00','63.7.4.5.0.00.00','63.8.2.0.0.00.00','63.9.1.1.1.07.00','63.9.1.1.1.10.00','63.9.2.1.0.00.00','65.3.3.0.0.00.00','65.6.1.1.1.02.00','65.6.1.1.1.03.00','65.6.1.1.1.04.00','65.6.1.1.1.05.00','65.6.1.1.1.06.00','65.6.1.1.1.07.00','65.6.1.1.1.08.00','65.6.1.1.1.09.00','65.6.1.1.1.10.00','65.6.1.1.1.11.00','65.6.1.1.1.12.00','65.9.5.0.0.00.00','65.9.6.0.0.00.00','65.9.7.0.0.00.00','65.9.8.0.0.00.00','67.9.3.9.0.00.00'))
    And substring(cen.CENTRO_COSTO,1,2) in ('22','23','41','42','43','44','45','49','51','52','53','58','59')"""
            elif prefix_table.lower() == 'talex':
                sql = """select cen.CENTRO_COSTO,cen.CUENTA_CONTABLE,cta1.DESCRIPCION,cen.ESTADO from TALEX.CENTRO_cuenta cen
inner join TALEX.CENTRO_COSTO cc1 on cc1.CENTRO_COSTO=cen.CENTRO_COSTO
inner join TALEX.CUENTA_CONTABLE cta1 on cta1.CUENTA_CONTABLE=cen.CUENTA_CONTABLE
Where CTA1.ACEPTA_DATOS='S' AND CEN.ESTADO='A' AND CC1.ACEPTA_DATOS='S' AND (cen.CUENTA_CONTABLE in ('62.4.1.0.0.00.00','62.4.3.0.0.00.00','62.5.6.0.0.00.00','63.1.1.1.1.08.00','63.1.1.1.1.09.00','63.1.1.1.1.10.00','63.1.2.0.0.00.00','63.1.3.1.0.00.00','63.1.3.2.0.00.00','63.1.4.1.0.00.00','63.1.4.2.0.00.00','63.1.5.1.0.00.00','63.1.5.2.0.00.00','63.2.6.1.0.00.00','63.2.9.6.0.00.00','63.2.9.7.0.00.00','63.3.2.0.0.00.00','63.4.3.1.0.00.00','63.4.3.2.0.00.00','63.4.3.3.0.00.00','63.4.3.4.0.00.00','63.4.3.5.0.00.00','63.4.3.8.0.00.00','63.4.3.9.0.00.00','63.7.1.1.0.00.00','63.7.1.2.0.00.00','63.7.1.3.0.00.00','63.7.1.4.0.00.00','63.7.1.5.0.00.00','63.7.1.6.0.00.00','63.7.1.7.0.00.00','63.7.1.8.0.00.00','63.7.1.9.0.00.00','63.7.2.1.0.00.00','63.7.3.1.0.00.00','63.7.3.3.0.00.00','63.7.3.4.0.00.00','63.7.3.5.0.00.00','63.8.2.0.0.00.00','63.9.2.1.0.00.00','63.9.3.1.1.07.00','63.9.3.1.1.10.00','63.9.3.1.1.14.00','65.6.1.1.1.02.00','65.6.1.1.1.03.00','65.6.1.1.1.04.00','65.6.1.1.1.05.00','65.6.1.1.1.06.00','65.6.1.1.1.07.00','65.6.1.1.1.08.00','65.6.1.1.1.09.00','65.6.1.1.1.10.00','65.6.1.1.1.12.00','65.9.3.1.0.00.00','65.9.3.5.0.00.00'))
And substring(cen.CENTRO_COSTO,1,2) in ('22','23','41','42','43','44','45','49','51','52','53','58','59')"""
            elif prefix_table.lower() == 'semillas':
                sql = """select cen.CENTRO_COSTO,cen.CUENTA_CONTABLE,cta1.DESCRIPCION,cen.ESTADO from SEMILLAS.CENTRO_cuenta cen
inner join SEMILLAS.CENTRO_COSTO cc1 on cc1.CENTRO_COSTO=cen.CENTRO_COSTO
inner join SEMILLAS.CUENTA_CONTABLE cta1 on cta1.CUENTA_CONTABLE=cen.CUENTA_CONTABLE
Where CTA1.ACEPTA_DATOS='S' AND CEN.ESTADO='A' AND CC1.ACEPTA_DATOS='S' AND (cen.CUENTA_CONTABLE in ('62.4.1.0.0.00.00','62.4.3.0.0.00.00','62.5.6.0.0.00.00','63.1.1.1.1.11.00','63.1.1.1.1.12.00','63.1.1.1.1.13.00','63.1.2.1.0.00.00','63.1.3.1.0.00.00','63.1.3.2.0.00.00','63.1.4.1.0.00.00','63.1.4.2.0.00.00','63.1.5.1.0.00.00','63.1.5.2.0.00.00','63.2.4.1.0.00.00','63.2.4.2.0.00.00','63.2.6.1.0.00.00','63.2.9.7.0.00.00','63.3.2.0.0.00.00','63.4.3.1.0.00.00','63.4.3.2.0.00.00','63.4.3.3.0.00.00','63.4.3.4.0.00.00','63.4.3.5.0.00.00','63.4.3.8.0.00.00','63.4.3.9.0.00.00','63.7.1.1.0.00.00','63.7.1.2.0.00.00','63.7.1.3.0.00.00','63.7.1.4.0.00.00','63.7.1.5.0.00.00','63.7.1.6.0.00.00','63.7.1.7.0.00.00','63.7.1.8.0.00.00','63.7.1.9.0.00.00','63.7.2.1.0.00.00','63.7.3.1.0.00.00','63.7.3.3.0.00.00','63.7.3.4.0.00.00','63.7.3.5.0.00.00','63.8.2.0.0.00.00','63.9.1.1.1.07.00','63.9.1.1.1.10.00','63.9.1.1.1.15.00','63.9.2.1.0.00.00','65.6.1.1.1.02.00','65.6.1.1.1.03.00','65.6.1.1.1.04.00','65.6.1.1.1.05.00','65.6.1.1.1.06.00','65.6.1.1.1.07.00','65.6.1.1.1.08.00','65.6.1.1.1.09.00','65.6.1.1.1.10.00','65.6.1.1.1.12.00','65.9.5.0.0.00.00','65.9.6.0.0.00.00','65.9.7.0.0.00.00','67.9.3.9.0.00.00'))
And substring(cen.CENTRO_COSTO,1,2) in ('22','23','41','42','43','44','45','49','51','52','53','58','59')"""
            elif prefix_table.lower() == 'biogen':
                sql = """select cen.CENTRO_COSTO,cen.CUENTA_CONTABLE,cta1.DESCRIPCION,cen.ESTADO from BIOGEN.CENTRO_cuenta cen
inner join BIOGEN.CENTRO_COSTO cc1 on cc1.CENTRO_COSTO=cen.CENTRO_COSTO
inner join BIOGEN.CUENTA_CONTABLE cta1 on cta1.CUENTA_CONTABLE=cen.CUENTA_CONTABLE
Where CTA1.ACEPTA_DATOS='S' AND CEN.ESTADO='A' AND CC1.ACEPTA_DATOS='S' AND (cen.CUENTA_CONTABLE in ('62.4.1.0.0.00.00','62.4.3.0.0.00.00','62.5.6.0.0.00.00','63.1.1.1.1.11.00','63.1.1.1.1.12.00','63.1.1.1.1.13.00','63.1.2.1.0.00.00','63.1.3.1.0.00.00','63.1.3.2.0.00.00','63.1.4.1.0.00.00','63.1.4.2.0.00.00','63.1.5.1.0.00.00','63.1.5.2.0.00.00','63.2.5.1.0.00.00','63.2.6.1.0.00.00','63.3.1.0.0.00.00','63.3.2.0.0.00.00','63.4.3.1.0.00.00','63.4.3.2.0.00.00','63.4.3.3.0.00.00','63.4.3.4.0.00.00','63.4.3.5.0.00.00','63.4.3.8.0.00.00','63.4.3.9.0.00.00','63.6.1.1.0.00.00','63.7.1.1.0.00.00','63.7.1.2.0.00.00','63.7.1.3.0.00.00','63.7.1.4.0.00.00','63.7.1.5.0.00.00','63.7.1.6.0.00.00','63.7.1.7.0.00.00','63.7.1.8.0.00.00','63.7.1.9.0.00.00','63.7.2.1.0.00.00','63.7.3.1.0.00.00','63.7.3.2.0.00.00','63.7.3.3.0.00.00','63.7.3.4.0.00.00','63.7.3.5.0.00.00','63.8.2.0.0.00.00','63.9.1.1.1.01.00','63.9.1.1.1.07.00','63.9.1.1.1.10.00','63.9.1.1.1.15.00','63.9.2.1.0.00.00','65.3.3.0.0.00.00','65.6.1.1.1.02.00','65.6.1.1.1.03.00','65.6.1.1.1.04.00','65.6.1.1.1.05.00','65.6.1.1.1.06.00','65.6.1.1.1.07.00','65.6.1.1.1.08.00','65.6.1.1.1.09.00','65.6.1.1.1.10.00','65.6.1.1.1.11.00','65.6.1.1.1.12.00','65.8.1.0.0.00.00','65.9.5.0.0.00.00','65.9.6.0.0.00.00','65.9.7.0.0.00.00','67.9.3.9.0.00.00'))
And substring(cen.CENTRO_COSTO,1,2) in ('22','23','41','42','43','44','45','49','51','52','53','58','59')"""
            elif prefix_table.lower() == 'agravent':
                sql = """select cen.CENTRO_COSTO,cc1.DESCRIPCION,cta1.DESCRIPCION,cen.ESTADO from AGRAVENT.CENTRO_cuenta cen
inner join AGRAVENT.CENTRO_COSTO cc1 on cc1.CENTRO_COSTO=cen.CENTRO_COSTO
inner join AGRAVENT.CUENTA_CONTABLE cta1 on cta1.CUENTA_CONTABLE=cen.CUENTA_CONTABLE
WHERE (CTA1.ACEPTA_DATOS='S' AND CEN.ESTADO='A' AND (CEN.CENTRO_COSTO NOT IN ('00.00.00.00') AND SUBSTRING(CEN.CENTRO_COSTO,1,2) NOT IN ('21','75','70','69'))) AND (SUBSTRING(CTA1.CUENTA_CONTABLE,1,2) IN ('62','63','64','65') AND CC1.ACEPTA_DATOS='S')"""

            ip_conexion = "10.10.10.228"
            data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
            user_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.username_exactus')
            pass_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.password_exactus')

            table_bd = 'cuenta.gastos.default'

            connection = pyodbc.connect(
                'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)

            cursor = connection.cursor()
            cursor.execute(sql)
            # GUARDA TODOS LOS REGISTROS DE SQL
            idusers = cursor.fetchall()
            # lista de campos odoo
            campList = ['department_id', 'codigo', 'description']

            # if company_table CONTAIN "EMPLEADO" then logic calculate states of the employees ('CES')
            nom_module = "cuenta.gastos.default"

            posiUser = [0]

            dataExternalSQL = [['department_id'], ['hr_department']]

            for user in idusers:
                variJson = {}
                sumNom = f'{user[0]}-{user[1]}'

                existId = self.env['ir.model.data'].search([('model', '=', nom_module), ('name', '=', sumNom)],
                                                           limit=1)
                res_id = existId.res_id

                def populate_variJson():
                    cont = 0
                    for i, field in enumerate(campList):
                        if i in posiUser:  # Translate names to corresponding IDs
                            if not user[i]:  # If field is NULL, set to False
                                id_exField = False
                            else:
                                searchId = f"{dataExternalSQL[1][cont]}.{user[i]}"
                                try:
                                    id_exField = self.env.ref(searchId).id
                                except ValueError:
                                    id_exField = False
                            variJson[field] = id_exField
                            cont += 1
                        else:
                            variJson[field] = user[i]

                populate_variJson()

                if existId:
                    self.env[table_bd].browse(res_id).write(variJson)
                else:
                    print("QUYE GFFES  XDXDXD")
                    original_id = self.env[table_bd].create(variJson).id
                    self.env["ir.model.data"].create({
                        'name': f'{user[0]}-{user[1]}',
                        'module': nom_module,
                        'model': table_bd,
                        'res_id': original_id
                    })

                self.env.cr.commit()
