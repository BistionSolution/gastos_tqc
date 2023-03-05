# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import re, pyodbc


class TqcAuth(models.Model):
    _name = 'tqc.autorizadores'
    _description = 'Autorizadores Jefatura'

    superior = fields.Many2one("hr.employee", string='Superior', required=1)
    subordinados = fields.Many2many("hr.employee", string="Subordinado", required=1)

    def load_autorizadores(self):
        data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
        if data_base:
            self.env['tqc.autorizadores'].search([]).unlink()
            self.env.cr.commit()
            sql = """SELECT
                      SUPERIOR AS external_id,
                      SUPERIOR AS superior,
                      SUBORDINADO AS subordinados
                    FROM """ + data_base + """.EMPLEADO_JERARQUIA"""

            ip_conexion = "10.10.10.228"
            data_base = "TQC"
            user_bd = "vacaciones"
            pass_bd = "exvacaciones"

            table_bd = 'tqc.autorizadores'

            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)

            cursor = connection.cursor()
            cursor.execute(sql)
            idusers = cursor.fetchall()  # GUARDA TODOS LOS REGISTROS DE SQL

            nom_module = table_bd.replace(".", "_")

            for user in idusers:
                existId = True
                sumNom = "{}.{}".format(nom_module, user[0])  # (nombre modulo) + (id del sql)
                try:
                    # obtiene id de su respectivo modelo
                    id_register = self.env.ref(sumNom).id
                except ValueError:
                    existId = False

                # si existe actualiza el registro
                if existId:
                    exitSub = True
                    sumNomsub = "{}.{}".format('hr_employee', user[2])
                    try:
                        id_subord = self.env.ref(sumNomsub).id
                    except ValueError:
                        exitSub = False

                    if exitSub:
                        sudord_ids = self.env['tqc.autorizadores'].browse(id_register).subordinados.mapped('id')
                        if not (id_subord in sudord_ids):
                            # agrega a usuario nuevo
                            self.env['tqc.autorizadores'].browse(id_register).write({'subordinados': [(4, id_subord)]})
                            self.env.cr.commit()

                else:  # CREA NUEVO REGISTRO
                    sumNomsub = "{}.{}".format('hr_employee', user[0])  # (nombre modulo) + (id del sql)
                    try:
                        # obtiene id de su respectivo modelo
                        id_register = self.env.ref(sumNomsub).id

                        # Si existe contnuara desde here
                        sumNomsub = "{}.{}".format('hr_employee', user[2])
                        try:
                            id_subord = self.env.ref(sumNomsub).id
                            vjson = {'superior': id_register, 'subordinados': [(6, 0, [id_subord])]}
                        except ValueError:
                            vjson = {'superior': id_register}

                        original_id = self.env[table_bd].create(vjson).id
                        self.env.cr.commit()
                        # Si funciona
                        self.env["ir.model.data"].create(
                            {'name': user[0], 'module': nom_module, 'model': table_bd, 'res_id': original_id})
                        self.env.cr.commit()

                    except ValueError:
                        print("No validadeo")
            TqcAuth.sicronizar_auth(self)

    def cal_all_auth(self):
        # TRAE LOS NIVELES DE AUTHORIZATION
        # EMPIEZA EL CALCULO DE AUTORIZADORES
        all_employee = self.env["hr.employee"].search([])
        for rec in all_employee:
            superior = self.env["tqc.autorizadores"].search([('subordinados', "in", rec.id)])
            if superior:
                ids_superior = superior.mapped('superior').mapped('id')
                self.env["hr.employee"].browse(rec.id).sudo().write({'superior': [(6, 0, ids_superior)]})
                self.env.cr.commit()
            else:
                self.env["hr.employee"].browse(rec.id).sudo().write({'superior': False})
                self.env.cr.commit()

            subords = self.env["tqc.autorizadores"].search([('superior', '=', rec.id)])
            if subords:
                ids_subord = subords.mapped('subordinados').mapped('id')
                self.env["hr.employee"].browse(rec.id).sudo().write({'subordinados': [(6, 0, ids_subord)]})
                self.env.cr.commit()
            else:
                self.env["hr.employee"].browse(rec.id).sudo().write({'superior': False})
                self.env.cr.commit()

    # SINCRONIZAR EMPLEADOS CON SU RESPECTIVO AUTORIZADOR
    def sicronizar_auth(self):
        TqcAuth.cal_all_auth(self)
        TqcAuth.masive_auth(self)
        TqcAuthConta.masive_auth(self)

    # ACTUALIZA DE FORMA MASIVA EL GRUPO DE USUARIO APROBADOR Y EMPLEADO DE TODOS LOS EMPLEADOS
    def masive_auth(self):
        id_group_emple = self.env['res.groups'].search([('full_name', '=', 'Web de Gastos / Gasto-Empleado')]).id
        id_group_aprob = self.env['res.groups'].search([('full_name', '=', 'Web de Gastos / Gasto-Aprobador')]).id

        # OBTENGO ID DE CUENTAS ERP DE LOS EMPLEADOS VINCULADOS COMO APROADORES, NOTE: ENVIE LIST1 - LISTA DE ID DE JOBS
        listsup = self.env["tqc.autorizadores"].search([]).mapped("superior").mapped("user_id").mapped("id")
        # listsub = self.env["tqc.autorizadores"].search([]).mapped("subordinados").mapped("user_id").mapped("id")

        # ID DE LOS ADMIN
        ids_aprobador = self.env['res.groups'].sudo().search(
            [('full_name', '=', 'Web de Gastos / Gasto-Administrador')]).mapped("users").mapped("id")
        # ids_aprobador = self.env['res.groups'].sudo().search([('full_name', '=', 'Web de Gastos / Aprobador')]).mapped("users").mapped("id")
        # ids_aprobador = self.env['res.groups'].sudo().search([('full_name', '=', 'Web de Gastos / Empleado')]).mapped("users").mapped("id")

        # LISTA ABPROBADORES (RESTA DE DOS ARREGLOS, SE QUEDA CoN LA PRIMERA LISTA MENOS LOS REPETIDOS DE LA SEGUNDA)
        list_new_aprob = list(set(listsup).difference(set(ids_aprobador)))

        # CONVERTIR EN APROBADORES
        self.env['res.groups'].search([('id', '=', id_group_aprob)]).sudo().write(
            {'users': [(4, i) for i in list_new_aprob]})
        # QUITAR rol aprobador a EMPLEADOS
        self.env['res.groups'].search([('id', '=', id_group_emple)]).sudo().write(
            {'users': [(3, i) for i in list_new_aprob]})

        # AHORA CON LOS USUARIO NO ADMIN Y EMPLEADOS
        # ID DE USUARIOS no ADMIN
        ids_not_aprob = self.env["hr.employee"].search([('user_id.id', 'not in', listsup)]).mapped("user_id").mapped(
            "id")

        # RESTAMOS (LISTA DE EMPLEADOS - ADMIN)
        list_new_emple = list(set(ids_not_aprob).difference(set(ids_aprobador)))

        # CONVERTIR EN EMPLEADOS
        self.env['res.groups'].search([('id', '=', id_group_emple)]).sudo().write(
            {'users': [(4, i) for i in list_new_emple]})
        # QUITAR EN APROBADORES
        self.env['res.groups'].search([('id', '=', id_group_aprob)]).sudo().write(
            {'users': [(3, i) for i in list_new_emple]})


