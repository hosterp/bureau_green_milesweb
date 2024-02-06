from openerp import fields, models, api
from openerp.osv import osv
from dateutil.relativedelta import *
from datetime import timedelta,datetime


class FleetInherits(models.Model):
    _inherit = 'fleet.vehicle'

    rent_amount = fields.Float('Rent Amount')
    is_a_mach = fields.Boolean('Ia A Machinery ?')





class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_insurer = fields.Boolean('Is Insurer')
    is_rent_mach_owner = fields.Boolean(string='Is Rent Machine Owner')
    is_rent_vehicle = fields.Boolean("Is Rent Vehicle Owner")


class VehicleLogservices1(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    def _get_default_service_type(self, cr, uid, context):
        try:
            model, model_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'fleet',
                                                                                  'type_service_service_8')
        except ValueError:
            model_id = False
        return model_id

    _defaults = {
        'cost_subtype_id': _get_default_service_type,
        'cost_type': 'services'
    }
    date_com = fields.Date('Date')
    odometer_end = fields.Float('Km/Hrs Reading')
    start_location = fields.Char('Location From')
    dest_location = fields.Char('Location To')
    opening_bal = fields.Float('Opening Balance')
    ending_bal = fields.Float('Ending Balance')
    nature_id = fields.Many2one('work.nature', 'Nature Of Work/Complaint')
    works_done = fields.Text('Works Done')
    mechanic_id = fields.Many2many('mechanic.person', string='Mechanic')
    maintenance_type_id = fields.Many2one('maintanence.type', 'Type of Maintenance')
    daily_maint_bool = fields.Boolean('Daily Maintenance', default=True)
    r_b_bool = fields.Boolean('Repair/Breakdown')
    prev_main_bool = fields.Boolean('Preventive Maintenance')
    project_id = fields.Many2one('project.project', 'Project')
    reg_code = fields.Many2one('vehicle.category.type', related="vehicle_id.vehicle_categ_id")
    tyre_bool = fields.Boolean('Tyre Repairs')
    other_bool = fields.Boolean('Other Repairs')
    last_main = fields.Date('Last Maintenance Attended')
    greasing_bool = fields.Boolean('Greasing')
    inspec_bool = fields.Boolean('All Round Insp')
    oil_check_bool = fields.Boolean('Oil Checks')
    tyre_battery_bool = fields.Boolean('Tyres/Battery')
    nature_breakdown = fields.Char('Nature Of breakdown')
    complete_work = fields.Boolean('Completed')
    taken_out_tyre = fields.Many2one('fleet.vehicle', 'Tyre taken Out From')
    fitted_tyre = fields.Many2one('fleet.vehicle', 'Tyre fitted To')
    type_tyre_work = fields.Selection([('retar', 'Rethread'),
                                       ('new', 'New')], 'Rethread/New')
    mileage = fields.Float('Mileage')
    date_of_rectification = fields.Date("Date of Rectification")
    target_date_completion = fields.Date("Target Date of Completion")
    tyre_fitting_date = fields.Date("Tyre Fitting Date")
    last_pmr_reading = fields.Float("Last Service SMR Reading")
    service_period = fields.Float("Service Period")
    vehicle_preventive_maintenance_line_ids = fields.One2many('vehicle.preventive.maintenance.line', 'service_id')
    # amount = fields.Float(string="Amount",compute='_get_total_amount')
    #
    # @api.depends('cost_ids')
    # def _get_total_amount(self):
    #     for rec in self:
    #         total = 0
    #         for cost in rec.cost_ids:
    #             total += cost.amount
    #         rec.amount = total


class VehicleRouteMapping(models.Model):
    _name = 'fleet.route.mapping'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    driver_id = fields.Many2one('hr.employee', string='Driver')
    routes = fields.One2many('fleet.route.mapping.line','route_id')
    start_bal = fields.Float('Start Balance')
    # end_bal = fields.Float('End Balance', compute="_compute_end_balance")


    @api.onchange('vehicle_id')
    def onchange_driver(self):
    	self.driver_id = self.vehicle_id.hr_driver_id.id

	# @api.multi
	# def _compute_end_balance(self):
	# 	for record in self:
	# 		bal = record.start_bal
	# 		for rec in record.routes:
	# 			bal = bal - rec.ending_bal


