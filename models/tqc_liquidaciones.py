# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, date, timedelta, time
import re, pyodbc

class Liquidaciones(models.Model):
    _name = 'tqc.liquidaciones'
    _description = 'Liquidaciones'

    name = fields.Char(compute='_get_name_soli')

    num_solicitud = fields.Char()
    empleado_name = fields.Many2one('hr.employee')
    centro_costo = fields.Many2one('hr.department')
    observacionenvio = fields.Text()
    numeroplaca = fields.Char()

    # useraprobacionjefatura_id = fields.Char()
    # fechaaprobacionjefatura = fields.Datetime()

    # aprobacionrecepcionoficina = fields.Boolean()
    # observacionrecepcionoficina = fields.Text()

    # useraprobacioncontabilidad_id = fields.Text()
    # fechaaprobacioncontabilidad = fields.Datetime()

    state = fields.Selection([
        ('habilitado', 'habilitado'),
        ('jefatura', 'Sin visto jefe'),
        ('contable', 'Sin visto Contable'),
        ('pendiente', 'Pediente a procesar')],
        default='habilitado', string='Estado Solicitud')

    aprobacioncontabilidad = fields.Boolean()
    ingresocompletado = fields.Boolean()

    muestreocontabilidad = fields.Boolean()
    tipoliquidacion_id = fields.Many2one('tqc.tipo.liquidaciones',
                                         default=lambda self: self.env['tqc.tipo.liquidaciones'].search(
                                             [('name', '=', 'A rendir')]))
    detalleliquidaciones_id = fields.One2many('tqc.detalle.liquidaciones', 'liquidacion_id')

    entrega_a_rendir = fields.Char()
    fecha_entrega = fields.Date()
    glosa_entrega = fields.Text()
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  states={'reported': [('readonly', True)], 'approved': [('readonly', True)],
                                          'done': [('readonly', True)]}, compute='_compute_currency_id',
                                  default=lambda self: self.env.company.currency_id)

    monto_entrega = fields.Monetary(currency_field='currency_id')

    aprobacionrecepcioncontabilidad = fields.Boolean()
    observacionrecepcioncontabilidad = fields.Text()
    fecharecepcioncontabilidad = fields.Datetime()
    userrecepcioncontabilidad_id = fields.Many2one('res.user')

    inferfazexactus = fields.Boolean()
    fecha_contable = fields.Date()
    fecha_generacion = fields.Datetime()

    centro_costo_descripcion = fields.Char()
    saldo = fields.Monetary(currency_field='currency_id')
    moneda = fields.Char()

    tipo_documento = fields.Selection([('a_rendir', 'A rendir'),
                                       ('tarjeta_credito', 'Tarjeta Crédito')],
                                      default='a_rendir', string='Tipo documento')

    habilitado_state = fields.Selection([('habilitado', 'Habilitado para liquidar'),
                                         ('proceso', 'Proceso de liquidacion'),
                                         ('corregir', 'Corregir y seguir')],
                                        default='habilitado', string='Proceso')
    mode_view = fields.Selection([('registro', 'Registro'),
                                  ('flujo', 'Flujo')],
                                 string='Modo de vista')

    table_depositos = fields.Html()

    current_user_uid = fields.Integer() #compute='_get_current_user', default=0
    uid_create = fields.Integer(compute='_get_current_user')
    current_total = fields.Float(string='Current Total', compute='_compute_amount')

    @api.depends('detalleliquidaciones_id')
    def _compute_amount(self):
        for rec in self:
            print("provando ")
            total = 0.0
            for line in rec.detalleliquidaciones_id:
                total += line.totaldocumento
            if total > rec.saldo:
                raise UserError(_('Se paso del saldo'))
            rec.current_total = total

    # @api.onchange('detalleliquidaciones_id')
    # def _onchange_amount(self):
    #     for rec in self:
    #         print("provando ")
    #         total = 0.0
    #         for line in rec.detalleliquidaciones_id:
    #             total += line.totaldocumento
    #         rec.current_total = total

    @api.depends()
    def _get_current_user(self):
        active_ids = self.env.context.get('active_ids', [])
        print("model ", active_ids)
        # data_id = model_obj._get_id('module_name', 'view_id_which_you_want_refresh')

        # view_id = model_obj.browse(data_id).res_id
        user_now = self.env.uid
        for record in self:
            # record.sudo().empleado_name.user_id.id == user_now) or
            if self.env.user.has_group('gastos_tqc.res_groups_administrator'):
                record.uid_create = 1
            elif self.env.user.has_group('gastos_tqc.res_groups_aprobador_gastos'):
                record.uid_create = 3
            elif self.env.user.has_group('gastos_tqc.res_groups_contador_gastos'):
                record.uid_create = 2
            else:
                record.uid_create = 0

            ##### NUEVA LOGICA
            # record.auth_one = record.id_trabajador.auth_one.id
            # record.auth_two = record.id_trabajador.auth_one.id
            # record.auth_three = record.id_trabajador.auth_one.id

            # super = record.sudo().empleado_name.superior.user_id.id
            # if super == user_now:
            #     record.current_user_uid = 1
            # else:
            #     record.current_user_uid = 0

    @api.depends('num_solicitud')
    def _get_name_soli(self):
        for rec in self:
            if rec.num_solicitud:
                rec.name = rec.num_solicitud
            else:
                rec.name = False

    @api.model
    def default_get(self, default_fields):
        return super(Liquidaciones, self).default_get(default_fields)

    @api.model
    def importar_exactus(self):
        ip_conexion = "10.10.10.228"
        data_base = "TQC"
        user_bd = "vacaciones"
        pass_bd = "exvacaciones"
        table_bd = "tqc.liquidaciones"
        table_relations = """empleado_name OF hr.employee"""

        sql_prime = """SELECT
                          ENTREGA_A_RENDIR AS external_id,
                          ENTREGA_A_RENDIR AS num_solicitud,
                          EMPLEADO AS empleado_name,
                          MONEDA AS moneda,
                          APLICACION AS glosa_entrega,
                          FECHA_ENTREGA AS fecha_entrega,
                          CONVERT(decimal(10,2),MONTO) AS monto_entrega,
                          CONVERT(decimal(10,2),SALDO) AS saldo
                        FROM
                          tqc.ENTREGA_A_RENDIR
                        WHERE LIQUIDADO = 'N'"""

        sql = """SELECT
                  ENTREGA_A_RENDIR AS external_id,
                  ENTREGA_A_RENDIR AS num_solicitud,
                  EMPLEADO AS empleado_name,
                  MONEDA AS moneda,
                  APLICACION AS glosa_entrega,
                  FECHA_ENTREGA AS fecha_entrega,
                  MONTO AS monto_entrega,
                  SALDO AS saldo
                FROM
                  tqc.ENTREGA_A_RENDIR
                WHERE LIQUIDADO = 'N'"""
        try:
            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
            if "SELECT" in sql:
                campList = self.convert_sql(sql)  # lista de campos odoo
                company_table = self.capturar_empresa_db(sql)  # capture table of company from exactus
                # if company_table CONTAIN "EMPLEADO" then logic calculate states of the employees ('CES')
                posiUser = []
                nom_module = table_bd.replace(".", "_")
                if table_relations:
                    dataExternalSQL = self.get_external_field(
                        table_relations)  # Devuelve un arreglo de los nombres de las tablas relacionadas
                    for data in dataExternalSQL[0]:
                        posiUser.append(campList.index(data))  # inicia posicion de elemento

                cursor = connection.cursor()
                cursor.execute(sql_prime)
                idusers = cursor.fetchall()  # GUARDA TODOS LOS REGISTROS DE SQL

                for user in idusers:
                    user[6] = (user[6]) / 100
                    user[7] = (user[7]) / 100
                    variJson = {}
                    work_email = False  # comprueba si tiene Correo, sino no llena
                    existId = True

                    sumNom = "{}.{}".format(nom_module, user[0])  # (nombre modulo) + (id del sql)
                    try:
                        register = self.env.ref(sumNom)  # obtiene id de su respectivo modelo
                        id_register = self.env.ref(sumNom).id
                    except ValueError:
                        existId = False

                    if existId:  # SI EXISTE ACTUALIZA
                        # ACTUALIZA REGISTRO
                        cont = 0
                        no_register = False

                        for j in range(len(campList)):
                            ## SOLO para validar correo repetidos en TQC ##
                            ## HASTA AQUI ##
                            if j == 0:
                                continue
                            # LLAVE FORANEA ENLACE
                            if j in posiUser:  # cambia los nombres por los id correspondientes, # GUARDA CORRESPONDENCIA ONE2MANY
                                if not user[j]:
                                    id_exField = False
                                else:
                                    searchId = "{}.{}".format(dataExternalSQL[1][cont], user[j])
                                    try:
                                        # obtiene id de su respectivo modelo
                                        id_exField = self.env.ref(searchId).id
                                    except ValueError:
                                        id_exField = False
                                    #
                                variJson['{}'.format(campList[j])] = id_exField
                                cont += 1
                                continue

                            variJson['{}'.format(campList[j])] = user[j]
                            res = {"success"}

                        if not no_register:  # si no cumple con los campos de usuarios no registra
                            self.env[table_bd].browse(id_register).sudo().write(variJson)
                            self.env.cr.commit()

                    else:  # CREA NUEVO REGISTRO
                        cont = 0
                        no_register = False  # PARA REGISTRAR
                        for i in range(len(campList)):  # recorre y relaciona los campos y datos para trasladar datos
                            try:
                                ## SOLO para validar correo repetidos en TQC ##
                                if (table_bd == 'res.users') and ('@' in user[i]):  # CORREO VALIDACION TQC
                                    if ";" in user[i]:
                                        user[i] = re.split(r'[;]', user[i])
                                    else:
                                        user[i] = re.split(r'[,]', user[i])
                                    user[i] = user[i][0]
                                    exist_mail = self.env["res.users"].search(
                                        [('login', '=', user[i]), ('id', '!=', int(id_register))])
                                    self.env.cr.commit()
                                    if exist_mail:
                                        no_register = True
                                        break
                                    if company_table == 'tqc.EMPLEADO':
                                        if 'tqc.com.pe' not in user[i]:
                                            no_register = True
                                            break
                                    elif company_table == 'TALEX.EMPLEADO':
                                        if 'talex.com.pe' not in user[i]:
                                            if 'tqc.com.pe' not in user[i]:
                                                no_register = True
                                                break
                                    elif company_table == 'SEMILLAS.EMPLEADO':
                                        if 'tqcsemillas.com.pe' not in user[i]:
                                            if 'tqc.com.pe' not in user[i]:
                                                no_register = True
                                                break
                                    else:  # PARA BIOGEN.EMPLEADO
                                        if 'biogenagro.com' not in user[i]:
                                            if 'tqc.com.pe' not in user[i]:
                                                no_register = True
                                                break
                                ##################
                                ## SOLO PARA CORREO DE TQC EMPLEADOS
                                if table_bd == 'hr.employee' and '@' in user[i]:  # CORREO VALIDADCION TQC
                                    if ";" in user[i]:
                                        user[i] = re.split(r'[;]', user[i])
                                    else:
                                        user[i] = re.split(r'[,]', user[i])
                                    user[i] = user[i][0]
                                    work_email = user[i]
                                ##################
                            except:
                                print("encontro fecha, no puede comparar")
                            if i == 0:
                                continue
                            if i in posiUser:  # cambia los nombres por los id correspondientes
                                if not user[i]:  # SI EL CAMPO NO TIENE RELACION(NULL) GUARDA FALSE
                                    id_exField = False
                                else:

                                    searchId = "{}.{}".format(dataExternalSQL[1][cont], user[i])
                                    #
                                    try:
                                        # obtiene id de su respectivo modelo
                                        id_exField = self.env.ref(searchId).id
                                    except ValueError:
                                        id_exField = False

                                variJson['{}'.format(campList[i])] = id_exField
                                cont += 1
                                continue
                            variJson['{}'.format(campList[i])] = user[i]

                        if not no_register:
                            original_id = self.env[table_bd].create(variJson).id
                            # Si funciona
                            self.env["ir.model.data"].sudo().create(
                                {'name': user[0], 'module': nom_module, 'model': table_bd, 'res_id': original_id})
                            self.env.cr.commit()
        except Exception as e:
            print("NADA")

    @api.model
    def create(self, vals):
        if "TARJETA" in str(vals.get("glosa_entrega")):
            vals['tipo_documento'] = 'tarjeta_credito'
        else:
            vals['tipo_documento'] = 'a_rendir'
        res = super(Liquidaciones, self).create(vals)
        return res

    @api.model
    def get_expense_dashboard(self):
        v_draf = len(self.env['tqc.liquidaciones'].search([('state', '=', 'habilitado')]))
        v_jefatura = len(self.env['tqc.liquidaciones'].search([('state', '=', 'jefatura')]))
        v_contable = len(self.env['tqc.liquidaciones'].search([('state', '=', 'contable')]))
        expense_state = {
            'habilitado': {
                'description': _('Sin visto Jefe'),
                'amount': v_draf,
                'currency': self.env.company.currency_id.id,
            },
            'reported': {
                'description': _('Sin visto contable'),
                'amount': v_jefatura,
                'currency': self.env.company.currency_id.id,
            },
            'approved': {
                'description': _('Pendientes a procesar'),
                'amount': v_contable,
                'currency': self.env.company.currency_id.id,
            }
        }
        # if not self.env.user.employee_ids:
        #     return expense_state
        # target_currency = self.env.company.currency_id
        # expenses = self.read_group(
        #     [
        #         ('employee_id', 'in', self.env.user.employee_ids.ids),
        #         ('payment_mode', '=', 'own_account'),
        #         ('state', 'in', ['draft', 'reported', 'approved'])
        #     ], ['total_amount', 'currency_id', 'state'], ['state', 'currency_id'], lazy=False)
        # for expense in expenses:
        #     state = expense['state']
        #     currency = self.env['res.currency'].browse(expense['currency_id'][0]) if expense[
        #         'currency_id'] else target_currency
        #     amount = currency._convert(
        #         expense['total_amount'], target_currency, self.env.company, fields.Date.today())
        #     expense_state[state]['amount'] += amount
        return expense_state

    @api.depends("moneda")
    def _compute_currency_id(self):
        for rec in self:
            if rec.moneda == 'USD':
                rec.currency_id = 2

    def _action_import_gastos(self):
        res = {
            "name": "Flujo de aprobaciones",
            "type": "ir.actions.act_window",
            "res_model": "tqc.liquidaciones",
            "view_type": "form",
            "view_mode": "tree,form",

            'views': [(self.env.ref("gastos_tqc.view_tree_tqc_liquidaciones").id, 'tree'),
                      (self.env.ref("gastos_tqc.view_form_tqc_liquidaciones").id, 'form')],
            "search_view_id": self.env.ref("gastos_tqc.search_register_filter").id,
            "target": "current",
            "context": {'search_default_draft': True,
                        'create': False,
                        'delete': False},
            # "domain": [('warehouse_id.id', 'in', warehose_ids)],
            'help': """
                                            <p class="o_view_nocontent_smiling_face">
                                                Create a new operation type
                                              </p><p>
                                                The operation type system allows you to assign each stock
                                                operation a specific type which will alter its views accordingly.
                                                On the operation type you could e.g. specify if packing is needed by default,
                                                if it should show the customer.
                                              </p>
                                            """
        }
        return res

    def convert_sql(self, frase):
        variJson = []
        frase_express = frase.replace("SELECT", "").replace("WHERE", "$").replace("FROM", "$").replace("\n",
                                                                                                       "").replace(
            "\r", "")
        parte_frase = re.split(r'[$]', frase_express)
        variables = parte_frase[0].replace(" AS ", ",").replace(" ", "")
        campos = re.split(r'[,\s]\s*', variables)
        cant = int(len(campos) / 2)
        for i in range(cant):
            variJson.append(campos[(i * 2) + 1])

        # AHORA PARA CADA BASE DE DATOS, CADA EMPRESA
        empresa_bd = parte_frase[1].replace(" ", "")
        return variJson

    def capturar_empresa_db(self, frase):
        frase_express = frase.replace("SELECT", "").replace("WHERE", "$").replace("FROM", "$").replace("\n",
                                                                                                       "").replace("\r",
                                                                                                                   "")
        parte_frase = re.split(r'[$]', frase_express)
        company_table = parte_frase[1].replace(" ", "")
        return company_table

    def get_external_field(self, arrExternal):
        # traemos los nombres de los campos q se desea reemplazar id
        refOther = arrExternal.replace("OF", ",").replace(" ", "").replace("\n", "").replace(".", "_").replace("\r", "")
        Other1 = []
        Other2 = []
        sumex = []
        ultOther = re.split(r'[,\s]\s*', refOther)

        if not refOther:
            sumex = []
        else:
            for i in range(int(len(ultOther) / 2)):
                Other1.append(ultOther[i * 2])
                Other2.append(ultOther[(i * 2) + 1])

            sumex.append(Other1)
            sumex.append(Other2)

        return sumex

    def _action_registro_gasto(self):
        name_employee = "Registro gastos"
        if (self.env.user.employee_id):
            name_employee = name_employee + " : " + self.env.user.employee_id.name + " | Centro de costo: " + self.env.user.employee_id.department_id.id_integrador + " - " + self.env.user.employee_id.department_id.name
        # employee_id

        res = {
            "name": name_employee,
            "type": "ir.actions.act_window",
            "res_model": "tqc.liquidaciones",
            "sequence": 1,
            "view_type": "form",
            "view_mode": "form,tree",
            "search_view_id": (self.env.ref("gastos_tqc.search_register_filter").id,),
            'views': [[self.env.ref("gastos_tqc.view_tree_registro_gasto").id, 'tree'],
                      [self.env.ref("gastos_tqc.view_form_registro_gasto").id, 'form']],
            "target": "current",
            "nodestroy": False,
            "context": {'search_default_filtro_rendir': True,
                        },
            # "domain": [('warehouse_id.id', 'in', warehose_ids)],
            'help': """
                                <p class="o_view_nocontent_smiling_face">
                                    No hay registros para mostrar
                                  </p><p>
                                    
                                  </p>
                                """
        }
        return res

    def generate_liquidacion(self):
        if self.detalleliquidaciones_id:
            ids = self.detalleliquidaciones_id.mapped('id')
            print("VAMOSSS es :", datetime.today())
            self.write({
                'habilitado_state': 'proceso',
                'state': 'jefatura',
                'fecha_generacion': datetime.today()
            })

            for id in ids:
                self.env["tqc.detalle.liquidaciones"].browse(id).write(
                    {
                        'state': 'historial'
                    })
        else:
            raise UserError(_("Los documentos estan vacios"))
        # self.env["tqc.detalle.liquidaciones"].browse(self.id).write(
        #     {
        #         'state': 'historial'
        #     })

    def button_jefatura(self):
        if self.state == 'jefatura':
            self.write({'state': 'contable'})

    def button_contable(self):
        if self.state == 'contable':
            self.write({'state': 'pendiente'})

    def volver_enviar(self):
        self.env['tqc.detalle.liquidaciones'].search([('liquidacion_id', '=', self.id)]).write({
            'revisado_state': 'corregido',
            'state': 'historial'
        })
        self.write({
            'habilitado_state': 'proceso'
        })

    @api.model
    def get_count_states(self):
        jefatura = self.env['tqc.liquidaciones'].search_count([('state', 'in', ['jefatura'])])
        contable = self.env['tqc.liquidaciones'].search_count([('state', 'in', ['contable'])])
        pendiente = self.env['tqc.liquidaciones'].search_count([('state', 'in', ['pendiente'])])
        return [jefatura, contable, pendiente]

    def search_ruc(self):
        pass

    def search_cod_client(self):
        pass
