# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

import re, pyodbc

no_server = True
database = 'TQCBKP2'
userbd = "TQC"
passbd = "extqc"


class detalleLiquidaciones(models.Model):
    _name = 'tqc.detalle.liquidaciones'
    _description = 'Detalle de Liquidaciones'

    liquidacion_id = fields.Many2one('tqc.liquidaciones')
    tipo = fields.Char()
    subtipo = fields.Char()
    serie = fields.Char(required=1, size=4)
    numero = fields.Char(required=1)
    ruc = fields.Char(string='RUC', required=1)
    proveedor_razonsocial = fields.Char(string='Razón social')
    razonsocial_invisible = fields.Selection([
        ('activo', 'acti'),
        ('no_activo', 'No activo'),
        ('no_existe', 'Historial ERC')
    ], default='activo')
    moneda = fields.Char()
    tipocambio = fields.Float(required=1, digits=(12, 3))
    fechaemision = fields.Date(required=1)

    base_afecta = fields.Monetary(currency_field='currency_id', required=1)
    base_inafecta = fields.Monetary(currency_field='currency_id', required=1)
    montoigv = fields.Monetary(currency_field='currency_id', required=1)
    impuesto = fields.Many2one('tqc.impuestos', required=1)
    totaldocumento = fields.Monetary(currency_field='currency_id', required=1)

    cuenta_contable = fields.Many2one('cuenta.gastos.default', required=1)
    tipodocumento = fields.Many2one('tqc.tipo.documentos', required=1)
    codetipo = fields.Char(compute="_depend_tipocode")
    observacionrepresentacion = fields.Text(string='Observacion representacion', required=1)
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

    proveedornoexiste = fields.Boolean()
    proveedornohabido = fields.Boolean()

    # Estado para poder pasar a modo historial o modo edicion 'documento'
    state = fields.Selection([
        ('document', 'Documento'),
        ('historial', 'Historial ERC')
    ], string='Stado', default='document',
        help="Estado solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")

    revisado_state = fields.Selection([
        ('borrador', 'Borrador'),
        ('aprobado_jefatura', 'Aprobado jefatura'),
        ('aprobado_contable', 'Aprobado contabilidad'),
        ('rechazado_jefatura', 'Rechazado jefatura'),
        ('rechazado_contable', 'Rechazado Contabilidad'),
        ('corregido', 'Corregido'),
        ('liquidado', 'Liquidado'),
        ('send_error', 'Error de envio')
    ], string='Estado', default='borrador',
        help="Tipo de de solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")
    attachment = fields.Many2many('ir.attachment', 'attach_rel', 'doc_id', 'attach_id', string="Archivos",
                                  help='You can upload your document', copy=False)
    current_user = fields.Integer(compute='_current_user')
    uid_create = fields.Integer(compute='_get_current_user')
    state_liqui = fields.Char(compute='_get_current_user')
    message_error = fields.Char(String='Mensaje Error respuesta')

    @api.depends("moneda")
    def _compute_currency_id(self):
        for rec in self:
            if rec.moneda == 'USD':
                rec.currency_id = 2

    @api.depends()
    def _current_user(self):
        for record in self:
            print("oje : ", record.state)
            print("UID _: ", record.liquidacion_id.current_user)
            record.current_user = record.liquidacion_id.current_user

    @api.depends()
    def _get_current_user(self):
        for record in self:
            print("oje : ", record.liquidacion_id.uid_create)
            print("UID _: ", record.liquidacion_id.state)
            record.uid_create = record.liquidacion_id.uid_create
            record.state_liqui = record.liquidacion_id.state

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

    @api.onchange('base_afecta', 'base_inafecta', 'impuesto')
    def _onchange_base_afecta(self):
        for rec in self:
            rec.update(rec._get_price_total())

    @api.onchange('tipodocumento')
    def _onchange_tipodocumento(self):
        for rec in self:
            if rec.tipodocumento.tipo == 'B/V':
                înafecto = self.env['tqc.impuestos'].search([('impuesto1', '=', 0)])
                rec.impuesto = înafecto[0].id
                rec.base_afecta = 0

    @api.depends('tipodocumento')
    def _depend_tipocode(self):
        for rec in self:
            if rec.tipodocumento:
                rec.codetipo = rec.tipodocumento.tipo
            else:
                rec.codetipo = False

    def _get_price_total(self, liquidacion_id=None, base_afecta=None, impuesto=None, base_inafecta=None):
        self.ensure_one()
        res = {}
        # Compute 'price_subtotal'.
        # saldo_liqudacion = self.liquidacion_id.saldo
        monto_igv = (self.base_afecta * self.impuesto.impuesto1) / 100
        totaldocumento = monto_igv + self.base_afecta + self.base_inafecta
        res['montoigv'] = monto_igv
        res['totaldocumento'] = totaldocumento
        # In case of multi currency, round before it's use for computing debit credit
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
        for rec in self:
            if rec.fechaemision and no_server:
                cambio = 0
                strfecha = rec.fechaemision
                ip_conexion = "10.10.10.228"
                data_base = database
                user_bd = userbd
                pass_bd = passbd

                sql_prime = """SELECT FECHA, CONVERT(decimal(10,3),MONTO) FROM tqc.TIPO_CAMBIO_HIST WHERE CONVERT(DATE, FECHA) = '""" + strfecha.strftime(
                    '%Y-%m-%d') + """' AND TIPO_CAMBIO = 'TCV'"""
                try:
                    connection = pyodbc.connect(
                        'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                    cursor = connection.cursor()
                    cursor.execute(sql_prime)
                    datos = cursor.fetchall()

                    for dat in datos:
                        print("DATA : ", dat)
                        cambio = dat[1]

                except Exception as e:
                    raise UserError(_("Error al consultar sql exactus"))

                if cambio == 0:
                    raise UserError(_("No existe tipo de cambio para la fecha " + strfecha.strftime('%Y-%m-%d')))
                print("DATA : ", cambio)
                rec.tipocambio = cambio
            # if hi == 1:
            #     raise UserError(_("No existe tipo de cambio para la fecha 2023-01-26"))
            # else:
            #     rec.tipocambio = 3.82

    @api.onchange('ruc')
    def _onchange_ruc(self):
        for rec in self:
            if rec.ruc and no_server:
                result = ""
                ip_conexion = "10.10.10.228"
                data_base = database
                user_bd = userbd
                pass_bd = passbd
                table_bd = "tqc.liquidaciones"
                table_relations = """empleado_name OF hr.employee"""

                sql_habido = """SELECT RUC FROM tqc.PROV_NO_HABIDO WHERE RUC = '""" + rec.ruc + """'"""

                sql_prime = """SELECT TOP 1 PROVEEDOR, NOMBRE, ACTIVO FROM tqc.PROVEEDOR WHERE PROVEEDOR = '""" + rec.ruc + """'"""
                try:
                    connection = pyodbc.connect(
                        'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                    cursor = connection.cursor()
                    cursor.execute(sql_habido)
                    proveedor_habido = cursor.fetchall()
                    print("GAAAAAAAAA", proveedor_habido)
                    if proveedor_habido:
                        raise ValueError(
                            _("RUC " + rec.ruc + " esta no habido, ingresa otro para poder crear documento"))
                    cursor.close()
                    print("GAAAAAAAAA 22 : ", sql_prime)
                    cursor = connection.cursor()
                    cursor.execute(sql_prime)
                    proveedores = cursor.fetchall()
                    print("GAAAAAAAAA 22", proveedores)
                    cursor.close()
                    connection.close()
                except ValueError as err:
                    raise UserError(_(err))
                except Exception as e:
                    raise UserError(_('Error conexion exactus'))

                if not proveedores:
                    rec.razonsocial_invisible = 'no_existe'
                else:
                    for proveedor in proveedores:
                        result = proveedor[1]
                    rec.proveedor_razonsocial = result

                    if proveedor[2] == 'S':
                        rec.razonsocial_invisible = 'activo'
                    else:
                        rec.razonsocial_invisible = 'no_activo'

    @api.onchange('cliente')
    def _onchange_cliente(self):
        for rec in self:
            if rec.cliente and no_server:
                print("que fuentes")
                result = ""

                ip_conexion = "10.10.10.228"
                data_base = database
                user_bd = userbd
                pass_bd = passbd

                sql_prime = """SELECT TOP 1 * FROM tqc.CLIENTE WHERE CLIENTE LIKE '%""" + rec.cliente + """'"""
                try:
                    connection = pyodbc.connect(
                        'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
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
        if no_server:
            info = []

            ip_conexion = "10.10.10.228"
            data_base = database
            user_bd = userbd
            pass_bd = passbd
            table_bd = "tqc.liquidaciones"
            table_relations = """empleado_name OF hr.employee"""

            sql_prime = """SELECT PROVEEDOR, NOMBRE FROM tqc.PROVEEDOR WHERE PROVEEDOR LIKE '%""" + args[
                'ruc'] + """%' OR NOMBRE LIKE '%""" + args['ruc'] + """%'"""

            try:
                connection = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
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
        if no_server:
            info = []
            ip_conexion = "10.10.10.228"
            data_base = database
            user_bd = userbd
            pass_bd = passbd
            sql_prime = """SELECT CLIENTE, NOMBRE FROM tqc.CLIENTE WHERE CLIENTE LIKE '%""" + args[
                'client'] + """%' OR NOMBRE LIKE '%""" + args['client'] + """%'"""
            try:
                connection = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
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

    def search_cod_client(self):
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


class cuentaAttachment(models.Model):
    _inherit = 'ir.attachment'
    attach_rel = fields.Many2many('tqc.detalle.liquidaciones', 'attachment', 'attachment_id', 'document_id',
                                  string="Attachment")


class cuentaGops(models.Model):
    _name = 'tqc.transit.detalle'
    _description = 'Vamos'
