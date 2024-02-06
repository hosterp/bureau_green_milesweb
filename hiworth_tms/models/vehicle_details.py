from openerp.exceptions import except_orm, ValidationError
#from openerp.tools import DEFAULT_SERVER_DateTIME_FORMAT
from openerp import models, fields, api, _
from openerp import workflow
import time
from datetime import datetime
#from datetime import datetime, timedelta
from datetime import date
#from openerp.osv import fields, osv
from openerp.tools.translate import _
#from openerp import SUPERUSER_ID
import openerp.addons.decimal_precision as dp
#from openerp.osv import fields, osv
from datetime import timedelta
from lxml import etree



class bank_emi_lines(models.Model):
    _name = 'bank.emi.lines'
    
    
    name = fields.Char('Name', size=64)
    date = fields.Date('Date')
    payment_mode = fields.Selection([('cash','Cash'),('bank','Bank'),('cheque','Cheque')], 'Mode Of Payment', select=True)
    reference = fields.Text('Reference')
    amount = fields.Float('Amount', Default=0.0)
    emi_line = fields.Many2one('fleet.vehicle', 'EMI Payment Details')
    receipt_no = fields.Char('Receipt No', size=64)
    
    
class bank_emi_lines(models.Model):
    _name = 'agent.ins.lines'
    
    
    name = fields.Char('Name', size=64)
    date = fields.Date('Date')
    payment_mode = fields.Selection([('cash','Cash'),('bank','Bank'),('cheque','Cheque')], 'Mode Of Payment', select=True)
    reference = fields.Text('Reference')
    amount = fields.Float('Amount', Default=0.0)
    ins_line = fields.Many2one('fleet.vehicle', 'Insurance Payment Details')
    receipt_no = fields.Char('Receipt No', size=64)
    
    
    
class puc_lines(models.Model):
    _name = 'puc.lines'
    
    
    name = fields.Char('Name', size=64)
    date = fields.Date('Date')
    exp_date = fields.Date('Expiry Date')
    reference = fields.Text('Reference')
    amount = fields.Float('Amount', Default=0.0)
    puc_line = fields.Many2one('fleet.vehicle', 'Insurance Payment Details')
    receipt_no = fields.Char('Receipt No', size=64)



class VehiclePreventiveMaintenance(models.Model):
    _name = 'vehicle.preventive.maintenance'
    _rec_name = 'vehicle_id'

    vehicle_id = fields.Many2one('fleet.vehicle', "Vehicle", required=False)
    vehicle_preventive_maintenance_line_ids = fields.One2many('vehicle.preventive.maintenance.line','vehicle_preventive_maintenance_id',"Maintenance")


class VehiclePreventiveMaintenanceLine(models.Model):
    _name = 'vehicle.preventive.maintenance.line'

    @api.depends('service_period','last_service_km')
    def compute_next_service(self):
        for rec in self:
            rec.next_service_km = rec.last_service_km + rec.service_period

    vehicle_id = fields.Many2one('fleet.vehicle', "Vehicle", required=False)
    date = fields.Date("Date")
    last_service_km = fields.Float("Last Service KM/HRS")
    service_period = fields.Float("Service Period")
    cost = fields.Float()
    next_service_km = fields.Float("Next Service KM/HRS",compute='compute_next_service',store=True)
    remarks = fields.Char("Remarks")
    work = fields.Char("Nature of Work")
    vehicle_preventive_maintenance_id = fields.Many2one('vehicle.preventive.maintenance', "Vehicle Preventive Maintenance", required=False)
    service_id = fields.Many2one('fleet.vehicle.log.services')

    # @api.onchange('date')
    # def onchange_date(self):
    #     for rec in self:
    #     if service_id.

    @api.model
    def create(self, vals):
        if 'service_id' in vals:
            parent = self.env['fleet.vehicle.log.services'].browse(vals['service_id'])
            vals.update({'vehicle_id': parent.vehicle_id.id,})
        res = super(VehiclePreventiveMaintenanceLine, self).create(vals)
        return res
    

