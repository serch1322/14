# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
from odoo import models, fields, api, _

class RentContract(models.Model):
    _name = 'car.insurance'
    _description = 'Insurance Management'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.depends('lineas_ids.subtotal')
    def _obtener_totales(self):
        total_concepts = 0.0
        for insurance in self:
            for line in insurance.lineas_ids:
                total_concepts = total_concepts + line.subtotal
            insurance.total_concepts = total_concepts

    total_concepts = fields.Float(string="Total", compute="_obtener_totales", store=True)
    name = fields.Char(string="Numero de Poliza",  required =True)
    supplier = fields.Many2one('res.partner',string="Proveedor", required =True)
    emergency_phone = fields.Char(string="Numero de Emergencia", required=True)
    invoice_date = fields.Date(string="Inicio de Poliza", required =True)
    end_date = fields.Date(string="Vencimiento Poliza", required =True)
    inciso = fields.Char(string="Inciso")
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user, index=True)
    state = fields.Selection(
        [('nuevo', 'Nuevo'), ('corriendo', 'Corriendo'), ('terminado', 'Terminado'), ('cancelado', 'Cancelado')], string="Estado",
        default="nuevo", copy=False)
    lineas_ids = fields.One2many('line.car.insurance','asegurados',readonly=False)

    def accion_aprobado(self):
        self.state = 'corriendo'
        self.ensure_one()
        factu_prov = self.env['account.move']
        valores_factu_prov = {}
        valores_factu_prov.update({
         'partner_id': self.supplier.id,
         'invoice_date': self.invoice_date,
         'ref': self.name,
         'move_type': 'in_invoice',
        })
        lista_factu = []
        if self.lineas_ids:
         for linea in self.lineas_ids:
             if linea.car:
                 lineas_factu = {
                     'name': linea.car.license_plate,
                     'quantity': linea.qty,
                     'price_unit': linea.price,
                 }
                 lista_factu.append((0, 0, lineas_factu))
        if lista_factu:
         valores_factu_prov.update({
             'invoice_line_ids': lista_factu,
         })
        factura_creada = factu_prov.create(valores_factu_prov)

    def accion_cancelado(self):
        self.state = 'cancelado'

    def accion_borrador(self):
        self.state = 'nuevo'

    # @api.model
    # def vencimento_seguro(self):
    #     if self.end_date <= date.today():
    #         self.state = 'terminado'

    # @api.model
    # def scheduler_manage_contract_expiration(self):
    #     # This method is called by a cron task
    #     # It manages the state of a contract, possibly by posting a message on the vehicle concerned and updating its status
    #     params = self.env['ir.config_parameter'].sudo()
    #     delay_alert_contract = int(params.get_param('hr_fleet.delay_alert_contract', default=30))
    #     date_today = fields.Date.from_string(fields.Date.today())
    #     outdated_days = fields.Date.to_string(date_today + relativedelta(days=+delay_alert_contract))
    #     nearly_expired_contracts = self.search([('state', '=', 'corriendo'), ('end_date', '<', outdated_days)])
    #
    #     for insurance in nearly_expired_contracts.filtered(lambda insurance: insurance.user_id):
    #         insurance.activity_schedule(
    #             'fleet.mail_act_fleet_contract_to_renew', insurance.end_date,
    #             user_id=insurance.user_id.id)
    #
    #     expired_contracts = self.search([('state', 'not in', ['terminado', 'cancelado']), ('expiration_date', '<',fields.Date.today() )])
    #     expired_contracts.write({'state': 'terminado'})
    #
    #     futur_contracts = self.search([('state', 'not in', ['nuevo', 'cancelado']), ('start_date', '>', fields.Date.today())])
    #     futur_contracts.write({'state': 'nuevo'})
    #
    #     now_running_contracts = self.search([('state', '=', 'nuevo'), ('start_date', '<=', fields.Date.today())])
    #     now_running_contracts.write({'state': 'corriendo'})
    #
    # def run_scheduler(self):
    #     self.scheduler_manage_contract_expiration()



class CarrosAsegurados(models.Model):
    _name = 'line.car.insurance'

    @api.depends('qty', 'price')
    def _get_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price

    asegurados = fields.Many2one('car.insurance',string="Carros Asegurados")
    car = fields.Many2one('fleet.vehicle',string="Vehículo", required=True, domain="[('insurance_count','=','0')]")
    price = fields.Float(string="Costo de Poliza")
    qty = fields.Float(default= 1 ,string="Cantidad", readonly= True)
    subtotal = fields.Float(string="Subtotal", compute="_get_subtotal", store=True)

class SeguroenVehiculo(models.Model):
    _inherit = ['fleet.vehicle']

    insurance_count = fields.Integer(compute="_compute_count_all", string="Seguro", store=True)

    def _compute_count_all(self):
        Odometer = self.env['fleet.vehicle.odometer']
        LogService = self.env['fleet.vehicle.log.services']
        LogContract = self.env['fleet.vehicle.log.contract']
        insurance = self.env['car.insurance']
        for record in self:
            record.odometer_count = Odometer.search_count([('vehicle_id', '=', record.id)])
            record.service_count = LogService.search_count([('vehicle_id', '=', record.id)])
            record.contract_count = LogContract.search_count([('vehicle_id', '=', record.id), ('state', '!=', 'closed')])
            record.history_count = self.env['fleet.vehicle.assignation.log'].search_count([('vehicle_id', '=', record.id)])
            record.insurance_count = insurance.search_count([('lineas_ids.car', '=', record.id), ('state', '=', 'corriendo')])

    def abrir_seguros(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Seguros',
            'view_mode': 'tree',
            'res_model': 'car.insurance',
            'domain': [('state', '=', 'corriendo'),('lineas_ids.car', '=', self.id)],
        }