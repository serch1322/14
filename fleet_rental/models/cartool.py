# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CarTools(models.Model):
    _name = 'car.tools'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nombre")
    num_serie = fields.Char(string="Número de Serie")
    costo = fields.Float(string="Costo")
    state = fields.Selection([('disponible','Disponible'),('reservado','Reservado'),('renta','Renta'),('vendido','Vendido'),('servicio','Servicio')],
                             string="Estado",default='disponible',copy=False)

    marca = fields.Char(string="Marca")
    rent_price = fields.Float(string="Precio de Renta")
    modelo = fields.Char(string="Modelo")
    date_compra = fields.Date(string="Año de Compra")
    date_fabric = fields.Date(string="Año de Fabricacion")
    descripcion = fields.Char(string="Descripcion")
    tipo = fields.Selection([('aditamento', 'Aditamento'), ('accesorio', 'Accesorio')],
                            string="Tipo", copy=False, required=True)
    car = fields.Many2one('fleet.vehicle', string="Vehículo Asociado")

    def vendido(self):
        self.state = 'vendido'

    def cambiar_disponible(self):
        self.state = 'disponible'