class VehicleRouteMapping1(models.Model):
    _name = 'fleet.route.mapping.line'

    route_id = fields.Many2one('fleet.route.mapping')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', related='route_id.vehicle_id')
    # license_plate = fields.Char('License Plate', related='vehicle.license_plate')
    time_from = fields.Datetime('Start Time')
    time_to = fields.Datetime('End Time')
    driver_id = fields.Many2one('hr.employee', string='Driver', related='route_id.driver_id')
    odometer_start = fields.Float('Odometer Start Value')
    odometer_end = fields.Float('Odometer End Value')
    start_location = fields.Many2one('stock.location', string='Route From')
    dest_location = fields.Many2one('stock.location', string='Route To')
    opening_bal = fields.Float('Opening Balance')
    ending_bal = fields.Float('Ending Balance')

    stocks = fields.One2many('fleet.vehicle.stock','stock_id')

    @api.onchange('vehicle_id')
    def onchange_driver(self):
    	self.driver_id = self.vehicle_id.hr_driver_id.id

    

class VehicleRouteMapping2(models.Model):
    _name = 'fleet.vehicle.stock'

    stock_id = fields.Many2one('fleet.route.mapping.line')
    product_id = fields.Many2one('product.product', string='Product')
    description = fields.Char('Description')
    quantity = fields.Float('Quantity')