class TqcAuthConta(models.Model):
    _name = 'tqc.auth.contabilidad'
    _description = 'Autorizadores Contabilidad'

    empleado = fields.Many2one("hr.employee", string='Nombre', required=1)

    def masive_auth(self):
        id_group_emple = self.env['res.groups'].search([('full_name', '=', 'Web de Gastos / Gasto-Empleado')]).id
        id_group_aprob = self.env['res.groups'].search([('full_name', '=', 'Web de Gastos / Gasto-Contador')]).id

        # OBTENGO ID DE CUENTAS ERP DE LOS EMPLEADOS VINCULADOS COMO APROADORES, NOTE: ENVIE LIST1 - LISTA DE ID DE JOBS
        listsup = self.env["tqc.auth.contabilidad"].search([]).mapped("empleado").mapped("user_id").mapped("id")
        # listsub = self.env["tqc.autorizadores"].search([]).mapped("subordinados").mapped("user_id").mapped("id")

        # ID DE LOS ADMIN
        ids_aprobador = self.env['res.groups'].sudo().search(
            [('full_name', '=', 'Web de Gastos / Gasto-Administrador')]).mapped("users").mapped("id")
        # ids_aprobador = self.env['res.groups'].sudo().search([('full_name', '=', 'Web de Gastos / Aprobador')]).mapped("users").mapped("id")
        # ids_aprobador = self.env['res.groups'].sudo().search([('full_name', '=', 'Web de Gastos / Empleado')]).mapped("users").mapped("id")

        # LISTA ABPROBADORES (RESTA DE DOS ARREGLOS, SE QUEDA CoN LA PRIMERA LISTA MENOS LOS REPETIDOS DE LA SEGUNDA)
        list_new_aprob = list(set(listsup).difference(set(ids_aprobador)))

        # CONVERTIR EN APROBADORES
        self.env['res.groups'].search([('id', '=', id_group_aprob)]).sudo().write(
            {'users': [(4, i) for i in list_new_aprob]})
        # QUITAR rol aprobador a EMPLEADOS
        self.env['res.groups'].search([('id', '=', id_group_emple)]).sudo().write(
            {'users': [(3, i) for i in list_new_aprob]})

        # AHORA CON LOS USUARIO NO ADMIN Y EMPLEADOS
        # ID DE USUARIOS no ADMIN
        ids_not_aprob = self.env["hr.employee"].search([('user_id.id', 'not in', listsup)]).mapped("user_id").mapped(
            "id")

        # RESTAMOS (LISTA DE EMPLEADOS - ADMIN)
        list_new_emple = list(set(ids_not_aprob).difference(set(ids_aprobador)))

        # CONVERTIR EN EMPLEADOS
        self.env['res.groups'].search([('id', '=', id_group_emple)]).sudo().write(
            {'users': [(4, i) for i in list_new_emple]})
        # QUITAR EN APROBADORES
        self.env['res.groups'].search([('id', '=', id_group_aprob)]).sudo().write(
            {'users': [(3, i) for i in list_new_emple]})

class gastosEmployee(models.Model):
    _inherit = "hr.employee"

    superior = fields.Many2many("hr.employee", 'super_emple_rel', 'emple_id', 'sup_id',
                                string="Superior")  # relacionada foreigth key hr.department
    subordinados = fields.Many2many("hr.employee", 'super_subord_rel', 'sup_id', 'sub_id',
                                    string="Subordinados")  # relacionada foreigth key hr.department
