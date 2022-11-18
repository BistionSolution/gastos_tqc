# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re, pyodbc

class Liquidaciones(models.Model):
    _name = 'tqc.liquidaciones'
    _description = 'Liquidaciones'

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
        ('draft', 'Borrador'),
        ('jefatura', 'Autorizacion jefatura'),
        ('contable', 'Visto Contable')],
        default='draft', string='Estado Solicitud')

    aprobacioncontabilidad = fields.Boolean()
    ingresocompletado = fields.Boolean()

    muestreocontabilidad = fields.Boolean()
    tipoliquidacion_id = fields.Many2one('tqc.tipo.liquidaciones')
    detalleliquidaciones_id = fields.One2many('tqc.detalle.liquidaciones','liquidacion_id')

    entrega_a_rendir = fields.Char()
    fecha_entrega = fields.Date()
    glosa_entrega = fields.Text()
    monto_entrega = fields.Float()

    aprobacionrecepcioncontabilidad = fields.Boolean()
    observacionrecepcioncontabilidad = fields.Text()
    fecharecepcioncontabilidad = fields.Datetime()
    userrecepcioncontabilidad_id = fields.Many2one('res.user')

    inferfazexactus = fields.Boolean()
    fecha_contable = fields.Date()
    fecha_generacion = fields.Datetime()

    centro_costo_descripcion = fields.Char()
    saldo = fields.Float()
    moneda = fields.Char()

    @api.model
    def get_expense_dashboard(self):
        expense_state = {
            'draft': {
                'description': _('to report'),
                'amount': 0.0,
                'currency': self.env.company.currency_id.id,
            },
            'reported': {
                'description': _('under validation'),
                'amount': 0.0,
                'currency': self.env.company.currency_id.id,
            },
            'approved': {
                'description': _('to be reimbursed'),
                'amount': 0.0,
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

    def _action_import_gastos(self):
        # ip_conexion = ""
        # data_base = ""
        # user_bd = ""
        # pass_bd = ""
        # table_bd = ""
        # table_relations = ""
        # sql = "SELECT "
        # try:
        #     connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
        #                                 data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
        #
        #     if "SELECT" in sql:
        #         campList = self.convert_sql(self, sql)  # lista de campos odoo
        #         company_table = self.capturar_empresa_db(self, sql)  # capture table of company from exactus
        #         # if company_table CONTAIN "EMPLEADO" then logic calculate states of the employees ('CES')
        #         posiUser = []
        #         nom_module = table_bd.replace(".", "_")
        #         if table_relations:
        #             dataExternalSQL = self.get_external_field(self, table_relations)  # Devuelve un arreglo de los nombres de las tablas relacionadas
        #             for data in dataExternalSQL[0]:
        #                 posiUser.append(campList.index(data))  # inicia posicion de elemento
        #
        #         cursor = connection.cursor()
        #         cursor.execute(sql)
        #         idusers = cursor.fetchall()  # GUARDA TODOS LOS REGISTROS DE SQL
        #
        #         for user in idusers:
        #             variJson = {}
        #             work_email = False  # comprueba si tiene Correo, sino no llena
        #             existId = True
        #
        #             sumNom = "{}.{}".format(nom_module, user[0])  # (nombre modulo) + (id del sql)
        #             try:
        #                 register = self.env.ref(sumNom)  # obtiene id de su respectivo modelo
        #                 id_register = self.env.ref(sumNom).id
        #             except ValueError:
        #                 existId = False
        #
        #             if existId:  # SI EXISTE ACTUALIZA
        #                 # ACTUALIZA REGISTRO
        #                 cont = 0
        #                 no_register = False
        #
        #                 for j in range(len(campList)):
        #                     ## SOLO para validar correo repetidos en TQC ##
        #                     #############
        #                     try:
        #                         # if table_bd == 'hr.employee' and (str(user[j]) == '1980-01-01 00:00:00'):
        #                         #     user[j] = False
        #                         if table_bd == 'res.users' and '@' in user[j]:  # COFRREO VALIDADCION TQC
        #                             if ";" in user[j]:
        #                                 user[j] = re.split(r'[;]', user[j])
        #                             else:
        #                                 user[j] = re.split(r'[,]', user[j])
        #                             user[j] = user[j][0]
        #                             exist_mail = self.env["res.users"].search(
        #                                 [('login', '=', user[j]), ('id', '!=', int(id_register))])
        #                             self.env.cr.commit()
        #                             if exist_mail:
        #                                 no_register = True
        #                                 break
        #                             if company_table.lower() == 'tqc.empleado':
        #                                 if 'tqc.com.pe' not in user[j]:
        #                                     no_register = True
        #                                     break
        #                             elif company_table.lower() == 'talex.empleado':
        #                                 if 'talex.com.pe' not in user[j]:
        #                                     if 'tqc.com.pe' not in user[j]:
        #                                         no_register = True
        #                                         break
        #                             elif company_table.lower() == 'semillas.empleado':
        #                                 if 'tqcsemillas.com.pe' not in user[j]:
        #                                     if 'tqc.com.pe' not in user[j]:
        #                                         no_register = True
        #                                         break
        #                             else:  # PARA BIOGEN.EMPLEADO
        #                                 if 'biogenagro.com' not in user[j]:
        #                                     if 'tqc.com.pe' not in user[j]:
        #                                         no_register = True
        #                                         break
        #                         if (table_bd == 'hr.employee') and ('@' in user[j]):
        #                             if ";" in user[j]:
        #                                 user[j] = re.split(r'[;]', user[j])
        #                             else:
        #                                 user[j] = re.split(r'[,]', user[j])
        #                             user[j] = user[j][0]
        #                             work_email = user[j]
        #
        #                     except:
        #                         print("encontro una fecha, no puede comparar")
        #                     ##################
        #                     ## HASTA AQUI ##
        #                     if j == 0:
        #                         continue
        #                     # LLAVE FORANEA ENLACE
        #                     if j in posiUser:  # cambia los nombres por los id correspondientes, # GUARDA CORRESPONDENCIA ONE2MANY
        #                         if not user[j]:
        #                             id_exField = False
        #                         else:
        #                             searchId = "{}.{}".format(dataExternalSQL[1][cont], user[j])
        #                             try:
        #                                 # obtiene id de su respectivo modelo
        #                                 id_exField = self.env.ref(searchId).id
        #                             except ValueError:
        #                                 id_exField = False
        #                             #
        #                         variJson['{}'.format(campList[j])] = id_exField
        #                         cont += 1
        #                         continue
        #
        #                     variJson['{}'.format(campList[j])] = user[j]
        #                     res = {"success"}
        #
        #                 if no_register:
        #                     print("No registro")
        #                 else:
        #                     self.env[table_bd].browse(id_register).write(variJson)
        #                     self.env.cr.commit()
        #
        #                     # ACTUALIZA CONTACTO EL CORREO
        #                     if table_bd == 'res.users':
        #                         # en respartner tr
        #                         print("iddpro     ------ :", id_register)
        #                         print("VARIJSON ES  ------ :", variJson['login'])
        #                         self.env["res.partner"].search([('user_ids', 'in', [id_register])]).write(
        #                             {'email': variJson['login']})
        #                         self.env.cr.commit()
        #
        #                     if table_bd == 'hr.employee' and work_email:
        #                         self.env[table_bd].browse(id_register).write(
        #                             {'work_email': work_email, 'work_phone': '999999999'})
        #                         self.env.cr.commit()
        #
        #             else:  # CREA NUEVO REGISTRO
        #                 cont = 0
        #                 no_register = False  # PARA REGISTRAR
        #                 for i in range(len(campList)):  # recorre y relaciona los campos y datos para trasladar datos
        #                     try:
        #                         ## SOLO para validar correo repetidos en TQC ##
        #                         if (table_bd == 'res.users') and ('@' in user[i]):  # CORREO VALIDACION TQC
        #                             if ";" in user[i]:
        #                                 user[i] = re.split(r'[;]', user[i])
        #                             else:
        #                                 user[i] = re.split(r'[,]', user[i])
        #                             user[i] = user[i][0]
        #                             print("GAAAAAAAAAAAAAAAAAAAAAA : ", id_register)
        #                             exist_mail = self.env["res.users"].search(
        #                                 [('login', '=', user[i]), ('id', '!=', int(id_register))])
        #                             self.env.cr.commit()
        #                             if exist_mail:
        #                                 no_register = True
        #                                 break
        #                             if company_table == 'tqc.EMPLEADO':
        #                                 if 'tqc.com.pe' not in user[i]:
        #                                     no_register = True
        #                                     break
        #                             elif company_table == 'TALEX.EMPLEADO':
        #                                 if 'talex.com.pe' not in user[i]:
        #                                     if 'tqc.com.pe' not in user[i]:
        #                                         no_register = True
        #                                         break
        #                             elif company_table == 'SEMILLAS.EMPLEADO':
        #                                 if 'tqcsemillas.com.pe' not in user[i]:
        #                                     if 'tqc.com.pe' not in user[i]:
        #                                         no_register = True
        #                                         break
        #                             else:  # PARA BIOGEN.EMPLEADO
        #                                 if 'biogenagro.com' not in user[i]:
        #                                     if 'tqc.com.pe' not in user[i]:
        #                                         no_register = True
        #                                         break
        #                         ##################
        #                         ## SOLO PARA CORREO DE TQC EMPLEADOS
        #                         if table_bd == 'hr.employee' and '@' in user[i]:  # CORREO VALIDADCION TQC
        #                             if ";" in user[i]:
        #                                 user[i] = re.split(r'[;]', user[i])
        #                             else:
        #                                 user[i] = re.split(r'[,]', user[i])
        #                             user[i] = user[i][0]
        #                             work_email = user[i]
        #                         ##################
        #                     except:
        #                         print("encontro fecha, no puede comparar")
        #                     if i == 0:
        #                         continue
        #                     if i in posiUser:  # cambia los nombres por los id correspondientes
        #                         if not user[i]:  # SI EL CAMPO NO TIENE RELACION(NULL) GUARDA FALSE
        #                             id_exField = False
        #                         else:
        #
        #                             searchId = "{}.{}".format(dataExternalSQL[1][cont], user[i])
        #                             #
        #                             try:
        #                                 # obtiene id de su respectivo modelo
        #                                 id_exField = self.env.ref(searchId).id
        #                             except ValueError:
        #                                 id_exField = False
        #
        #                         variJson['{}'.format(campList[i])] = id_exField
        #                         cont += 1
        #                         continue
        #                     variJson['{}'.format(campList[i])] = user[i]
        #                 res = variJson
        #                 if no_register:
        #                     print("no registro el registro")
        #                 else:
        #                     original_id = self.env[table_bd].create(variJson).id
        #                     # Si funciona
        #                     self.env["ir.model.data"].create(
        #                         {'name': user[0], 'module': nom_module, 'model': table_bd, 'res_id': original_id})
        #                     self.env.cr.commit()
        #
        #                     if table_bd == 'hr.employee' and work_email:
        #                         self.env[table_bd].browse(original_id).write(
        #                             {'work_email': work_email, 'work_phone': '999999999'})
        #                         self.env.cr.commit()
        #
        #         # update employee cesados ('CES')
        #         if 'empleado' in company_table.lower():
        #             try:
        #                 connection2 = pyodbc.connect(
        #                     'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
        #                     data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
        #                 all_employees = self.env['hr.employee'].search([]).mapped('id_integrador')
        #                 for empl in all_employees:
        #                     if empl:
        #                         cursor2 = connection2.cursor()
        #                         cursor2.execute(
        #                             "SELECT ESTADO_EMPLEADO,FECHA_SALIDA FROM " + company_table + " WHERE EMPLEADO = '" + empl + "'")
        #                         stado = cursor2.fetchall()
        #                         if stado:
        #                             for st in stado:
        #                                 if st[0] == 'CES':
        #                                     self.env['hr.employee'].search(
        #                                         [('id_integrador', '=', empl)]).write({'stado': 'CES', 'finish_job': st[1]})
        #                                     self.env.cr.commit()
        #             except Exception as e:
        #                 raise ValidationError("no guardo correctamente")
        # except Exception as e:
        #     raise ValidationError("no guardo correctamente")

        return {
            "name": "Liquidaciones",
            "type": "ir.actions.act_window",
            "res_model": "tqc.liquidaciones",
            "view_type": "form",
            "view_mode": "tree,form",
            "target": "current",
            "context": {'search_default_draft': True},
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

class detalleLiquidaciones(models.Model):
    _name = 'tqc.detalle.liquidaciones'
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
    base_afecta = fields.Integer()
    montoigv = fields.Integer()
    totaldocumento = fields.Integer()
    cuenta_contable = fields.Char()
    observacionrepresentacion = fields.Text()
    base_inafecta = fields.Integer()
    nocliente = fields.Char()

    useraprobacioncontabilidad = fields.Integer()
    fechaaprobacionjefatura = fields.Datetime()
    aprobacionjefatura = fields.Boolean()
    observacionjefatura = fields.Text()

    cliente = fields.Char()
    totaldocumento_soles = fields.Float()
    cliente_razonsocial = fields.Char()
    cuenta_contable_descripcion = fields.Char()
    tipodocumento_soles = fields.Integer()
    proveedornoexiste = fields.Boolean()
    proveedornohabido = fields.Boolean()

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
    cuenta_contable = fields.Char()
    cuenta_bancaria = fields.Char()
    fecha_contable = fields.Date()

class tipoLiquidaciones(models.Model):
    _name = 'tqc.tipo.liquidaciones'
    _description = 'Tipo de Liquidaciones'

    name = fields.Char()