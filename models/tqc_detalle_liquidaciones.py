# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

import re, pyodbc
from odoo.tools import float_compare, float_round

no_server = True


class detalleLiquidaciones(models.Model):
    _name = 'tqc.detalle.liquidaciones'
    _description = 'Detalle de Liquidaciones'

    liquidacion_id = fields.Many2one('tqc.liquidaciones')
    empleado_id = fields.Many2one('hr.employee', related='liquidacion_id.empleado_name')
    tipo = fields.Char()
    subtipo = fields.Char()
    serie = fields.Char()
    numero = fields.Char()
    ruc = fields.Char(string='RUC', required=1)
    proveedor_razonsocial = fields.Char(string='Razón social')
    razonsocial_invisible = fields.Selection([
        ('activo', 'acti'),
        ('no_activo', 'No activo'),
        ('no_existe', 'Historial ERC')
    ], default='activo')

    tipocambio = fields.Float(required=1, digits=(12, 3))
    fechaemision = fields.Date(required=1)

    base_afecta = fields.Monetary(currency_field='currency_id', digits=(12, 2), required=1)
    base_inafecta = fields.Monetary(currency_field='currency_id', digits=(12, 2), required=1)
    montoigv = fields.Monetary(currency_field='currency_id', required=1)
    impuesto = fields.Many2one('tqc.impuestos', required=1)
    # Totales
    totaldocumento = fields.Monetary(currency_field='currency_id', required=1)
    total_neto = fields.Monetary(currency_field='currency_id', required=1)

    cuenta_contable = fields.Many2one('cuenta.gastos.default', required=1)
    department_id = fields.Many2one('hr.department', related='empleado_id.department_id')
    tipodocumento = fields.Many2one('tqc.tipo.documentos', required=1)
    codetipo = fields.Char(compute="_depend_tipocode")
    code_cuenta_contable = fields.Char(compute="_depend_cuentacontable")
    observacionrepresentacion = fields.Text(string='Observacion representacion')
    nocliente = fields.Char()
    moneda = fields.Selection([
        ('SOL', 'SOL'),
        ('USD', 'DOLAR')
    ], string='Moneda', default="SOL", required=True)
    currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
                                  states={'reported': [('readonly', True)], 'approved': [('readonly', True)],
                                          'done': [('readonly', True)]}, compute='_compute_currency_id',
                                  default=lambda self: self.env.company.currency_id)
    currency_liquidacion_id = fields.Many2one('res.currency', string='Currency', related='liquidacion_id.currency_id')

    useraprobacionjefatura = fields.Monetary(currency_field='currency_id', string="Monto aprobado jefatura")
    fechaaprobacionjefatura = fields.Datetime()
    aprobacionjefatura = fields.Boolean()
    observacionjefatura = fields.Text()

    useraprobacioncontabilidad = fields.Monetary(currency_field='currency_id', string="Monto aprobado contabilidad")
    fechaaprobacioncontabilidad = fields.Datetime()
    aprobacioncontabilidad = fields.Boolean()
    observacioncontabilidad = fields.Text()

    cliente = fields.Char()
    totaldocumento_soles = fields.Float()

    cliente_razonsocial = fields.Char()
    cuenta_contable_descripcion = fields.Char()
    icbper = fields.Monetary(currency_field='currency_id', string="ICBPER")
    otros_tributos = fields.Monetary(currency_field='currency_id', string="Otros tributos")
    proveedornoexiste = fields.Boolean()
    proveedornohabido = fields.Boolean()

    # Estado para poder pasar a modo historial o modo edicion 'documento'
    state = fields.Selection([
        ('document', 'Documento'),
        ('historial', 'Historial ERC')
    ], string='Estado', default='document',
        help="Estado solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")

    revisado_state = fields.Selection([
        ('borrador', 'Por enviar'),
        ('aprobado_jefatura', 'Aprobado jefatura'),
        ('aprobado_contable', 'Aprobado contabilidad'),
        ('observado_contable', 'Observado contabilidad'),
        ('rechazado_jefatura', 'Rechazado jefatura'),
        ('rechazado_contable', 'Rechazado contabilidad'),
        ('observado_jefatura', 'Rechazado contabilidad'),
        ('corregido', 'Corregido'),
        ('liquidado', 'Liquidado'),
        ('send_error', 'Error de envio')
    ], string='Estado', default='borrador',
        help="Tipo de de solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")
    attachment = fields.Many2many('ir.attachment', 'attach_rel', 'doc_id', 'attach_id', string="Archivos",
                                  help='You can upload your document')
    # attachment_ids = fields.Many2many('ir.attachment', string="Archivos",
    #                                     help='You can upload your document',  attachment=True)
    current_user = fields.Integer(compute='_current_user')
    uid_create = fields.Integer(compute='_get_current_user')
    state_liqui = fields.Char(compute='_get_current_user')
    message_error = fields.Char(String='Mensaje Error respuesta')

    sequence = fields.Integer('Secuencia', default=0)

    # @api.model
    # def create(self, vals):
    #     last_record = self.search([], order='sequence desc', limit=1)
    #     vals['sequence'] = last_record.sequence + 1 if last_record else 0
    #     return super(detalleLiquidaciones, self).create(vals)

    @api.model
    def create(self, vals):
        templates = super(detalleLiquidaciones, self).create(vals)

        # fix attachment ownership
        for template in templates:
            if template.attachment:
                template.attachment.write({'res_model': self._name, 'res_id': template.id})
        return templates

    def fix_existing_attachments(self):
        # Obtener todos los registros relevantes
        all_records = self.sudo().search([])
        for record in all_records:
            record.attachment.write({'res_model': self._name, 'res_id': record.id})

    # @api.depends()
    # def compute_departments_id(self):
    #     for rec in self:
    #         print("empleado_id ", rec.empleado_id.department_id)
    #         rec.department_id = rec.empleado_id.department_id

    # @api.model
    # def create(self, vals):
    #     templates = super(detalleLiquidaciones, self).create(vals)
    #     # fix attachment ownership
    #     for template in templates:
    #         if template.attachment:
    #             template.attachment.write({'res_model': self._name, 'res_id': template.id})
    #     return templates

    # Comprueba si ya existe documentos con el mismo numero y serie
    @api.onchange('serie', 'numero', 'ruc')
    def _onchange_serie_number(self):
        # Verificar que el numero y serie y proveedor no se repita en registros anteriores
        # if record.serie and record.numero and record.ruc:
        #     count = self.search_count([('serie', '=', record.serie), ('numero', '=', record.numero),
        #                                ('ruc', '=', record.ruc)])
        #     if count >= 2:
        #         raise ValidationError(
        #             f'El número de serie y proveedor ya existe en un registro anterior, verifique por favor. {count}')
        if self.serie and self.numero and self.ruc:
            # Obtener todos los registros del modelo 'modelo.detalles' en la vista actual
            all_details = self.env['tqc.detalle.liquidaciones'].search_read([
                ('serie', '=', self.serie),
                ('numero', '=', self.numero),
                ('ruc', '=', self.ruc)
            ], ['id', 'serie', 'numero', 'ruc', 'liquidacion_id'])
            print("ALL self.id: ", self.id)
            print("ALL DETAILS: ", all_details)
            print("ALL DETALLES: ", self.liquidacion_id.detalleliquidaciones_id)
            for detalle in self.liquidacion_id.detalleliquidaciones_id:
                # Verificar que no se compare el registro consigo mismo
                if detalle != self and detalle.serie == self.serie and detalle.numero == self.numero and detalle.ruc == self.ruc:
                    raise ValidationError(
                        f'El número de serie {self.serie}, número {self.numero} y RUC {self.ruc} ya existen en un registro anterior. Por favor, verifique.'
                    )

            # Filtrar y revisar cada registro individualmente
            for rec in all_details:
                print("ID del registro:", rec['id'])  # Imprime el ID de cada registro encontrado
                if 'NewId' in str(self.id):
                    print("NEW RECORD: ", rec)
                    id_string = str(self.id)
                    parts = id_string.split("_")
                    print("PARTS: ", parts[1])
                    if len(parts) > 1 and parts[1].isdigit():
                        temp_id = int(parts[1])  # Asegurarse de que es un número y convertirlo
                        print("Temp ID:", temp_id)

                        if rec['id'] == temp_id:
                            continue
                        # Mostrar una advertencia si se encuentran duplicados
                raise ValidationError(
                    f'El número de serie {self.serie}, número {self.numero} y RUC {self.ruc} ya existen en un registro anterior con ID: {rec["id"]} en la liquidacion: {rec["liquidacion_id"][1]}. Por favor, verifique.'
                )

    @api.depends("moneda")
    def _compute_currency_id(self):
        for rec in self:
            if rec.moneda == 'USD':
                # Buscar moneda USD
                rec.currency_id = self.env['res.currency'].search([('name', '=', 'USD')]).id
            else:
                rec.currency_id = self.env['res.currency'].search([('name', '=', 'PEN')]).id

    @api.depends()
    def _current_user(self):
        for record in self:
            print("current user : ", record.liquidacion_id.current_user)
            record.current_user = record.liquidacion_id.current_user

    @api.depends()
    def _get_current_user(self):
        for record in self:
            record.uid_create = record.liquidacion_id.uid_create
            record.state_liqui = record.liquidacion_id.state

    def _get_cuenta_domain(self):
        context = self._context.copy() or {}
        # obtener valor de state en la siguiente vista
        # dame solo las cuentas que esten activas
        domain = []
        domain.append(('department_id', '=', self.empleado_id.department_id.id))
        return domain

    # @api.onchange('empleado_id')
    # def _onchange_empleado_id(self):
    #     print("DOMAIN ----------> HERE")
    #     if self.empleado_id:
    #         # Define aquí la lógica para el dominio basado en el empleado_id
    #         domain = [('department_id', '=', self.empleado_id.department_id.id)]
    #     else:
    #         domain = []
    #
    #     print("DOMAIN ----------> ", domain)
    #     return {'domain': {'cuenta_contable': domain}}

    # totaldocumento no debe ser meno a 0
    # @api.constrains('totaldocumento')
    # def check_saldo(self):
    #     for rec in self:
    #         if rec.totaldocumento <= 0:
    #             raise UserError(_('El monto total del documento no debe ser menor o igual a 0'))

    # @api.constrains('tipocambio')
    # def check_saldo(self):
    #     for rec in self:
    #         if rec.tipocambio == 0:
    #             raise UserError(_('se debe seleccionar fecha de emision correcta para tipo de cambio'))

    # @api.onchange('totaldocumento')
    # def _onchange_totaldocumento(self):
    #     for rec in self:
    #         if rec.totaldocumento:
    #             saldo_liqudacion = rec.liquidacion_id.saldo
    #             sum_total = sum(rec.liquidacion_id.detalleliquidaciones_id.mapped('totaldocumento'))
    #             if sum_total > saldo_liqudacion:
    #                 raise UserError(_('Se paso del saldo'))

    @api.onchange('base_afecta', 'base_inafecta', 'impuesto', 'icbper', 'otros_tributos', 'moneda')
    def _onchange_base_afecta(self):
        for rec in self:
            rec.update(rec._get_price_total())

    @api.onchange('tipodocumento')
    def _onchange_tipodocumento(self):
        for rec in self:
            if rec.tipodocumento.descripcion in ['03 - Boleta de Venta', '01 - Factura No Gravada',
                                                 '53 - Planilla Movilidad', 'Vale Otros Gastos']:
                if rec.tipodocumento.descripcion == '03 - Boleta de Venta':
                    rec.icbper = 0
                    rec.otros_tributos = 0
                if rec.tipodocumento.descripcion == 'Vale Otros Gastos':
                    rec.serie = False
                    rec.numero = False
                înafecto = self.env['tqc.impuestos'].search([('impuesto1', '=', 0)])
                rec.impuesto = înafecto[0].id
                rec.base_afecta = 0
            else:
                if rec.impuesto.impuesto1 == 0:
                    rec.impuesto = False

    @api.depends('tipodocumento')
    def _depend_tipocode(self):
        for rec in self:
            if rec.tipodocumento:
                rec.codetipo = rec.tipodocumento.descripcion
            else:
                rec.codetipo = False

    @api.depends('cuenta_contable')
    def _depend_cuentacontable(self):
        for rec in self:
            rec.code_cuenta_contable = rec.cuenta_contable.codigo if rec.cuenta_contable else False

    @api.onchange('cuenta_contable')
    def _onchange_cuentacontable(self):
        for rec in self:
            if rec.cuenta_contable:
                if rec.cuenta_contable.codigo == '63.4.3.3.0.00.00':
                    print("Mostrar campo de observacion de representacion")
                    warning = {
                        'title': "Mensaje de advertencia",
                        'message': "Llenar campo de (Obs. de presentación) donde se consigna el numero de placa.",
                    }
                    return {'warning': warning}

    @api.onchange('totaldocumento')
    def _check_detraction(self):
        for rec in self:
            print("total neto ", rec.totaldocumento, rec.codetipo)
            if rec.totaldocumento > 700 and rec.codetipo in ['01 - Factura']:
                print("RARO ", rec.totaldocumento, rec.codetipo)
                warning = {
                    'title': "Mensaje de advertencia",
                    'message': "Factura mas de 700 se encuentra afecta a detracción (por adquisición de servicios) o retención (por adquisición de bienes)",
                }
                return {'warning': warning}
                # raise UserError(_('Se paso del saldo'))
                # title = _("Connection Test Succeeded!")
                # message = _("Everything seems properly set up!")
                # return {
                #     'type': 'ir.actions.client',
                #     'tag': 'display_notification',
                #     'params': {
                #         'title': title,
                #         'message': message,
                #         'sticky': False,
                #     }
                # }

    # @api.constrains('total_neto')
    # def _check_monto(self):
    #     for record in self:
    #         print("Contrain ----------- monto ", record.total_neto)
    #         if record.total_neto <= 0:
    #             raise ValidationError("El monto debe ser mayor que cero.")

    # def _get_price_total(self):
    #     self.ensure_one()
    #     res = {}
    #
    #     # Redondear los valores de base_afecta, impuesto1, etc.
    #     base_afecta_rounded = round(self.base_afecta, 2)
    #     impuesto1_rounded = round(self.impuesto.impuesto1, 2)
    #     base_inafecta_rounded = round(self.base_inafecta, 2)
    #     icbper_rounded = round(self.icbper, 2)
    #     otros_tributos_rounded = round(self.otros_tributos, 2)
    #
    #     # Calcular el monto IGV redondeando el resultado
    #     monto_igv = round((base_afecta_rounded * impuesto1_rounded) / 100, 2)
    #
    #     # Calcular el total del documento redondeando el resultado
    #     totaldocumento = round(
    #         monto_igv + base_afecta_rounded + base_inafecta_rounded + icbper_rounded + otros_tributos_rounded, 2)
    #
    #     res['montoigv'] = monto_igv
    #     res['totaldocumento'] = totaldocumento
    #
    #     if self.tipocambio != 0:
    #         if self.currency_liquidacion_id.name == 'USD' and self.currency_id.name == 'PEN':
    #             res['total_neto'] = round(totaldocumento / self.tipocambio, 2)
    #         elif self.currency_liquidacion_id.name == 'PEN' and self.currency_id.name == 'USD':
    #             res['total_neto'] = round(totaldocumento * self.tipocambio, 2)
    #         else:
    #             res['total_neto'] = totaldocumento
    #     else:
    #         res['total_neto'] = totaldocumento
    #
    #     # En caso de multi-moneda, redondear antes de usar para el cálculo de débito y crédito
    #     return res

    def _get_price_total(self):
        self.ensure_one()
        res = {}

        # Redondear los valores de base_afecta, impuesto1, etc.
        base_afecta_rounded = self.base_afecta
        impuesto1_rounded = self.impuesto.impuesto1
        base_inafecta_rounded = self.base_inafecta
        icbper_rounded = self.icbper
        otros_tributos_rounded = self.otros_tributos

        # Calcular el monto IGV redondeando el resultado
        monto_igv = (base_afecta_rounded * impuesto1_rounded) / 100

        # Calcular el total del documento redondeando el resultado
        totaldocumento = monto_igv + base_afecta_rounded + base_inafecta_rounded + icbper_rounded + otros_tributos_rounded

        # Aplicar redondeo usando la precisión definida en Odoo para la moneda
        monto_igv_rounded = float_round(monto_igv, precision_digits=self.currency_id.decimal_places)
        totaldocumento_rounded = float_round(totaldocumento, precision_digits=self.currency_id.decimal_places)

        res['montoigv'] = monto_igv_rounded
        res['totaldocumento'] = totaldocumento_rounded

        if self.tipocambio != 0:
            if self.currency_liquidacion_id.name == 'USD' and self.currency_id.name == 'PEN':
                res['total_neto'] = float_round(totaldocumento_rounded / self.tipocambio, precision_digits=2)
            elif self.currency_liquidacion_id.name == 'PEN' and self.currency_id.name == 'USD':
                res['total_neto'] = float_round(totaldocumento_rounded * self.tipocambio, precision_digits=2)
            else:
                res['total_neto'] = totaldocumento_rounded
        else:
            res['total_neto'] = totaldocumento_rounded

        # En caso de multi-moneda, redondear antes de usar para el cálculo de débito y crédito
        return res

    # @api.onchange('base_inafecta')
    # def _onchange_base_inafecta(self):
    #     for rec in self:
    #         rec.update(rec._get_price_total())
    #
    #
    # @api.onchange('impuesto')
    # def _onchange_impuesto(self):
    #     for rec in self:
    #         rec.update(rec._get_price_total())

    @api.onchange('fechaemision')
    def _onchange_fecha(self):
        prefix_table = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.prefix_table')
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        for rec in self:
            if rec.fechaemision and no_server:
                cambio = 0
                strfecha = rec.fechaemision
                print("fecha ", strfecha)
                # restar 3 dias a la fecha y guardarla en una variable
                strfecha2 = strfecha - datetime.timedelta(days=3)
                ip_conexion = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.ip_conexion')
                data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
                user_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.username_exactus')
                pass_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.password_exactus')

                sql_prime = """SELECT FECHA, CONVERT(decimal(10,3),MONTO) FROM """ + prefix_table + """.TIPO_CAMBIO_HIST WHERE 
                     CONVERT(DATE, FECHA) > '""" + strfecha2.strftime(
                    '%Y-%m-%d') + """' AND CONVERT(DATE, FECHA) <= '""" + strfecha.strftime(
                    '%Y-%m-%d') + """'  AND TIPO_CAMBIO = 'TCV'"""
                try:
                    connection = pyodbc.connect(
                        'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                    cursor = connection.cursor()
                    cursor.execute(sql_prime)
                    datos = cursor.fetchall()

                    for dat in datos:
                        cambio = dat[1]


                except Exception as e:
                    raise UserError(_("Error al consultar sql exactus"))

                if cambio == 0:
                    raise UserError(_("No existe tipo de cambio para la fecha " + strfecha2.strftime(
                        '%Y-%m-%d') + " hasta la fecha ingresada " + strfecha.strftime('%Y-%m-%d')))
                rec.tipocambio = cambio

                if rec.fechaemision.weekday() == 6:
                    warning = {
                        'title': "Mensaje de advertencia",
                        'message': "Fecha domingo debe contar aprobación de su jefatura, enviar mensaje a reembolsos.go@tqc.com.pe",
                    }
                    return {'warning': warning}

    @api.onchange('serie')
    def _onchange_serie(self):
        for rec in self:
            min_serie = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.min_serie')
            max_serie = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.max_serie')

            if rec.serie:
                if not int(min_serie) <= len(rec.serie) <= int(max_serie):
                    # raise UserError('error')
                    raise UserError('La serie debe ser menor igual a %s y mayor igual a %s' % (min_serie, max_serie))
                rec.serie = rec.serie.upper()
            else:
                rec.serie = False

    # @api.onchange('numero')
    # def _onchange_numero(self):
    #     for rec in self:
    #         print("fa ",rec.liquidacion_id.detalleliquidaciones_id)
    # print("liquidacion ",rec.liquidacion_id.id)
    # print("rec did ",rec.id)
    # print("fa ",self.env['tqc.detalle.liquidaciones'].search([('liquidacion_id','=', rec.liquidacion_id.id)]))

    @api.onchange('ruc')
    def _onchange_ruc(self):
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        prefix_table = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.prefix_table')
        for rec in self:
            if rec.ruc and no_server:
                if rec.tipodocumento.descripcion == '53 - Planilla Movilidad' and len(rec.ruc) != 8:
                    raise UserError('El campo RUC debe contener numero DNI (8 dígitos)')
                result = ""
                ip_conexion = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.ip_conexion')
                data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
                user_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.username_exactus')
                pass_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.password_exactus')

                sql_habido = """SELECT RUC FROM """ + prefix_table + """.PROV_NO_HABIDO WHERE RUC = '""" + rec.ruc + """'"""
                sql_prime = """SELECT TOP 1 PROVEEDOR, NOMBRE, ACTIVO FROM """ + prefix_table + """.PROVEEDOR WHERE PROVEEDOR = '""" + rec.ruc + """'"""

                try:
                    connection = pyodbc.connect(
                        'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                    cursor = connection.cursor()
                    cursor.execute(sql_habido)
                    proveedor_habido = cursor.fetchall()

                    cursor.close()
                    # print("GAAAAAAAAA 22 : ", sql_prime)
                    cursor = connection.cursor()
                    cursor.execute(sql_prime)
                    proveedores = cursor.fetchall()
                    # print("GAAAAAAAAA 22", proveedores)
                    cursor.close()
                    connection.close()
                except ValueError as err:
                    raise UserError(_(err))
                except Exception as e:
                    raise UserError(_('Error conexion exactus'))

                if proveedor_habido:
                    raise UserError(
                        _("RUC " + rec.ruc + " esta no habido, ingresa otro para poder crear documento"))

                if not proveedores:
                    rec.razonsocial_invisible = 'no_existe'
                    # warning = {
                    #     'title': "Mensaje de advertencia",
                    #     'message': "Proveedor no existente en Exactus, puede ingresar el RUC pero se le marcara en rojo",
                    # }
                    # return {'warning': warning}
                    self.env.user.notify_warning(
                        message='Proveedor no existente en Exactus, puede ingresar el RUC pero se le marcara en rojo')
                else:
                    for proveedor in proveedores:
                        result = proveedor[1]
                        if proveedor[2] != 'S':
                            print(proveedor.errpo)
                            raise UserError(_('Proveedor no activo, no puede crear documento'))
                    rec.razonsocial_invisible = 'activo'
                    rec.proveedor_razonsocial = result

    @api.onchange('cliente')
    def _onchange_cliente(self):
        prefix_table = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.prefix_table')
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        for rec in self:
            if rec.cliente and no_server:
                result = ""
                ip_conexion = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.ip_conexion')
                data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
                user_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.username_exactus')
                pass_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.password_exactus')

                sql_prime = """SELECT TOP 1 * FROM """ + prefix_table + """.CLIENTE WHERE CLIENTE LIKE '%""" + rec.cliente + """'"""
                try:
                    connection = pyodbc.connect(
                        'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                    cursor = connection.cursor()
                    cursor.execute(sql_prime)
                    proveedores = cursor.fetchall()

                    for proveedor in proveedores:
                        rucclient = proveedor[0]
                        result = proveedor[1]

                except Exception as e:
                    result = ""

                rec.cliente_razonsocial = result

    # def unlink(self):
    #     # liquidaciones = self.sudo().env['tqc.liquidaciones'].search([('liquidacion_id', '=', self.id), ('habilitado_state', 'in', ['proceso', 'corregir'])])
    #     if self.env.user.has_group('gastos_tqc.res_groups_aprobador_gastos'):
    #         raise UserError(_("No puedes eliminar registro si eres rol jefatura"))
    #
    #     if self.liquidacion_id.habilitado_state in ['proceso', 'corregir']:
    #         raise UserError(_("No puedes eliminar registro en estado 'corregir' y 'proceso'"))
    #     return super(detalleLiquidaciones, self).unlink()

    def action_approve(self):
        pass

    def action_refuse(self):
        pass

    @api.model
    def search_ruc(self, args):
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        if no_server:
            info = []
            ip_conexion = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.ip_conexion')
            data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
            user_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.username_exactus')
            pass_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.password_exactus')
            prefix_table = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.prefix_table')

            sql_prime = """SELECT PROVEEDOR, NOMBRE FROM """ + prefix_table + """.PROVEEDOR WHERE PROVEEDOR LIKE '%""" + \
                        args[
                            'ruc'] + """%' OR NOMBRE LIKE '%""" + args['ruc'] + """%'"""

            try:
                connection = pyodbc.connect(
                    'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                    data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                cursor = connection.cursor()
                cursor.execute(sql_prime)
                proveedores = cursor.fetchall()

                for key in proveedores:
                    info.append({
                        "ruc": key[0],
                        "razon": key[1]
                    })
            except Exception as e:
                raise UserError(e)

            return info

    @api.model
    def search_client(self, args):
        driver_version = self.env['ir.config_parameter'].sudo().get_param('total_integrator.version_drive')
        if no_server:
            info = []
            ip_conexion = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.ip_conexion')
            data_base = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.data_base_gastos')
            user_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.username_exactus')
            pass_bd = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.password_exactus')
            prefix_table = self.env['ir.config_parameter'].sudo().get_param('gastos_tqc.prefix_table')

            sql_prime = """SELECT CLIENTE, NOMBRE FROM """ + prefix_table + """..CLIENTE WHERE CLIENTE LIKE '%""" + \
                        args[
                            'client'] + """%' OR NOMBRE LIKE '%""" + args['client'] + """%'"""
            try:
                connection = pyodbc.connect(
                    'DRIVER={ODBC Driver ' + driver_version + ' for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                    data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                cursor = connection.cursor()
                cursor.execute(sql_prime)
                clientes = cursor.fetchall()

                for key in clientes:
                    info.append({
                        "ruc": key[0],
                        "razon": key[1]
                    })

            except Exception as e:
                raise UserError(e)

            return info

    def get_razon_social_cortada(self):
        if len(self.proveedor_razonsocial) > 30:
            # Corta la cadena para que no exceda de 30 caracteres
            # y evita cortar palabras a mitad.
            return ' '.join(self.proveedor_razonsocial[:30].split(' ')[:-1]) + '...'
        else:
            return self.proveedor_razonsocial

    def search_cod_client(self):
        pass

    def open_edit_form(self):

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'tqc.detalle.liquidaciones',
            'view_mode': 'form',
            'res_id': self.id,
            'view_id': self.env.ref('gastos_tqc.view_form_detalles_liquidaciones').id,
            'target': 'new',
        }


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


class cuentaAttachment(models.Model):
    _inherit = 'ir.attachment'
    attach_rel = fields.Many2many('tqc.detalle.liquidaciones', 'tqc_detalle_liquidaciones_ir_attachment_rel',
                                  'attachment_id', 'document_id',
                                  string="Attachment")


class cuentaGops(models.Model):
    _name = 'tqc.transit.detalle'
    _description = 'Vamos'
