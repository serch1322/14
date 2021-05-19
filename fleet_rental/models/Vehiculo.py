# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import datetime

class EntidadMatricula(models.Model):
    _inherit = ['fleet.vehicle']

    entidad = fields.Many2one('res.country.state', string="Entidad de Matricula")
    future_driver = fields.Many2many('res.partner', string="Conductores Aprobados", tracking=True, help='Next Driver of the vehicle',
                                       copy=False,
                                       domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    serie_motor = fields.Char(string="Numero de Serie Motor")
    numero_cilindros = fields.Float(string="Numero de Cilindros")
    seats = fields.Integer(string="Numero de Pasajeros", help='Number of seats of the vehicle')
    carga= fields.Float(string="Capacidad de Carga")
    categoria = fields.Many2one('car.category',string="Categoria de Vehiculo")
    tipo = fields.Selection(related='categoria.tipo')
    depr = fields.Selection([('total', 'Depreciación Total'), ('parcial', 'Depreciación Parcial')],string="Tipo de Depreciación",default=False)

    def depreciacion(self):
        if 'tipo' == 'carga':
            self.ensure_one()
            activo = self.env['account.asset']
            valores_activo = {}
            valores_activo.update({
                'name': self.license_plate,
                'original_value': self.net_car_value,
                'acquisition_date': self.acquisition_date,
                'salvage_value': 0,
                'method': 'linear',
                'method_number':48,
                'method_period':1,
                'first_depreciation_date': date.today(),
                'company_id':1,
                'account_asset_id': self.categoria.activo.id,
                'account_depreciation_id': self.categoria.amortizacion.id,
                'account_depreciation_expense_id': self.categoria.gasto.id,
                'journal_id': 3,
                'state':'open',

            })
            activo_creado = activo.create(valores_activo)
        else:
            if 'depr' == 'total':
                self.ensure_one()
                activo = self.env['account.asset']
                valores_activo = {}
                valores_activo.update({
                    'name': self.license_plate,
                    'original_value': self.net_car_value,
                    'acquisition_date': self.acquisition_date,
                    'salvage_value': 0,
                    'method': 'linear',
                    'method_number': 1,
                    'method_period': 1,
                    'first_depreciation_date': date.today(),
                    'company_id': 1,
                    'account_asset_id': self.categoria.activo.id,
                    'account_depreciation_id': self.categoria.amortizacion.id,
                    'account_depreciation_expense_id': self.categoria.gasto.id,
                    'journal_id': 3,
                    'state': 'open',

                })
                activo_creado = activo.create(valores_activo)
            else:
                if 'self.net_car_value' > '175000':
                    self.ensure_one()
                    activo = self.env['account.asset']
                    valores_activo = {}
                    valores_activo.update({
                        'name': self.license_plate,
                        'original_value': self.net_car_value,
                        'acquisition_date': self.acquisition_date,
                        'salvage_value': self.net_car_value - 175000,
                        'method': 'linear',
                        'method_number': 48,
                        'method_period': 1,
                        'first_depreciation_date': date.today(),
                        'company_id': 1,
                        'account_asset_id': self.categoria.activo.id,
                        'account_depreciation_id': self.categoria.amortizacion.id,
                        'account_depreciation_expense_id': self.categoria.gasto.id,
                        'journal_id': 3,
                        'state': 'open',

                    })
                    activo_creado = activo.create(valores_activo)
                elif 'self.net_car_value' <= '175000':
                    self.ensure_one()
                    activo = self.env['account.asset']
                    valores_activo = {}
                    valores_activo.update({
                        'name': self.license_plate,
                        'original_value': self.net_car_value,
                        'acquisition_date': self.acquisition_date,
                        'salvage_value': 0,
                        'method': 'linear',
                        'method_number': 48,
                        'method_period': 1,
                        'first_depreciation_date': date.today(),
                        'company_id': 1,
                        'account_asset_id': self.categoria.activo.id,
                        'account_depreciation_id': self.categoria.amortizacion.id,
                        'account_depreciation_expense_id': self.categoria.gasto.id,
                        'journal_id': 3,
                        'state': 'open',

                    })
                    activo_creado = activo.create(valores_activo)


