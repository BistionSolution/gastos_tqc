# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import re, pyodbc

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
    tipodocumento = fields.Many2one('tqc.tipo.documentos')
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

    proveedornoexiste = fields.Boolean()
    proveedornohabido = fields.Boolean()

    state = fields.Selection([
        ('document', 'Documento'),
        ('historial', 'Historial ERC')
    ], string='Tipo', default='document',
        help="Tipo de de solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")

    @api.depends("moneda")
    def _compute_currency_id(self):
        for rec in self:
            if rec.moneda == 'USD':
                rec.currency_id = 2

    @api.constrains('base_afecta')
    def check_saldo(self):
        for rec in self:
            saldo_liqudacion = rec.liquidacion_id.saldo
            sum_total = sum(rec.liquidacion_id.detalleliquidaciones_id.mapped('totaldocumento'))
            # print("Saldo : ",saldo_liqudacion)
            # print("Saldo 2 : ",sum_total)
            if sum_total > saldo_liqudacion:
                raise UserError(_('Se paso del saldo'))

    @api.onchange('base_afecta', 'base_inafecta')
    def _compute_igv_total(self):
        for rec in self:
            monto_igv = (rec.base_afecta * 18) / 100
            rec.montoigv = monto_igv
            rec.totaldocumento = monto_igv + rec.base_afecta + rec.base_inafecta

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

class tipoDocumento(models.Model):
    _name = 'tqc.tipo.documentos'
    _description = 'Tipo de Documentos'

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

class transitdetalle(models.AbstractModel):
    _name = 'tqc.transit.detalle'
    _description = 'Transito de Liquidaciones'

    # liquidacion_id = fields.Many2one('tqc.liquidaciones')
    tipo = fields.Char()
    subtipo = fields.Char()
    serie = fields.Char()
    numero = fields.Char()
    ruc = fields.Char()
    moneda = fields.Char()
    tipocambio = fields.Integer()
    fechaemision = fields.Date()
    #
    # base_afecta = fields.Monetary(currency_field='currency_id')
    # base_inafecta = fields.Monetary(currency_field='currency_id')
    # montoigv = fields.Monetary(currency_field='currency_id')
    # totaldocumento = fields.Monetary(currency_field='currency_id')
    #
    # cuenta_contable = fields.Many2one('cuenta.contable.gastos')
    tipodocumento = fields.Many2one('tqc.tipo.documentos')
    # observacionrepresentacion = fields.Text()
    # nocliente = fields.Char()
    #
    # currency_id = fields.Many2one('res.currency', string='Currency', required=True, readonly=False, store=True,
    #                               states={'reported': [('readonly', True)], 'approved': [('readonly', True)],
    #                                       'done': [('readonly', True)]}, compute='_compute_currency_id',
    #                               default=lambda self: self.env.company.currency_id)

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

    state = fields.Selection([
        ('document', 'Documento'),
        ('historial', 'Historial ERC')
    ], string='Tipo',
        help="Tipo de de solicitud" +
             "\nEl tipo 'Exportacion' es para exportacion de solicitudes" +
             "\nEl tipo 'Restaurar es para volverlos a su estado anterior de exportados")
