# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re, pyodbc

class Liquidaciones(models.Model):
    _name = 'tqc.liquidaciones'
    _description = 'Liquidaciones'

    num_solicitud = fields.Char()
    empleado_id = fields.Many2one('hr.employee')
    empleado_name = fields.Char()
    centro_costo = fields.Char()
    observacionenvio = fields.Text()
    numeroplaca = fields.Char()

    # useraprobacionjefatura_id = fields.Char()
    # fechaaprobacionjefatura = fields.Datetime()

    # aprobacionrecepcionoficina = fields.Boolean()
    # observacionrecepcionoficina = fields.Text()

    # useraprobacioncontabilidad_id = fields.Text()
    # fechaaprobacioncontabilidad = fields.Datetime()

    state = fields.Selection([
        ('draft', 'Sin visto jefe'),
        ('jefatura', 'Autorizacion jefatura'),
        ('contable', 'Visto Contable')],
        default='draft', string='Estado Solicitud')

    aprobacioncontabilidad = fields.Boolean()
    ingresocompletado = fields.Boolean()

    muestreocontabilidad = fields.Boolean()
    tipoliquidacion_id = fields.Many2one('tqc.tipo.liquidaciones', default=lambda self: self.env['tqc.tipo.liquidaciones'].search([('name','=','A rendir')]))
    detalleliquidaciones_id = fields.One2many('tqc.detalle.liquidaciones','liquidacion_id')

    entrega_a_rendir = fields.Char()
    fecha_entrega = fields.Date()
    glosa_entrega = fields.Text()
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  states={'reported': [('readonly', True)], 'approved': [('readonly', True)],
                                          'done': [('readonly', True)]}, compute='_compute_currency_id', default=lambda self: self.env.company.currency_id)

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

    table_depositos = fields.Html()

    @api.model
    def get_expense_dashboard(self):
        v_draf = len(self.env['tqc.liquidaciones'].search([('state','=','draft')]))
        v_jefatura = len(self.env['tqc.liquidaciones'].search([('state','=','jefatura')]))
        v_contable = len(self.env['tqc.liquidaciones'].search([('state','=','contable')]))
        expense_state = {
            'draft': {
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
        ip_conexion = "10.10.10.228"
        data_base = "TQC"
        user_bd = "vacaciones"
        pass_bd = "exvacaciones"
        table_bd = "tqc.liquidaciones"
        table_relations = ""
        sql_prime = """SELECT
                  ENTREGA_A_RENDIR AS external_id,
                  ENTREGA_A_RENDIR AS num_solicitud,
                  EMPLEADO AS empleado_name,
                  MONEDA AS moneda,
                  APLICACION AS glosa_entrega,
                  FECHA_ENTREGA AS fecha_entrega,
                  CAST(MONTO as decimal(10,2)) AS monto_entrega,
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
                    dataExternalSQL = self.get_external_field(table_relations)  # Devuelve un arreglo de los nombres de las tablas relacionadas
                    for data in dataExternalSQL[0]:
                        posiUser.append(campList.index(data))  # inicia posicion de elemento

                cursor = connection.cursor()
                cursor.execute(sql_prime)
                idusers = cursor.fetchall()  # GUARDA TODOS LOS REGISTROS DE SQL

                for user in idusers:
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
                            #############
                            try:
                                # if table_bd == 'hr.employee' and (str(user[j]) == '1980-01-01 00:00:00'):
                                #     user[j] = False
                                if table_bd == 'res.users' and '@' in user[j]:  # CORREO VALIDACION TQC
                                    if ";" in user[j]:
                                        user[j] = re.split(r'[;]', user[j])
                                    else:
                                        user[j] = re.split(r'[,]', user[j])
                                    user[j] = user[j][0]
                                    exist_mail = self.env["res.users"].search(
                                        [('login', '=', user[j]), ('id', '!=', int(id_register))])
                                    self.env.cr.commit()
                                    if exist_mail:
                                        no_register = True
                                        break
                                    if company_table.lower() == 'tqc.empleado':
                                        if 'tqc.com.pe' not in user[j]:
                                            no_register = True
                                            break
                                    elif company_table.lower() == 'talex.empleado':
                                        if 'talex.com.pe' not in user[j]:
                                            if 'tqc.com.pe' not in user[j]:
                                                no_register = True
                                                break
                                    elif company_table.lower() == 'semillas.empleado':
                                        if 'tqcsemillas.com.pe' not in user[j]:
                                            if 'tqc.com.pe' not in user[j]:
                                                no_register = True
                                                break
                                    else:  # PARA BIOGEN.EMPLEADO
                                        if 'biogenagro.com' not in user[j]:
                                            if 'tqc.com.pe' not in user[j]:
                                                no_register = True
                                                break
                                if (table_bd == 'hr.employee') and ('@' in user[j]):
                                    if ";" in user[j]:
                                        user[j] = re.split(r'[;]', user[j])
                                    else:
                                        user[j] = re.split(r'[,]', user[j])
                                    user[j] = user[j][0]
                                    work_email = user[j]

                            except:
                                print("encontro una fecha, no puede comparar")
                            ##################
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

                        if not no_register: # si no cumple con los campos de usuarios no registra
                            self.env[table_bd].browse(id_register).write(variJson)
                            self.env.cr.commit()

                            # ACTUALIZA CONTACTO EL CORREO
                            if table_bd == 'res.users':
                                # en respartner tr
                                self.env["res.partner"].search([('user_ids', 'in', [id_register])]).write(
                                    {'email': variJson['login']})
                                self.env.cr.commit()

                            if table_bd == 'hr.employee' and work_email:
                                self.env[table_bd].browse(id_register).write(
                                    {'work_email': work_email, 'work_phone': '999999999'})
                                self.env.cr.commit()

                        print("ESTE VARI JSON : ",variJson)
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
                        res = variJson
                        if no_register:
                            print("no registro el registro")
                        else:
                            original_id = self.env[table_bd].create(variJson).id
                            # Si funciona
                            self.env["ir.model.data"].create(
                                {'name': user[0], 'module': nom_module, 'model': table_bd, 'res_id': original_id})
                            self.env.cr.commit()

                            if table_bd == 'hr.employee' and work_email:
                                self.env[table_bd].browse(original_id).write(
                                    {'work_email': work_email, 'work_phone': '999999999'})
                                self.env.cr.commit()

                # update employee cesados ('CES')
                # if 'empleado' in company_table.lower():
                if 'xdvdx' in company_table.lower():
                    try:
                        connection2 = pyodbc.connect(
                            'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                            data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                        all_employees = self.env['hr.employee'].search([]).mapped('id_integrador')
                        for empl in all_employees:
                            if empl:
                                cursor2 = connection2.cursor()
                                cursor2.execute(
                                    "SELECT ESTADO_EMPLEADO,FECHA_SALIDA FROM " + company_table + " WHERE EMPLEADO = '" + empl + "'")
                                stado = cursor2.fetchall()
                                if stado:
                                    for st in stado:
                                        if st[0] == 'CES':
                                            self.env['hr.employee'].search(
                                                [('id_integrador', '=', empl)]).write({'stado': 'CES', 'finish_job': st[1]})
                                            self.env.cr.commit()
                    except Exception as e:
                        raise ValidationError("error here correctamente")

            res = {
                "name": "Flujo de aprobaciones",
                "type": "ir.actions.act_window",
                "res_model": "tqc.liquidaciones",
                "view_type": "form",
                "view_mode": "tree,form",
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
        except Exception as e:
            res = {
                "name": "Flujo de aprobaciones",
                "type": "ir.actions.act_window",
                "res_model": "tqc.liquidaciones",
                "view_type": "form",
                "view_mode": "tree,form",
                "search_view_id": self.env.ref("gastos_tqc.search_register_filter").id,
                "target": "current",
                "context": {'search_default_draft': True,
                            'create': False,
                            'delete':False
                            },
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
        frase_express = frase.replace("SELECT", "").replace("WHERE", "$").replace("FROM", "$").replace("\n","").replace("\r","")
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
        try:
            form_view_id = self.env.ref("gastos_tqc.view_form_registro_gasto").id
            tree_view_id = self.env.ref("gastos_tqc.view_tree_registro_gasto").id
            search_view_id = self.env.ref("gastos_tqc.search_register_filter").id
        except Exception as e:
            form_view_id = False
            tree_view_id = False
            search_view_id = False

        name_employee = "Registro gasto"
        if (self.env.user.employee_id):
            name_employee = name_employee + " : " + self.env.user.employee_id.name + " | Centro de costo: " +self.env.user.employee_id.department_id.id_integrador+" - " +self.env.user.employee_id.department_id.name
        # employee_id

        res = {
            "name": name_employee,
            "type": "ir.actions.act_window",
            "res_model": "tqc.liquidaciones",
            "view_type": "form",
            "view_mode": "tree,form",
            "search_view_id": (self.env.ref("gastos_tqc.search_register_filter").id,),
            'views': [(tree_view_id, 'tree'),(form_view_id, 'form')],
            "target": "current",
            "context": {'search_default_filtro_rendir': True,
                        'create': False,
                        'delete': False},
            # "domain": [('warehouse_id.id', 'in', warehose_ids)],
            'help': """
                                <p class="o_view_nocontent_smiling_face">
                                    No hay registros para mostrar
                                  </p><p>
                                    
                                  </p>
                                """
        }
        return res

class detalleLiquidaciones(models.Model):
    _name = 'tqc.detalle.liquidaciones'
    _description = 'Detalle de Liquidaciones'

    liquidacion_id = fields.Many2one('tqc.liquidaciones')
    tipo = fields.Char()
    subtipo = fields.Char()
    serie = fields.Char()
    numero = fields.Char()
    ruc = fields.Char()
    moneda = fields.Char()
    tipocambio = fields.Integer()
    fechaemision = fields.Date()

    base_afecta = fields.Monetary(currency_field='currency_id')
    base_inafecta = fields.Monetary(currency_field='currency_id')
    montoigv = fields.Monetary(currency_field='currency_id')
    totaldocumento = fields.Monetary(currency_field='currency_id')

    cuenta_contable = fields.Many2one('cuenta.contable.gastos')
    observacionrepresentacion = fields.Text()
    nocliente = fields.Char()

    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  states={'reported': [('readonly', True)], 'approved': [('readonly', True)],
                                          'done': [('readonly', True)]}, compute='_compute_currency_id',
                                  default=lambda self: self.env.company.currency_id)

    useraprobacionjefatura = fields.Integer()
    fechaaprobacionjefatura = fields.Datetime()
    aprobacionjefatura = fields.Boolean()
    observacionjefatura = fields.Text()

    useraprobacioncontabilidad = fields.Integer()
    fechaaprobacioncontabilidad = fields.Datetime()
    aprobacioncontabilidad = fields.Boolean()
    observacioncontabilidad = fields.Text()

    cliente = fields.Char()
    totaldocumento_soles = fields.Float()
    cliente_razonsocial = fields.Char()
    cuenta_contable_descripcion = fields.Char()
    tipodocumento_soles = fields.Integer()

    proveedornoexiste = fields.Boolean()
    proveedornohabido = fields.Boolean()

    state = fields.Selection([
        ('export', 'Exportacion'),
        ('restaurar', 'Restaurar')
    ], string='Tipo',
        help="Tipo de de solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")

    @api.depends("moneda")
    def _compute_currency_id(self):
        for rec in self:
            if rec.moneda == 'USD':
                rec.currency_id = 2

    def action_approve(self):
        pass

    def action_refuse(self):
        pass

class depositos(models.Model):
    _name = 'tqc.depositos'
    _description = 'Depositos'

    name = fields.Char()
    fecha_deposito = fields.Date()
    numero_operacion = fields.Char()
    liquidacion_id = fields.Many2one('tqc.liquidaciones')
    monto = fields.Float('Monto')
    tipo = fields.Char('Tipo')
    subtipo = fields.Integer()
    moneda = fields.Char()

    cuenta_contable = fields.Many2one('cuenta.contable.gastos')
    cuenta_bancaria = fields.Char()
    fecha_contable = fields.Date()

class tipoLiquidaciones(models.Model):
    _name = 'tqc.tipo.liquidaciones'
    _description = 'Tipo de Liquidaciones'

    name = fields.Char()

class cuentaContable(models.Model):
    _name = 'cuenta.contable.gastos'
    _description = 'Tipo de Liquidaciones'

    name = fields.Char()
    description = fields.Char()
    estado = fields.Char()
    centrocosto = fields.Char()
    descripcioncentrocosto = fields.Char()

    # def unlink(self):
    #     for record in self:
    #         if not (self.env.user.has_group('vacation_control.res_groups_administrator')):
    #             if record.state in ['aprobado', 'en_goce', 'gozado', 'suspend']:
    #                 raise UserError(_("No puedes eliminar registro ya calculados"))
    #         #     else:
    #         #         id_trabajador = record.vc_trabajador.id
    #         #         res = super(solicitudVacaciones, record).unlink()
    #         #         self.estado_cuenta(id_trabajador)
    #         # else:
    #         #     id_trabajador = record.vc_trabajador.id
   