class fleet_vehicle(models.Model):
    _inherit = 'fleet.vehicle'

    no_of_tyres = fields.Integer()
    retreading_tyre_line_ids = fields.One2many('retreading.tyre.line', 'vehicle_id')
    registration_date = fields.Date()
    work_location = fields.Many2one('stock.location')



    def _generate_virtual_location(self, cr, uid, truck, vehicle_ok, trailer_ok, context): 
        pass
    
    
    # def onchange_basic_odometer(self, cr, uid, ids, counter_basic, context=None):
    #     data={}
    #     if counter_basic:
    #         data['odometer'] = counter_basic
    #     return {'value' : data}

    @api.multi
    @api.depends('counter_basic','meter_lines')
    def get_odometer(self):
        for rec in self:
            if not rec.meter_lines:
                rec.odometer = rec.counter_basic
            else:
                odometers = self.env['vehicle.meter'].search([('vehicle_id','=',rec.id)], order='date desc', limit=1)
                rec.odometer = odometers.end_value

    is_rent_mach = fields.Boolean(string="Is Rent Machinery")

    owner = fields.Many2one('res.partner', 'Owner', size=64)
    manager = fields.Many2one('res.partner', 'Manager', size=64)
    
    gasoil_id = fields.Many2one('product.product', 'Fuel', required=False, domain=[('fuel_ok','=','True')])
    
    emi_no = fields.Char('EMI No', size=64)
    bank_id = fields.Many2one('res.bank','Bank Details')
    emi_lines =  fields.One2many('bank.emi.lines','emi_line', 'EMI Payment Details')
    emi_start_date = fields.Date('Beginning Date')
    last_paid_date = fields.Date('Last Date')
    next_payment_date = fields.Date('Next Payment Date')
    total_due = fields.Float('Total Due', Default=0.0)
    total_paid = fields.Float('Total Paid', Default=0.0)
    balance_due = fields.Float('Balance', Default=0.0)
    emi_amt = fields.Float("EMI Amount")
    ins_no = fields.Char('EMI No', size=64)
    agent_id = fields.Many2one('res.partner','Agent Details')
    insu_start_date = fields.Date("Start Date")
    ins_lines = fields.One2many('agent.ins.lines','ins_line', 'Insurance Payment Details')
    last_paid_date_ins = fields.Date('Last Date Paid')
    next_payment_date_ins = fields.Date('Next Payment Date')
    permit_start_date = fields.Date("Start Date")
    permit_end_date = fields.Date("End Date")

    puc_lines = fields.One2many('puc.lines','puc_line', 'PUC Details')
    vehilce_old_odometer = fields.Float('Vehicle Old Old OdoMeter', readonly=False)     
    mileage = fields.Float('Mileage', readonly=False, compute="_compute_mileage",store=True)
    fuel_odometer = fields.Float('Fuel Odometer',  default=0.0)
    related_account = fields.Many2one('account.account', required=False)
    asset_account_id = fields.Many2one('account.account','Asset Account')
    trip_commission = fields.Float('Trip Commission %')
    state = fields.Selection([('park','Parking'),('travel','Travelling'),
                                  ('maintenance','For Maintenance')], 'State', select=True)
    meter_lines = fields.One2many('vehicle.meter', 'vehicle_id', 'Meter Statement')
    fuel_lines = fields.One2many('vehicle.fuel.voucher', 'vehicle_id', 'Fuel Voucher')
    odometer = fields.Float(string='Last Odometer', help='Odometer measure of the vehicle at this moment')
    last_odometer = fields.Float(string="Odometer",help='Odometer measure of the vehicle at this moment')
    rate_per_km = fields.Float('Rate Per Km')
    vehicle_under  =fields.Many2one('res.partner','Vehicle Owner')
    per_day_rent = fields.Float('Rent Per Day')
    rent_vehicle = fields.Boolean(default=False)
    machinery = fields.Boolean(default=False)
    mach_rent_type = fields.Selection([('hours','For Hours'),
                                        ('days','For Days'),
                                        ('months','For Months')
                                        ], string="Rent Type", default="hours")
    counter_basic = fields.Float('base', digits=(20,3))
    brand_id = fields.Many2one('fleet.vehicle.model.brand', 'Brand')
    hr_driver_id = fields.Many2one('hr.employee', string='Driver', domain=[('driver_ok','=',True)])
    vehicle_ok = fields.Boolean('Vehicle')
    model_id = fields.Many2one('fleet.vehicle.model', 'Model', required=False)

    name = fields.Char(compute="_get_tms_vehicle_name", string='Nom', store=True)
    full_supply = fields.Boolean(default=False,string="Full Supply")
    full_supply_line = fields.One2many('fullsupply.line','line_id')
    capacity = fields.Float('Capacity')
    # vehicle_type = fields.Selection([('eicher','Eicher'),
    #                                 ('taurus','Taurus'),
    #                                 ('pickup','Pick Up')
    #                                 ])

    vehicle_categ_id = fields.Many2one('vehicle.category.type', string="Vehicle Type")
    eicher_categ = fields.Boolean('Eicher', compute="_compute_veh_category", store=True)
    taurus_categ = fields.Boolean('Taurus', compute="_compute_veh_category",  store=True)
    insurance_date = fields.Date('Renewal Date')
    pollution_date = fields.Date('Renewal Date')
    roadtax_date = fields.Date('Renewal Date')
    fitness_date = fields.Date('Renewal Date')
    permit_date = fields.Date('Renewal Date')
    fitness_start_date = fields.Date("Start Date")
    fitness_end_date = fields.Date("End Date")
    pollution_start_date = fields.Date("Start Date")
    pollution_end_date = fields.Date("End Date")
    road_tax_start_date = fields.Date("Start Date")
    road_tax_end_date = fields.Date("End Date")
    tyre_detials_ids = fields.One2many('vehicle.tyre','vehicle_id',"Tyre Details")
    battery_details_ids = fields.One2many('vehicle.battery','vehicle_id',"Battery Details")
    gps_start_date = fields.Date("Start Date")
    gps_end_date = fields.Date("End Date")
    gps_renew_date = fields.Date("Renew Date")
    permit_no = fields.Char("No")
    pollu_amt_last_paid = fields.Float("Last Paid")
    road_amt_last_paid = fields.Float("Last Paid")
    insu_amt_last_paid = fields.Float("Last Paid")
    vehicle_gps_ids = fields.One2many('vehicle.gps','vehicle_id',"GPS")
    retreading_ids = fields.One2many('retreading.tyre.line', 'vehicle_id', "Tyre Retreading")

    @api.multi
    def print_report(self):
        return{
                'name':  _('Print Maintenance Details'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'print.vehicle',
                'type': 'ir.actions.act_window',
                'view_id': self.env.ref('hiworth_tms.print_vehicle_wizard_view').id,
                'target': 'new',
                'context': {'vehicle_id': self.id}

        }

    @api.multi
    def return_action_to_open(self):
        """ This opens the xml view specified in xml_id for the current vehicle """

        return {
            'name': 'Contracts',
            'view_type': 'form',
            'view_mode': 'tree,form',

            'res_model': 'fleet.vehicle.log.contract',
            'domain':[('vehicle_id','=',self.id)],
            'type': 'ir.actions.act_window',
            'context':{'default_vehicle_id':self.id,
                       'default_opening_odometer':self.last_odometer,
                       'default_purchase_date':self.acquisition_date,
                       'default_start_date':self.acquisition_date,
                       'default_purchaser_id':self.vehicle_under.id,
                       }

        }

    @api.multi
    def button_view_other_expenses(self):
        return {
            'name': 'Other Expense',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'driver.daily.expense',
            'domain': [('vehicle_id', '=', self.id)],
            'type': 'ir.actions.act_window',

        }

    @api.multi
    def button_view_payment_voucher(self):
        return {
            'name': 'Cashier Payments',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'res_model': 'payment.vouchers',
            'domain': [('opp_account_id', '=', self.related_account.id)],
            'type': 'ir.actions.act_window',

        }


    @api.multi
    def button_view_goods_purchases(self):
        for rec in self:
            services = self.env['fleet.vehicle.log.services'].search([('vehicle_id','=',self.id)])
            # goods_list = []
            # for goods in goods_recive:
            #     goods_list.extend(goods.goods_recieve_report_line_ids.ids)
            return {
                'name': 'Repair Maintenances',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
                'res_model': 'fleet.vehicle.log.services',
                'domain':[('id', 'in', services.ids)],
                'type': 'ir.actions.act_window',


            }

    @api.multi
    def button_view_services(self):
        for rec in self:
            services = self.env['vehicle.preventive.maintenance'].search([('vehicle_id', '=', self.id)])
            # goods_list = []
            # for goods in goods_recive:
            #     goods_list.extend(goods.goods_recieve_report_line_ids.ids)
            return {
                'name': 'Preventive Maintenances',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'target': 'current',
                'res_model': 'vehicle.preventive.maintenance',
                'domain': [('id', 'in', services.ids)],
                'type': 'ir.actions.act_window',

            }

        # view_tree = self.env.ref('expense_voucher.view_mou_tree')
        # view_form = self.env.ref('expense_voucher.view_mou_form')
        # return {
        #     'name': 'Related MOU Details',
        #     'type': 'ir.actions.act_window',
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'res_model': 'mou.mou',
        #     'views': [(view_tree.id, 'tree'), (view_form.id, 'form')],
        #     'target': 'current',
        #     'domain': [('partner_id', '=', self.id)],
        # }


    @api.multi
    def button_action_documents_pollut(self):
        for rec in self:
            return {
                'name': 'Documents Renewal',
                'view_type': 'form',
                'view_mode': 'form',

                'res_model': 'fleet.vehicle.documents',

                'type': 'ir.actions.act_window',


                'context': {'default_vehicle_id':rec.id,
                            'default_start_date':rec.pollution_start_date,
                            'default_end_date':rec.pollution_end_date,
                            'default_renewal_date':rec.pollution_date,
                            'default_document_type':'pollution',
                            'default_vehicle_type':rec.vehicle_categ_id.id,
                            },
            }

    @api.multi
    def button_action_documents_road(self):
        for rec in self:
            return {
                'name': 'Documents Renewal',
                'view_type': 'form',
                'view_mode': 'form',

                'res_model': 'fleet.vehicle.documents',

                'type': 'ir.actions.act_window',


                'context': {'default_vehicle_id':rec.id,
                            'default_start_date':rec.road_tax_start_date,
                            'default_end_date':rec.road_tax_end_date,
                            'default_renewal_date':rec.roadtax_date,
                            'default_document_type':'road_tax',
                            'default_vehicle_type':rec.vehicle_categ_id.id,
                            },
            }

    @api.multi
    def button_action_documents_gps(self):
        for rec in self:
            return {
                'name': 'Documents Renewal',
                'view_type': 'form',
                'view_mode': 'form',

                'res_model': 'fleet.vehicle.documents',

                'type': 'ir.actions.act_window',

                'context': {'default_vehicle_id': rec.id,
                            'default_start_date': rec.gps_start_date,
                            'default_end_date': rec.gps_end_date,
                            'default_renewal_date': rec.gps_renew_date,
                            'default_document_type': 'gps',
                            'default_vehicle_type': rec.vehicle_categ_id.id,
                            },
            }

    @api.multi
    def button_action_documents_fitness(self):
        for rec in self:
            return {
                'name': 'Documents Renewal',
                'view_type': 'form',
                'view_mode': 'form',

                'res_model': 'fleet.vehicle.documents',

                'type': 'ir.actions.act_window',


                'context': {'default_vehicle_id':rec.id,
                            'default_start_date':rec.fitness_start_date,
                            'default_end_date':rec.fitness_end_date,
                            'default_renewal_date':rec.fitness_date,
                            'default_document_type':'fitness',
                            'default_vehicle_type':rec.vehicle_categ_id.id,
                            },
            }

    @api.multi
    def button_action_documents_insurance(self):
        for rec in self:
            return {
                'name': 'Documents Renewal',
                'view_type': 'form',
                'view_mode': 'form',

                'res_model': 'fleet.vehicle.documents',

                'type': 'ir.actions.act_window',


                'context': {'default_vehicle_id':rec.id,
                            'default_start_date':rec.insu_start_date,
                            'default_end_date':rec.next_payment_date_ins,
                            'default_renewal_date':rec.insurance_date,
                            'default_document_type':'insurance',
                            'default_vehicle_type':rec.vehicle_categ_id.id,
                            },
            }

    @api.multi
    def button_action_documents_permit(self):
        for rec in self:
            return {
                'name': 'Documents Renewal',
                'view_type': 'form',
                'view_mode': 'form',

                'res_model': 'fleet.vehicle.documents',

                'type': 'ir.actions.act_window',


                'context': {'default_vehicle_id':rec.id,
                            'default_start_date':rec.permit_start_date,
                            'default_end_date':rec.permit_end_date,
                            'default_renewal_date':rec.permit_date,
                            'default_document_type':'permit',
                            'default_vehicle_type':rec.vehicle_categ_id.id,
                            },
            }
    ############################# Vehicle status ###################################

    # from_date_status = fields.Date('From Date') 
    # to_date_status = fields.Date('To Date')






    @api.multi
    @api.depends('vehicle_categ_id')
    def _compute_veh_category(self):
        for record in self:
            print 'record.vehicle_categ_id------------------', record.vehicle_categ_id, self.env.ref('hiworth_tms.vehicle_category_eicher1').id
            if record.vehicle_categ_id.id == self.env.ref('hiworth_tms.vehicle_category_eicher1').id:
                record.eicher_categ = True
            elif record.vehicle_categ_id.id == self.env.ref('hiworth_tms.vehicle_category_taurus').id:
                record.taurus_categ = True
            else:
                pass


    @api.onchange('vehicle_under','full_supply')
    def onchange_full_supply_details(self):
        result = []
        if self.full_supply == True and self.vehicle_under:
            record = self.env['fleet.vehicle'].search([('vehicle_under','=', self.vehicle_under.id),('full_supply','=',True)], limit=1)
            
            for rec in record.full_supply_line:
                result.append((0, 0, {'date_from': rec.date_from, 'date_to': rec.date_to,'location_id': rec.location_id.id, 'product_id': rec.product_id.id, 'rate':rec.rate}))
            
            self.full_supply_line = result


    @api.depends('license_plate')
    def _get_tms_vehicle_name(self):
        for record in self:
            print 'vvvvvvvvvvvvvvvvvvv', record.license_plate, record.name
            record.name = record.license_plate
            print 'vvvvvvvvvvvvvvvvvvv', record.license_plate, record.name




    _defaults = {
         'state': 'park'
         }

    @api.constrains('name')
    def _check_duplicate_name(self):
        names = self.search([])
        for c in names:
            if self.id != c.id:
                if self.name and c.name:
                    if self.name.lower() == c.name.lower() or self.name.lower().replace(" ", "") == c.name.lower().replace(" ", ""):
                        raise osv.except_osv(_('Error!'), _('Error: vehicle name must be unique'))
            else:
                pass
    
    @api.model
    def create(self, vals):
        result = super(fleet_vehicle, self).create(vals)
        if result.rent_vehicle == False:
            if result.rate_per_km == 0.0:
                raise except_orm(_('Warning'),
                             _('The Rate Per Km not be zero'))
        return result


# <<<<<<< HEAD
    # @api.multi
    # def write(self, vals):
    #     result = super(fleet_vehicle, self).write(vals)
    #     if self.rent_vehicle == True:
    #         if vals.get('vehicle_under') != self.vehicle_under.id:
    #             if vals.get('vehicle_under') != self.vehicle_under.id:
    #                 raise except_orm(_('Warning'),
    #                          _('You cannot edit the vehicle owner..!!'))
# =======
    @api.multi
    def write(self, vals):
        result = super(fleet_vehicle, self).write(vals)
        if self.rent_vehicle:
            if vals.get('vehicle_under'):
                raise except_orm(_('Warning'),
                    _('You cannot edit the vehicle owner..!!'))
# >>>>>>> c987d8b138782ee76facfce09f088e8a88fe41b4

        return result

    
    
    @api.multi
    @api.depends('meter_lines','fuel_lines','brand_id')
    def _compute_mileage(self):
        for record in self:
            km = 0
            fuel = 0
            # for meter in record.meter_lines:
            # if record.meter_lines:
            #     km = record.meter_lines[-1].end_value
            #     print 'km------------------------', km
            rec = False
            for rec in record.fuel_lines:
                km += rec.total_reading
                fuel += rec.litre * rec.per_litre
            print 'fuel------------------------', fuel
            if rec:
                record.last_odometer = rec.closing_reading
            if fuel != 0 and km != 0:
                record.mileage = km/fuel





class VehicleCategoryType(models.Model):
    _name = 'vehicle.category.type'

    name = fields.Char(string="Vehicle Type")
    
class FullSupplyLine(models.Model):
    _name = 'fullsupply.line'

    line_id = fields.Many2one('fleet.vehicle')
    mou_id = fields.Many2one('mou.mou')
    date_from = fields.Date('From')
    date_to = fields.Date('To')
    location_id = fields.Many2one('stock.location','Location')
    product_id = fields.Many2one('product.product','Product')
    rate = fields.Float('Rate')


class fleet_vehicle_cost(models.Model):
    _inherit = 'fleet.vehicle.cost'

    particular = fields.Char('Particular', size=64)
    qty = fields.Float('Qty')
    rate = fields.Float('Rate')
    remarks = fields.Char("Remarks")
    insurance_date = fields.Date('Insurance Date')
    pollution_date = fields.Date('Pollution Date')
    roadtax_date = fields.Date('Road Tax Date')
    fitness_date = fields.Date('Fitness Date')
    permit_date = fields.Date('Permit Date')
    new_parts_name = fields.Char("New Part's name")
    old_parts_name = fields.Char("Replaced Part's name")
    total_amount = fields.Float(compute='compute_amount')
    date1 = fields.Date()

    @api.depends('rate', 'qty')
    def compute_amount(self):
        for rec in self:
            rec.total_amount = rec.qty * rec.rate


class VehicleMeter(models.Model):
    _name = 'vehicle.meter'
    _order = 'date desc'


    name = fields.Char('Name')
    date = fields.Date('Date')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    start_value = fields.Float('Start Value')
    end_value = fields.Float('End Value')
    fuel_value = fields.Float('Total Fuel Refilled')


class VehicleFuelVoucher(models.Model):
    _name = 'vehicle.fuel.voucher'
    _order = 'date desc'

    @api.multi
    @api.depends('litre','per_litre')
    def compute_amount(self):
        for rec in self:
            rec.amount = rec.litre * rec.per_litre

    @api.multi
    @api.depends('opening_reading', 'closing_reading')
    def compute_total_km(self):
        for rec in self:
            rec.total_reading = rec.closing_reading - rec.opening_reading

    name = fields.Char('Name')
    date = fields.Date('Date')
    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle')
    pump_id = fields.Many2one('res.partner','Diesel Pump', domain=[('diesel_pump_bool','=',True)])
    litre = fields.Float('Fuel Qty')
    per_litre = fields.Float('Fuel Price')
    amount = fields.Float(compute='compute_amount', store=True, string='Amount')
    odometer = fields.Float('Fuel Filling KM')
    opening_reading = fields.Float("Open Reading")
    closing_reading = fields.Float("Closing Reading")
    total_reading = fields.Float("Total Reading",compute='compute_total_km', store=True,)
    full_tank = fields.Boolean("Full Tank")
    item_char = fields.Char()

class fleet_vehicle_log_contract(models.Model):
    _inherit='fleet.vehicle.log.contract'
    _order = 'start_date desc'

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(fleet_vehicle_log_contract, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        if view_type == 'form':
            # Check if user is in group that allow creation
            doc = etree.XML(res['arch'])
            has_my_group = self.env.user.has_group('base.group_erp_manager')
            if has_my_group:
                if has_my_group:
                    root = etree.fromstring(res['arch'])
                    root.set('edit', 'true')
            res['arch'] = etree.tostring(root)
        return res


    @api.constrains('ending_odometer')
    def check_ending_odometer(self):
        for rec in self:
            if rec.ending_odometer < rec.opening_odometer:
                raise except_orm(_('Warning'),
                                 _('Ending Odometer must be greater than Opening Odometer'))


    amc_type = fields.Selection([('normal','Normal Warranty'),
                                 ('extend','Extend Warranty'),
                                 ('amc','AMC')],default='normal',string="Warranty Type")

    amc_section = fields.Selection([('comprehensive','Comprehensive'),
                                    ('non_comprehensive','Non - Comprehensive')],default='comprehensive',string="AMC Type")



    purchase_date = fields.Date("Purchase Date")
    opening_odometer = fields.Float("Opening Odometer")
    ending_odometer = fields.Float("Ending Odometer")
    no_of_calls = fields.Float("Number of Calls")
    odometer_vehicle = fields.Float("Current Odometer",related='vehicle_id.odometer')
    debit_account_id = fields.Many2one('account.account',"Debit Account")
    move_id = fields.Many2one('account.move',"Account entry")
    journal_id = fields.Many2one('account.journal',"Mode of Payment")
    @api.multi
    def act_renew_contract(self):
        for element in self:
            #compute end date
            startdate = datetime.strptime(element.start_date,"%Y-%m-%d")
            enddate = datetime.strptime(element.expiration_date,"%Y-%m-%d")
            diffdate = (enddate - startdate)
            default = {
                'default_opening_odometer':element.ending_odometer,
                'default_vehicle_id':element.vehicle_id.id,
                'default_purchase_date':element.purchase_date,
                'default_purchaser_id':element.purchaser_id.id,
                'default_start_date': (enddate + timedelta(days=1)).strftime("%Y-%m-%d"),
                'default_expiration_date': (enddate + timedelta(days=diffdate.days)).strftime("%Y-%m-%d"),
            }
            date = datetime.now().strftime("%Y-%m-%d")
            if self.amc_type in ['normal','extend']:
                if enddate <= datetime.now() or self.ending_odometer <= self.vehicle_id.last_odometer:
                    self.state = 'closed'

                    return {

                        'view_mode': 'form',

                        'view_type': 'tree,form',
                        'res_model': 'fleet.vehicle.log.contract',
                        'type': 'ir.actions.act_window',

                        'domain': [('vehicle_id','=',self.vehicle_id.id)],

                        'context':default ,
                    }
                else:
                    raise except_orm(_('Warning'),
                                     _('Vehicle is under Warranty/AMC'))
            else:
                if enddate <= datetime.now() or (self.no_of_calls!=0 and self.no_of_calls == len(self.cost_ids.ids)):
                    self.state = 'closed'

                    return {

                        'view_mode': 'form',

                        'view_type': 'tree,form',
                        'res_model': 'fleet.vehicle.log.contract',
                        'type': 'ir.actions.act_window',

                        'domain': [('vehicle_id', '=', self.vehicle_id.id),],

                        'context': default,
                    }
                else:
                    raise except_orm(_('Warning'),
                                     _('Vehicle is under Warranty/AMC'))


class PrintVehicle(models.TransientModel):
    _name = 'print.vehicle'

    date_from = fields.Date()
    date_to = fields.Date()

    @api.multi
    def print_report(self):
        vehicle = self.env['fleet.vehicle'].browse(self._context['vehicle_id'])
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read()[0],
            'vehicle': vehicle.id,
            # 'maintenance': maintenance,
            # 'battery_details_ids': battery_details_ids,
            # 'vehicle_gps_ids': vehicle_gps_ids,
            # 'fuel_lines': fuel_lines,
            # 'retreading_ids': retreading_ids,
            # 'tyre_detials_ids': tyre_detials_ids,

        }

        return {
            'name': 'Vehicle Details',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_tms.vehicle_details_custom_report',
            'data': datas,
            'report_type': 'qweb-pdf'
        }