class VehicleDocuments(models.Model):
    _name = 'fleet.vehicle.documents'
    _order = 'date desc'

    @api.depends('vehicle_id')
    def compute_view_count(self):
        for rec in self:
            rec.attach_count = self.env['ir.attachment'].search_count(
                [('res_model', '=', 'fleet.vehicle.documents'), ('res_id', '=', rec.id)])


    date = fields.Date('Date',default=lambda self: fields.datetime.now())
    renewal_date = fields.Date('Renewal Date')
    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle", domain="[('rent_vehicle','!=',True)]")
    vehicle_type = fields.Many2one('vehicle.category.type', string="Vehicle Type", related='vehicle_id.vehicle_categ_id')
    amount = fields.Float('Amount')
    journal_id = fields.Many2one('account.journal',string='Mode Of Payment', domain="[('type','in',['cash','bank'])]")
    account_id = fields.Many2one('account.account', string="Debit Account")
    insurer_id = fields.Many2one('res.partner', string="Insurance Company")
    state = fields.Selection([('draft','Draft'),('paid','Paid')], default="draft")
    document_type = fields.Selection([('pollution','Pollution'),
                                    ('road_tax','Road Tax'),
                                    ('fitness','Fitness'),
                                    ('insurance','Insurance'),
                                    ('permit','Permit'),
                                      ('gps','GPS'),
                                    ], string="Document Type")
    is_account_entry = fields.Boolean('Is Account Entry Needed?', default=True)
    attach_count = fields.Float("Attachments",compute='compute_view_count')
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    renewal_duration = fields.Integer("Renewal Duration")
    renewal_type = fields.Selection([('month','Months'),
                                     ('year','Year')],default='month',)

    @api.onchange('end_date')
    def onchange_renewal_date(self):
        if self.end_date:
            date =datetime.strptime(self.end_date,"%Y-%m-%d")
            if self.document_type == 'pollution':
                self.renewal_date = date - timedelta(days=15)
            if self.document_type == 'fitness':
                self.renewal_date = date - timedelta(days=15)
            if self.document_type == 'insurance':
                self.renewal_date = date - timedelta(days=15)
            if self.document_type == 'permit':
                self.renewal_date =date - timedelta(days=15)

   

    @api.multi
    def button_payment(self):

        move = self.env['account.move']
        move_line = self.env['account.move.line']
        re_date = datetime.strptime(self.end_date,"%Y-%m-%d")

        if self.document_type == 'pollution':
            self.renewal_date = re_date - timedelta(days=15)

        if self.document_type == 'fitness':
            self.renewal_date = re_date - timedelta(days=15)

        if self.document_type == 'insurance':
            self.renewal_date = re_date - timedelta(days=15)

        if self.document_type == 'permit':
            self.renewal_date = re_date - timedelta(days=15)

        if self.document_type == 'road_tax':
            self.renewal_date = re_date - timedelta(days=15)
            self.vehicle_id.roadtax_date = re_date - timedelta(days=15)

        if self.account_id.id == False and self.journal_id.id == False:
            raise osv.except_osv(('Error'), ('Please configure journal and account for this payment'));
        elif self.account_id.id == False:
            raise osv.except_osv(('Error'), ('Please configure account for this payment'));
        elif self.journal_id.id == False:
            raise osv.except_osv(('Error'), ('Please configure journal for this payment'));
        else:
            pass

        values = {
                'journal_id': self.journal_id.id,
                # 'date': rec.date,
                }
        move_id = move.create(values)

        values = {
                'account_id': self.journal_id.default_credit_account_id.id,
                'name': str(self.document_type) + 'Payment',
                'debit': self.amount,
                'credit': 0,
                'move_id': move_id.id,
                }
        line_id = move_line.create(values)


        values2 = {
                'account_id': self.account_id.id,
                'name': str(self.document_type) + 'Payment',
                'debit': 0,
                'credit': self.amount,
                'move_id': move_id.id,
                }
        line_id = move_line.create(values2)
        move_id.button_validate()
        self.state = 'paid'
        if self.document_type == 'insurance':
            date = datetime.strptime(self.end_date,"%Y-%m-%d")
            time = self.renewal_duration
            self.vehicle_id.insu_start_date = date + timedelta(days=1)
            if self.renewal_type == 'month':
                self.vehicle_id.next_payment_date_ins = date  + relativedelta(months=self.renewal_duration)
            else:

                self.vehicle_id.next_payment_date_ins = datetime.strptime((date).strftime("%Y-%m-%d"),"%Y-%m-%d") + relativedelta(years=time)
            self.vehicle_id.last_paid_date_ins = self.date
            re_date = datetime.strptime(self.vehicle_id.next_payment_date_ins, "%Y-%m-%d")
            self.vehicle_id.insurance_date = re_date - timedelta(days=15)
        if self.document_type=='permit':
            date = datetime.strptime(self.end_date, "%Y-%m-%d")
            self.vehicle_id.permit_start_date = date + timedelta(days=1)
            if self.renewal_type == 'month':
                self.vehicle_id.permit_end_date = date  + relativedelta(
                    months=self.renewal_duration)
            else:
                self.vehicle_id.permit_end_date = date  + relativedelta(
                    years=self.renewal_duration)
            re_date = datetime.strptime(self.vehicle_id.permit_end_date, "%Y-%m-%d")
            self.vehicle_id.permit_date = re_date - timedelta(days=15)
        if self.document_type=='fitness':
            date = datetime.strptime(self.end_date, "%Y-%m-%d")
            self.vehicle_id.fitness_start_date = date + timedelta(days=1)
            if self.renewal_type == 'month':
                self.vehicle_id.fitness_end_date = date  + relativedelta(
                    months=self.renewal_duration)
            else:
                self.vehicle_id.fitness_end_date = date  + relativedelta(
                    years=self.renewal_duration)

            re_date = datetime.strptime(self.vehicle_id.fitness_end_date, "%Y-%m-%d")
            self.vehicle_id.fitness_date = re_date - timedelta(days=15)
        if self.document_type=='pollution':
            date = datetime.strptime(self.end_date, "%Y-%m-%d")
            self.vehicle_id.pollution_start_date = date + timedelta(days=1)
            if self.renewal_type == 'month':
                self.vehicle_id.pollution_end_date = date + relativedelta(
                    months=self.renewal_duration)
            else:
                self.vehicle_id.pollution_end_date = date + relativedelta(
                    years=self.renewal_duration)
            re_date = datetime.strptime(self.vehicle_id.pollution_end_date, "%Y-%m-%d")
            self.vehicle_id.pollution_date = re_date - timedelta(days=15)
        if self.document_type=='road_tax':
            date = datetime.strptime(self.end_date, "%Y-%m-%d")
            self.vehicle_id.road_tax_start_date = date + timedelta(days=1)
            if self.renewal_type == 'month':
                self.vehicle_id.road_tax_end_date = date + relativedelta(
                    months=self.renewal_duration)
            else:
                self.vehicle_id.road_tax_end_date = date  + relativedelta(
                    years=self.renewal_duration)
            re_date = datetime.strptime(self.vehicle_id.road_tax_end_date, "%Y-%m-%d")
            self.vehicle_id.roadtax_date = re_date - timedelta(days=15)





