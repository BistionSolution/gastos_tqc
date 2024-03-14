# -*- coding: utf-8 -*-
from builtins import print

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime
import re, pyodbc
import logging

# import locale

# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

_logger = logging.getLogger(__name__)

database = 'TQCBKP2'
userbd = "TQC"
passbd = "extqc"


class Liquidaciones(models.Model):
    _name = 'tqc.liquidaciones'
    _description = 'Liquidaciones'

    name = fields.Char(compute='_get_name_soli')

    num_solicitud = fields.Char()
    empleado_name = fields.Many2one('hr.employee')
    centro_costo = fields.Many2one('hr.department', compute='_get_department')
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
        ('contable', 'Sin visto Contable'),
        ('jefatura', 'Sin visto jefe'),
        ('pendiente', 'Pendiente a procesar'),
        ('liquidado', 'Liquidado')
    ],
        default='habilitado', string='Estado Solicitud')

    aprobacioncontabilidad = fields.Boolean()
    ingresocompletado = fields.Boolean()

    muestreocontabilidad = fields.Boolean()

    detalleliquidaciones_id = fields.One2many('tqc.detalle.liquidaciones', 'liquidacion_id', 'Detalles',
                                              domain=lambda self: self._get_document_domain())
    detalle_historial = fields.One2many('tqc.detalle.liquidaciones', 'liquidacion_id', 'Detalles',
                                        domain=[('state', '=', 'historial')])

    entrega_a_rendir = fields.Char()
    fecha_entrega = fields.Date()
    glosa_entrega = fields.Text()
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  states={'reported': [('readonly', True)], 'approved': [('readonly', True)],
                                          'done': [('readonly', True)]}, compute='_compute_currency_id',
                                  default=lambda self: self.env.company.currency_id)

    monto_entrega = fields.Monetary(currency_field='currency_id')
    monto_rendido = fields.Monetary(currency_field='currency_id')

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
                                         ('corregir', 'Corregir y seguir'),
                                         ('liquidado', 'Liquidado')],
                                        default='habilitado', string='Proceso')
    mode_view = fields.Selection([('registro', 'Registro'),
                                  ('flujo', 'Flujo')],
                                 string='Modo de vista')

    table_depositos = fields.Html()

    current_user = fields.Integer(compute='_current_user')  # compute='_get_current_user', default=0
    uid_create = fields.Integer(compute='_get_current_user')
    user_id = fields.Integer(compute='_get_user_id')

    current_total = fields.Float(string='Current Total')

    # Verificar el monto total de detalleliquidaciones_id
    # @api.depends('detalleliquidaciones_id')
    # def _compute_amount(self):
    #     for record in self:
    #         record.current_total = sum(record.detalleliquidaciones_id.mapped('monto'))
    #
    @api.onchange('detalleliquidaciones_id')
    def _compute_amount(self):
        for record in self:
            # raise UserError(_('Se paso del saldo'))
            # print("RECORD : ", rec.detalleliquidaciones_id)
            # total = 0.0
            total = sum(record.detalleliquidaciones_id.mapped('total_neto'))
            for line in record.detalleliquidaciones_id:
                print("Monto : ", line.total_neto)
                if line.total_neto <= 0:
                    raise UserError(_('Monto menor a 0 o igua a 0'))
            #     # if line.revisado_state != 'liquidado':
            #     total += line.total_neto
            if total > record.saldo + (record.saldo * 0.05):
                print("SALODSO PASODSO")
                raise UserError(_('Se paso del saldo, ingrese un monto menor'))

    @api.onchange('detalleliquidaciones_id')
    def _onchange_detalles(self):
        for rec in self:
            print("DETALLES : ", rec.detalleliquidaciones_id)

    def _get_document_domain(self):
        context = self._context.copy() or {}
        # obtener valor de state en la siguiente vista

        if context.get("mode_view", False) == 'flujo':
            domain = []
            if self.state == 'contable':
                # Agregar un elemento a la lista con
                domain = []
            if self.state == 'pendiente':
                domain = []
            # if context.get("search_default_jefatura"):
            #     print("searhc JEGATURA")
        elif context.get("mode_view", False) == 'historial':
            domain = []
        elif context.get("mode_view", False) == 'registro':
            domain = [('state', '!=', 'historial')]
        else:
            domain = []
            # domain = [('state', '!=', 'historial')]

        return domain

    @api.depends('empleado_name')
    def _get_department(self):
        for record in self:
            if record.empleado_name.department_id:
                record.centro_costo = record.empleado_name.department_id.id
            else:
                record.centro_costo = False

    @api.depends()
    def _current_user(self):
        for record in self:

            if self.env.uid in record.empleado_name.superior.mapped('user_id').mapped('id'):
                record.current_user = 1
            else:
                record.current_user = 0

    @api.depends()
    def _get_user_id(self):
        for record in self:
            # print("SUPER ID  : ",record.empleado_name.user_id.id)
            # record.empleado_name.user_id.id
            record.user_id = record.empleado_name.user_id.id

    @api.depends()
    def _get_current_user(self):
        # data_id = model_obj._get_id('module_name', 'view_id_which_you_want_refresh')
        # view_id = model_obj.browse(data_id).res_id
        user_now = self.env.uid

        # ['|', ('empleado_name.superior.user_id', 'in', [self.env.uid]), ('empleado_name.user_id', '=', self.env.uid)]
        for record in self:
            # record.sudo().empleado_name.user_id.id == user_now) or
            if self.env.user.has_group('gastos_tqc.res_groups_administrator'):
                record.uid_create = 1
            elif self.env.user.has_group('gastos_tqc.res_groups_contador_gastos'):
                record.uid_create = 2
            elif self.env.user.has_group('gastos_tqc.res_groups_aprobador_gastos'):
                record.uid_create = 3
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

    def print_pdf(self):
        return self.env.ref('gastos_tqc.action_report_und_report_pendient').report_action(self)

    @api.model
    def importar_exactus(self):
        global dataExternalSQL
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        ip_conexion = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.ip_conexion')
        data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
        user_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.username_exactus')
        pass_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.password_exactus')

        table_bd = "tqc.liquidaciones"
        table_relations = """empleado_name OF hr.employee"""

        # sql_prime = """SELECT
        #                   ENTREGA_A_RENDIR AS external_id,
        #                   ENTREGA_A_RENDIR AS num_solicitud,
        #                   EMPLEADO AS empleado_name,
        #                   MONEDA AS moneda,
        #                   APLICACION AS glosa_entrega,
        #                   FECHA_ENTREGA AS fecha_entrega
        #                 FROM
        #                   tqc.ENTREGA_A_RENDIR
        #                 WHERE LIQUIDADO != 'S'"""

        sql_prime_super = """SELECT
                                  ENTREGA_A_RENDIR AS external_id,
                                  ENTREGA_A_RENDIR AS num_solicitud,
                                  EMPLEADO AS empleado_name,
                                  MONEDA AS moneda,
                                  APLICACION AS glosa_entrega,
                                  FECHA_ENTREGA AS fecha_entrega,
                                  CONVERT(decimal(10,2),MONTO) AS monto_entrega,
                                  CONVERT(decimal(10,2),SALDO) AS saldo,
                                  LIQUIDADO                                  
                                FROM
                                  tqc.ENTREGA_A_RENDIR
                                WHERE LIQUIDADO != 'S'"""

        try:
            connection = pyodbc.connect(
                'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)

            campList = ['external_id', 'num_solicitud', 'empleado_name', 'moneda', 'glosa_entrega', 'fecha_entrega',
                        'monto_entrega', 'saldo']
            # company_table = self.capturar_empresa_db(sql)  # capture table of company from exactus
            # if company_table CONTAIN "EMPLEADO" then logic calculate states of the employees ('CES')
            posiUser = []
            print("table_bd : ", table_bd)
            nom_module = table_bd.replace(".", "_")
            dataExternalSQL = self.get_external_field(
                table_relations)  # Devuelve un arreglo de los nombres de las tablas relacionadas
            print("dataExternalSQL : ", dataExternalSQL)
            for data in dataExternalSQL[0]:
                posiUser.append(campList.index(data))  # inicia posicion de elemento

            cursor = connection.cursor()
            cursor.execute(sql_prime_super)
            idusers = cursor.fetchall()  # GUARDA TODOS LOS REGISTROS DE SQL

            # current_locale = locale.getlocale()
            # print("LENGUAJE LOCAL : ", current_locale)
            # _logger.info('LENGUAJE extraAAAAAA')
            # _logger.info('LENGUAJE LOCAL : %s and %s' % (current_locale[0], current_locale[1]))

            for user in idusers:
                if user[1] == '000000017694':
                    _logger.info('VALOR TODO: ->>>>>>>>>>>>>>>>>>>>>>>>>> %s' % (user))
                    _logger.info('VALOR >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: %s' % (user[6]))
                    _logger.info('SALDO >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>: %s' % (user[7]))
                # user[6] = (user[6]) / 100
                # user[7] = (user[7]) / 100
                variJson = {}

                # register = self.env.ref(sumNom)  # obtiene id de su respectivo modelo
                # id_register = self.env.ref(sumNom).id
                id_register = self.env["ir.model.data"].sudo().search(
                    [('name', '=', user[0]), ('model', '=', table_bd)]).res_id

                register = self.env['tqc.liquidaciones'].sudo().browse(id_register)

                if id_register != 0:  # SI EXISTE ACTUALIZA
                    if user[1] == '000000017694':
                        _logger.info('here update -----------------> %s')
                    if register.habilitado_state == 'liquidado':  # si ya se encuentra liquidado crea otra liquidacion
                        if user[1] == '000000017694':
                            _logger.info('INTER LOIQUIDATED ---------->>>>>>>>>>>>> %s')
                        cont = 0
                        for i in range(len(campList)):  # recorre y relaciona los campos y datos para trasladar datos
                            if i == 0:
                                continue
                            if i in posiUser:  # cambia los nombres por los id correspondientes
                                if not user[i]:  # SI EL CAMPO NO TIENE RELACION(NULL) GUARDA FALSE
                                    id_exField = False
                                else:
                                    searchId = "{}.{}".format(dataExternalSQL[1][cont], user[i])
                                    try:
                                        # obtiene id de su respectivo modelo
                                        id_exField = self.env.ref(searchId).id
                                    except ValueError:
                                        id_exField = False

                                variJson['{}'.format(campList[i])] = id_exField
                                cont += 1
                                continue
                            variJson['{}'.format(campList[i])] = user[i]

                        original_id = self.env[table_bd].create(variJson).id
                        # Si funciona
                        self.env["ir.model.data"].sudo().search(
                            [('name', '=', register.num_solicitud), ('model', '=', 'tqc.liquidaciones')]).sudo().write(
                            {'res_id': original_id})
                        self.env.cr.commit()
                        cont = 0
                        for j in range(len(campList)):
                            # SOLO para validar correo repetidos en TQC #
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

                        self.env[table_bd].browse(id_register).sudo().write(variJson)
                        self.env.cr.commit()
                    if register.habilitado_state == 'habilitado':
                        variJsonNew = {}
                        print("user[8] : ", user[8])
                        if user[8] == 'S':
                            variJsonNew['habilitado_state'] = 'liquidado'
                        if user[1] == '000000017694':
                            _logger.info('actualizando ---------->>>>>>>>>>>>> %s')
                        variJsonNew['saldo'] = user[7]
                        print("variJsonNew : ", variJsonNew)
                        self.env[table_bd].browse(id_register).sudo().write(variJsonNew)
                        self.env.cr.commit()

                else:  # CREA NUEVO REGISTRO
                    if user[1] == '000000017694':
                        _logger.info('create new -----------------> %s')
                    cont = 0
                    for i in range(len(campList)):  # recorre y relaciona los campos y datos para trasladar datos
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

                    original_id = self.env[table_bd].sudo().create(variJson).id
                    # Si funciona
                    self.env["ir.model.data"].sudo().create(
                        {'name': user[0], 'module': nom_module, 'model': table_bd, 'res_id': original_id})
                    self.env.cr.commit()
        except Exception as e:
            raise UserError(_(e))

    @api.model
    def import_exactus(self):
        self.importar_exactus()
        res = {
            "name": "Liquidaciones",
            "type": "ir.actions.act_window",
            "res_model": "tqc.liquidaciones",
            "view_type": "form",
            "view_mode": "form,tree",
            "target": "current",
            'views': [(self.env.ref("gastos_tqc.view_tree_registro_gasto").id, 'tree'),
                      (self.env.ref("gastos_tqc.view_form_registro_gasto").id, 'form')],
            'domain': [('habilitado_state', '!=', 'liquidado')],
            "context": {'search_default_filtro_rendir': 1},
            'search_view_id': [self.env.ref("gastos_tqc.search_register_filter").id, 'search'],
            # 'clear_breadcrumb': True,
            # "nodestroy": True,
            'help': """
                            <p class="o_view_nocontent_smiling_face">
                                No hay registros para mostrar
                              </p><p>

                              </p>
                            """
        }
        return res

    @api.model
    def import_exactus_register(self):
        self.importar_exactus()
        uid = self.env.uid
        res = {
            "name": "Web Gastos",
            "type": "ir.actions.act_window",
            "res_model": "tqc.liquidaciones",
            "view_type": "form",
            "view_mode": "form,tree",
            "target": "current",
            'views': [(self.env.ref("gastos_tqc.view_tree_registro_gasto").id, 'tree'),
                      (self.env.ref("gastos_tqc.view_form_registro_gasto").id, 'form')],
            'domain': [('empleado_name.user_id', '=', uid), ('habilitado_state', '!=', 'liquidado')],
            "context": {'search_default_filtro_rendir': 1, 'mode_view': 'registro'},
            'search_view_id': [self.env.ref("gastos_tqc.search_register_filter").id, 'search'],
            # 'clear_breadcrumb': True,
            # "nodestroy": True,
            'help': """
                               <p class="o_view_nocontent_smiling_face">
                                   No hay registros para mostrar
                                 </p><p>

                                 </p>
                               """
        }
        return res

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

    # def _action_import_gastos(self):
    #     res = {
    #         "name": "Flujo de aprobaciones",
    #         "type": "ir.actions.act_window",
    #         "res_model": "tqc.liquidaciones",
    #         "view_type": "form",
    #         "view_mode": "tree,form",
    #
    #         'views': [(self.env.ref("gastos_tqc.view_tree_tqc_liquidaciones").id, 'tree'),
    #                   (self.env.ref("gastos_tqc.view_form_tqc_liquidaciones").id, 'form')],
    #         "search_view_id": self.env.ref("gastos_tqc.search_register_filter").id,
    #         "target": "current",
    #         "context": {'search_default_draft': True,
    #                     'create': False,
    #                     'delete': False},
    #         # "domain": [('warehouse_id.id', 'in', warehose_ids)],
    #         'help': """
    #                                         <p class="o_view_nocontent_smiling_face">
    #                                             Create a new operation type
    #                                           </p><p>
    #                                             The operation type system allows you to assign each stock
    #                                             operation a specific type which will alter its views accordingly.
    #                                             On the operation type you could e.g. specify if packing is needed by default,
    #                                             if it should show the customer.
    #                                           </p>
    #                                         """
    #     }
    #     return res

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

    # def _action_registro_gasto(self):
    #     name_employee = "Registro gastos"
    #     if (self.env.user.employee_id):
    #         name_employee = name_employee + " : " + self.env.user.employee_id.name + " | Centro de costo: " + self.env.user.employee_id.department_id.id_integrador + " - " + self.env.user.employee_id.department_id.name
    #     # employee_id
    #
    #     res = {
    #         "name": name_employee,
    #         "type": "ir.actions.act_window",
    #         "res_model": "tqc.liquidaciones",
    #         "sequence": 1,
    #         "view_type": "form",
    #         "view_mode": "form,tree",
    #         "search_view_id": (self.env.ref("gastos_tqc.search_register_filter").id,),
    #         'views': [[self.env.ref("gastos_tqc.view_tree_registro_gasto").id, 'tree'],
    #                   [self.env.ref("gastos_tqc.view_form_registro_gasto").id, 'form']],
    #         "target": "current",
    #         "nodestroy": False,
    #         "context": {'search_default_filtro_rendir': True,
    #                     },
    #         # "domain": [('warehouse_id.id', 'in', warehose_ids)],
    #         'help': """
    #                             <p class="o_view_nocontent_smiling_face">
    #                                 No hay registros para mostrar
    #                               </p><p>
    #
    #                               </p>
    #                             """
    #     }
    #     return res

    def generate_liquidacion(self):
        if self.detalleliquidaciones_id:
            vals = {
                'habilitado_state': 'proceso',
                'state': 'contable',
                'fecha_generacion': datetime.date.today(),
                'detalleliquidaciones_id': []
            }
            for doc in self.detalleliquidaciones_id:
                vals['detalleliquidaciones_id'].append([1, doc.id, {'state': 'historial'}])
            self.write(vals)
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'reload',
            # }
            return self.env.ref('gastos_tqc.action_report_und_report_pendient').report_action(self)
        else:
            raise UserError(_("Los documentos estan vacios"))
        # self.env["tqc.detalle.liquidaciones"].browse(self.id).write(
        #     {
        #         'state': 'historial'
        #     })

    def button_jefatura(self):
        if self.state == 'jefatura':
            self.write({'state': 'pendiente'})
            for doc in self.detalleliquidaciones_id:
                if doc.revisado_state not in ['liquidado', 'rechazado_jefatura', 'rechazado_contable',
                                              'observado_contable', 'observado_jefatura']:
                    doc.write({
                        'revisado_state': 'aprobado_jefatura'
                    })

    def button_contable(self):
        if self.state == 'contable':
            for doc in self.detalleliquidaciones_id:
                if doc.razonsocial_invisible == 'no_existe' and doc.revisado_state not in ['rechazado_jefatura',
                                                                                           'rechazado_contable']:
                    raise UserError(
                        _('Hay documentos donde el "Proveedor" no existe, cambiar de "Proveedor" o crear uno nuevo desde Exactus'))

            self.write({'state': 'jefatura'})
            for doc in self.detalleliquidaciones_id:
                if doc.revisado_state not in ['liquidado', 'rechazado_jefatura', 'rechazado_contable',
                                              'observado_contable', 'observado_jefatura']:
                    doc.write({
                        'revisado_state': 'aprobado_contable'
                    })

    def send_exactus(self):
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        ip_conexion = "10.10.10.228"
        data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
        user_bd = userbd
        pass_bd = passbd

        vals = {
            'detalleliquidaciones_id': []
        }

        try:
            connection = pyodbc.connect(
                'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                data_base + ';UID=' + user_bd + ';PWD=' + pass_bd + ';Encrypt=no')
            sql = """
            DECLARE	@return_value int,
                    @psDocumento varchar(20),
                    @psAsiento varchar(10),
                    @psMensajeError varchar(250)
            SELECT	@psDocumento = ?

            EXEC	@return_value = [tqc].[Exactus_CJ_Ingresar_ERC_Creditos]
                    @psConjunto = ?,
                    @psEntregaRendir = ?,
                    @psTipo = ?,
                    @psDocumento = @psDocumento OUTPUT,
                    @pnSubtipo = ?,
                    @pdtFecha = ?,
                    @pdtFechaContable = ?,
                    @psProveedor = ?,
                    @psRazonSocial = ?,
                    @psContribuyente = ?,
                    @psAplicacion = ?,
                    @psMoneda = ?,
                    @pnSubtotal = ?,
                    @pnDescuento = ?,
                    @pnImpuesto1 = ?,
                    @pnImpuesto2 = ?,
                    @pnRubro1 = ?,
                    @pnRubro2 = ?,
                    @pnMonto = ?,
                    @pnRetencion1 = ?,
                    @pnRetencion2 = ?,
                    @pnRetencion3 = ?,
                    @pnRetencion4 = ?,
                    @psCentroCosto = ?,
                    @psCuentaContable = ?,
                    @psCategoriaCaja = ?,
                    @psConsecutivoRecibo = ?,
                    @pdtFechaRecibo = ?,
                    @psRubro1Doc = ?,
                    @psRubro2Doc = ?,
                    @psRubro3Doc = ?,
                    @psRubro4Doc = ?,
                    @psRubro5Doc = ?,
                    @psRubro6Doc = ?,
                    @psRubro7Doc = ?,
                    @psRubro8Doc = ?,
                    @psRubro9Doc = ?,
                    @psRubro10Doc = ?,
                    @psCuentaBanco = ?,
                    @psNotas = ?,
                    @psUsuario = ?,
                    @psAsiento = @psAsiento OUTPUT,
                    @psMensajeError = @psMensajeError OUTPUT         
            
            SELECT	@psDocumento as N'@psDocumento',
                    @psAsiento as N'@psAsiento',
                    @psMensajeError as N'@psMensajeError'
            """

            monto_rendido = sum(self.detalleliquidaciones_id.mapped('totaldocumento'))

            for document in self.detalleliquidaciones_id:
                # == 'aprobado_contable'
                if document.revisado_state in ['aprobado_jefatura', 'aprobado_contable']:
                    values = (
                        (document.serie + "-" + document.numero) if document.numero and document.serie else None,
                        # Numero factura
                        'TQC',
                        self.num_solicitud,  # Numero de solicitud
                        document.tipodocumento.tipo,  # Tipó DE DOCUMENTO
                        document.tipodocumento.subtipo,  # Subtipo
                        document.fechaemision,  # fecha de emision del documento, Obligatorio.
                        self.fecha_contable,
                        # Fecha contable del documento. Si no se especifica, se asume igual que la fecha de emisión.
                        document.ruc,  # Ruc proveedor
                        document.proveedor_razonsocial,  # Razon social
                        document.ruc,  # Código del contribuyente
                        self.glosa_entrega,  # aplicación
                        document.moneda,  # Moneda
                        document.base_afecta,  # Monto del subtotal.
                        0,  # Monto del descuento.
                        document.montoigv,  # Monto del impuesto 1.
                        document.icbper,  # Monto del impuesto 2.
                        document.base_inafecta + document.otros_tributos,  # Monto del rubro 1.
                        0,  # Monto del rubro 2.
                        document.totaldocumento,
                        # Monto total del documento. Obligatorio. No puede ser cero. Total = Subtotal-Descuento+Impuesto1+Impuesto2+Rubro1+Rubro2-Retencion1-Retencion2-Retencion3-Retencion4.
                        0,  # Monto de la retención 1 (sólo válido para RHP). Opcional.
                        0,  # Monto de la retención 2 (sólo válido para RHP). Opcional.
                        0,  # Monto de la retención 3 (sólo válido para RHP). Opcional.
                        0,  # Monto de la retención 4 (RIGV) (sólo válido para FAC, B/V, N/D, N/C). Opcional.
                        self.centro_costo.id_integrador,  # Centro de costo de gasto.
                        document.cuenta_contable.codigo,
                        # Cuenta contable de gasto. Obligatorio si el subtipo no usa categoría de caja.
                        None,  # Código de la categoría de caja. Obligatorio si el subtipo usa categoría de caja.
                        None,
                        # Consecutivo para el comprobante de retención. Obligatorio sólo si la factura está afecta a retención de IGV.
                        document.fechaemision,
                        # Fecha para el comprobante de retención. Obligatorio sólo si la factura está afecta a retención de IGV.
                        None,  # Rubro 1 adicional del documento. Opcional.
                        None,  # Rubro 2 adicional del documento. Opcional.
                        None,  # Rubro 3 adicional del documento. Opcional.
                        None,  # Rubro 4 adicional del documento. Opcional.
                        None,  # Rubro 5 adicional del documento. Opcional.
                        None,  # Rubro 6 adicional del documento. Opcional.
                        None,  # Rubro 7 adicional del documento. Opcional.
                        None,  # Rubro 8 adicional del documento. Opcional.
                        None,  # Rubro 9 adicional del documento. Opcional.
                        None,  # Rubro 10 adicional del documento. Opcional.
                        None,  # Código de la cuenta bancaria. Obligatorio para depósito o devoluciones de efectivo.
                        document.observacionrepresentacion or '',  # NOTAS
                        'SA',  # Código del usuario de la transacción. Obligatorio. Por defecto: SA.
                        # self.state,  # Código del asiento generado por el documento.
                        # self.state  # Mensaje de error en caso ocurra un error en la transacción.
                    )
                    print("VALORES : ", values)
                    try:
                        cursor = connection.cursor()
                        cursor.execute(sql, values)
                        idusers = cursor.fetchone()
                        cursor.commit()
                        # idusers = cursor.fetchval()
                        cursor.close()
                    except Exception as e:
                        print("Error ", e)
                        vals['detalleliquidaciones_id'].append(
                            [1, document.id, {'revisado_state': 'send_error', 'message_error': f"Error sql :{e}"}])
                        continue

                    # Si no hay error cambia estado a liquidado
                    if idusers[1]:
                        vals['detalleliquidaciones_id'].append([1, document.id, {'revisado_state': 'liquidado'}])

                    else:
                        print("ERROR : ", idusers[2])
                        vals['detalleliquidaciones_id'].append(
                            [1, document.id, {'revisado_state': 'send_error', 'message_error': idusers[2]}])

            # Cambia estado de liquidacion
            vals['habilitado_state'] = 'liquidado'
            vals['state'] = 'liquidado'
            vals['monto_rendido'] = monto_rendido
            self.importar_exactus()
            self.write(vals)
            # res = {
            #     "name": "Historial de liquidaciones",
            #     "type": "ir.actions.act_window",
            #     "res_model": "tqc.liquidaciones",
            #     "view_type": "form",
            #     "view_mode": "tree, form",
            #     "res_id": self.id,
            #     "search_view_id": (self.env.ref("gastos_tqc.search_historial_filter").id,),
            #     'views': [
            #         [self.env.ref("gastos_tqc.view_form_historial_liquidaciones").id, 'form'],
            #         [self.env.ref("gastos_tqc.view_tree_historial_liquidaciones").id, 'tree']],
            #     "target": "main",
            #     # "context": {'no_breadcrumbs': True},
            #     'clear_breadcrumb': True,
            #     "nodestroy": True,
            #     'help': """
            #                             <p class="o_view_nocontent_smiling_face">
            #                                 No hay registros para mostrar
            #                               </p><p>
            #
            #                               </p>
            #                             """
            # }
            # return res

            # title = _("¡Envio exitoso!")
            # message = _("Se envio correctamente los documentos")
            # return {
            #     'type': 'ir.actions.client',
            #     'tag': 'display_notification',
            #     'params': {
            #         'title': title,
            #         'message': message,
            #         'sticky': False,
            #     }
            # }

        except Exception as e:
            raise UserError(_(e))

    def volver_enviar(self):
        self.env['tqc.detalle.liquidaciones'].search([('liquidacion_id', '=', self.id)]).write({
            'revisado_state': 'corregido',
            'state': 'historial'
        })
        self.write({
            'habilitado_state': 'proceso'
        })

    def historial_go(self):
        res = {
            "name": "Historial de Liquidaciones",
            "type": "ir.actions.act_window",
            "res_model": "tqc.liquidaciones",
            "view_type": "form",
            "view_mode": "tree, form",
            "res_id": self.id,
            "search_view_id": (self.env.ref("gastos_tqc.search_historial_filter").id,),
            'views': [
                [self.env.ref("gastos_tqc.view_form_historial_liquidaciones").id, 'form'],
                [self.env.ref("gastos_tqc.view_tree_historial_liquidaciones").id, 'tree']],
            "target": "main",
            # "context": {'no_breadcrumbs': True},
            'clear_breadcrumb': True,
            "nodestroy": True,
            'help': """
                            <p class="o_view_nocontent_smiling_face">
                                No hay registros para mostrar
                              </p><p>

                              </p>
                            """
        }
        return res

    @api.model
    def get_count_states(self, user_id):
        print("CORRE O NO CORRE")
        result = {
            'jefatura': 0,
            'contable': 0,
            'pendiente': 0
        }
        # public = self.env.ref('gastos_tqc.res_groups_aprobador_gastos')
        result['jefatura'] = self.env['tqc.liquidaciones'].with_user(user_id).search_count(
            [('state', 'in', ['jefatura']), ('habilitado_state', 'in', ['proceso'])])
        result['contable'] = self.env['tqc.liquidaciones'].with_user(user_id).search_count(
            [('state', 'in', ['contable']), ('habilitado_state', 'in', ['proceso'])])
        result['pendiente'] = self.env['tqc.liquidaciones'].with_user(user_id).search_count(
            [('state', 'in', ['pendiente']), ('habilitado_state', 'in', ['proceso'])])

        return result

    def search_ruc(self):
        pass

    def search_cod_client(self):
        pass

    @api.model
    def search_employee(self):
        user_now = self.env.uid
        print(user_now)
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', user_now)])
        if employee:
            return [employee.name, employee.department_id.name]
        else:
            return False
