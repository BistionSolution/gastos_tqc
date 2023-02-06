# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime

import re, pyodbc


class detalleLiquidaciones(models.Model):
    _name = 'tqc.detalle.liquidaciones'
    _description = 'Detalle de Liquidaciones'

    liquidacion_id = fields.Many2one('tqc.liquidaciones')
    tipo = fields.Char()
    subtipo = fields.Char()
    serie = fields.Char(required=1)
    numero = fields.Char(required=1)
    ruc = fields.Char(string='RUC', required=1)
    proveedor_razonsocial = fields.Char(string='Razón social')
    moneda = fields.Char()
    tipocambio = fields.Float(required=1, digits=(12, 3))
    fechaemision = fields.Date(required=1)

    base_afecta = fields.Monetary(currency_field='currency_id', required=1)
    base_inafecta = fields.Monetary(currency_field='currency_id', required=1)
    montoigv = fields.Monetary(currency_field='currency_id', required=1)
    impuesto = fields.Many2one('tqc.impuestos', required=1)
    totaldocumento = fields.Monetary(currency_field='currency_id', required=1)

    cuenta_contable = fields.Many2one('cuenta.contable.gastos', required=1)
    tipodocumento = fields.Many2one('tqc.tipo.documentos', required=1)
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

    cliente = fields.Char(required=1)
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
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('corregido', 'Corregido'),
    ], string='Estado', default='borrador',
        help="Tipo de de solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")

    @api.depends("moneda")
    def _compute_currency_id(self):
        for rec in self:
            if rec.moneda == 'USD':
                rec.currency_id = 2

    @api.onchange('totaldocumento')
    def _onchange_totaldocumento(self):
        for rec in self:
            if rec.totaldocumento:
                saldo_liqudacion = rec.liquidacion_id.saldo
                sum_total = sum(rec.liquidacion_id.detalleliquidaciones_id.mapped('totaldocumento'))
                if sum_total > saldo_liqudacion:
                    raise UserError(_('Se paso del saldo'))

    # @api.constrains('tipocambio')
    # def check_saldo(self):
    #     for rec in self:
    #         if rec.tipocambio == 0:
    #             raise UserError(_('se debe seleccionar fecha de emision correcta para tipo de cambio'))

    @api.onchange('base_afecta', 'base_inafecta', 'impuesto')
    def _compute_igv_total(self):
        for rec in self:
            monto_igv = (rec.base_afecta * rec.impuesto.impuesto) / 100
            rec.montoigv = monto_igv
            rec.totaldocumento = monto_igv + rec.base_afecta + rec.base_inafecta

    @api.onchange('fechaemision')
    def _onchange_fecha(self):
        for rec in self:
            if rec.fechaemision:
                cambio = 0
                strfecha = rec.fechaemision
                print("fecgha es s, ", strfecha)
                print("string fecha es ", strfecha.strftime('%Y-%m-%d'))
                ip_conexion = "10.10.10.228"
                data_base = "TQC"
                user_bd = "vacaciones"
                pass_bd = "exvacaciones"

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
                        cambio = dat[1] / 1000

                except Exception as e:
                    raise UserError(_("Error al consultar sql exactus"))

                if cambio == 0:
                    raise UserError(_("No existe tipo de cambio para la fecha " + strfecha.strftime('%Y-%m-%d')))

                rec.tipocambio = cambio
            # if hi == 1:
            #     raise UserError(_("No existe tipo de cambio para la fecha 2023-01-26"))
            # else:
            #     rec.tipocambio = 3.82

    @api.onchange('ruc')
    def _onchange_ruc(self):
        for rec in self:
            if rec.ruc:
                result = ""
                ip_conexion = "10.10.10.228"
                data_base = "TQC"
                user_bd = "vacaciones"
                pass_bd = "exvacaciones"
                table_bd = "tqc.liquidaciones"
                table_relations = """empleado_name OF hr.employee"""

                sql_prime = """SELECT TOP 1 * FROM tqc.PROVEEDOR WHERE PROVEEDOR LIKE '%""" + rec.ruc + """'"""
                try:
                    connection = pyodbc.connect(
                        'DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
                    cursor = connection.cursor()
                    cursor.execute(sql_prime)
                    proveedores = cursor.fetchall()

                    for proveedor in proveedores:
                        result = proveedor[2]

                except Exception as e:
                    result = ""
                print("razon soc ",result)
                rec.proveedor_razonsocial = result

    @api.onchange('cliente')
    def _onchange_cliente(self):
        for rec in self:
            if rec.cliente:
                print("que fuentes")
                result = ""

                ip_conexion = "10.10.10.228"
                data_base = "TQC"
                user_bd = "vacaciones"
                pass_bd = "exvacaciones"

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

    def unlink(self):
        # liquidaciones = self.sudo().env['tqc.liquidaciones'].search([('liquidacion_id', '=', self.id), ('habilitado_state', 'in', ['proceso', 'corregir'])])
        if self.liquidacion_id.habilitado_state in ['proceso', 'corregir']:
            raise UserError(_("No puedes eliminar registro en estado 'corregir' y 'proceso'"))
        return super(detalleLiquidaciones, self).unlink()

    def action_approve(self):
        pass

    def action_refuse(self):
        pass

    @api.model
    def search_ruc(self, args):
        result = ""
        rucproveedor = ""

        ip_conexion = "10.10.10.228"
        data_base = "TQC"
        user_bd = "vacaciones"
        pass_bd = "exvacaciones"
        table_bd = "tqc.liquidaciones"
        table_relations = """empleado_name OF hr.employee"""

        sql_prime = """SELECT TOP 1 * FROM tqc.PROVEEDOR WHERE PROVEEDOR LIKE '%""" + args['ruc'] + """'"""
        try:
            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
            cursor = connection.cursor()
            cursor.execute(sql_prime)
            proveedores = cursor.fetchall()

            for proveedor in proveedores:
                rucproveedor = proveedor[0]
                result = proveedor[2]

        except Exception as e:
            result = "Fallo la conexxion"

        if result:
            rucproveedor = rucproveedor.strip()
            return [rucproveedor, result]
        else:
            return 'esta vacio'

    @api.model
    def search_client(self, args):
        result = ""
        rucclient = ""

        ip_conexion = "10.10.10.228"
        data_base = "TQC"
        user_bd = "vacaciones"
        pass_bd = "exvacaciones"

        sql_prime = """SELECT TOP 1 * FROM tqc.CLIENTE WHERE CLIENTE LIKE '%""" + args['client'] + """'"""
        try:
            connection = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server}; SERVER=' + ip_conexion + ';DATABASE=' +
                                        data_base + ';UID=' + user_bd + ';PWD=' + pass_bd)
            cursor = connection.cursor()
            cursor.execute(sql_prime)
            proveedores = cursor.fetchall()

            for proveedor in proveedores:
                rucclient = proveedor[0]
                result = proveedor[1]

        except Exception as e:
            result = "Fallo la conexion"

        if result:
            print(rucclient)
            rucclient = rucclient.strip()
            return [rucclient, result]
        else:
            return 'esta vacio cliente'

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


class tipoLiquidaciones(models.Model):
    _name = 'tqc.tipo.liquidaciones'
    _description = 'Tipo de Liquidaciones'

    name = fields.Char()


class tipoDocumento(models.Model):
    _name = 'tqc.tipo.documentos'
    _description = 'Tipo de Documentos'

    name = fields.Char(required=1)
    code = fields.Char(required=1)

    def name_get(self):  # agrega nombre al many2one relacionado
        result = []
        for rec in self:
            if rec.code:
                name = str(rec.code + ' - ' + rec.name)
            else:
                name = rec.name
            result.append((rec.id, name))
        return result


class cuentaContable(models.Model):
    _name = 'cuenta.contable.gastos'
    _description = 'Tipo de Liquidaciones'

    name = fields.Char()
    description = fields.Char()
    estado = fields.Char()
    centrocosto = fields.Many2one('hr.department')
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


class cuentaGops(models.Model):
    _name = 'tqc.transit.detalle'
    _description = 'Vamos'
