from openerp import models, fields, api, _
from openerp import exceptions
import dateutil.parser
from dateutil.relativedelta import relativedelta
# from dateutil import relativedelta
import time
from datetime import datetime, date, timedelta
import openerp.addons.decimal_precision as dp
import calendar
from openerp import tools
from openerp.exceptions import except_orm, ValidationError
import calendar
from datetime import *
from dateutil.relativedelta import *
from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import osv


# from openerp.osv import fields, osv


# class HrJob(models.Model):
#     _inherit = 'hr.job'

#     code = fields.Char('Code',required=True)

class BranchProject(models.Model):
    _name = 'branch.project'

    name = fields.Char('Branch Name', required=True)
    code = fields.Char('Code', required=True)


class ResPartner1(models.Model):
    _inherit = 'res.partner'

    contractor = fields.Boolean('Contractor')
    res_company_new = fields.Boolean(default=False)
    company_contractor = fields.Boolean('Company Contractor')

    

# class CompanyNew(models.Model):
#     _name='res.company.new'
#     _inherits = {'res.partner':'partner_id'}
#
#     # name = fields.Char('Company Name')
#
#     @api.model
#     def create(self,vals):
#         print 'res.company.new---------------------------------------', vals.get('res.company.new')
#         vals['res_company_new'] = True
#         return super(CompanyNew, self).create(vals)

class TechnicalTraining(models.Model):
    _name = 'technical.training'

    emp_id = fields.Many2one('hr.employee')
    name = fields.Char(string="Training")
    year_pass = fields.Char(string="Year of Passing")

# class EmployeePosition(models.Model):
#     _name = 'employee.position'
#
#     name = fields.Char(string="Employee Position")

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    date_rejoin = fields.Date('Rejoin Date')
    wages = fields.Float('Basic Salary')

    @api.multi
    def cash_transfer(self):
        view_ref = self.env['ir.model.data'].get_object_reference('hiworth_construction', 'view_cash_transfer_amount')
        view_id = view_ref[1] if view_ref else False
        res = {
            'type': 'ir.actions.act_window',
            'name': _('Cash Transfer'),
            'res_model': 'cash.transfer',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'new',
            'context': {'default_name': self.id}
        }

        return res
    @api.multi
    def view_action_rejoin(self):
        self.date_rejoin = date.today()
        self.status1 = 'active'
        return self.date_rejoin


    @api.multi
    def view_stmts(self):
        view_id = self.env.ref('hiworth_accounting.view_account_form_hiworth').id
        return {
            'name': 'Balance',
            'view_type': 'form',
            'view_mode': 'tree',
            'views': [(view_id, 'form')],
            'res_model': 'account.account',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.payment_account.id,
            'target': 'new',
            'context': {},
        }

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(HrEmployee, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                      submenu=submenu)
        if res.get('toolbar', False) and res.get('toolbar').get('print', False):
            reports = res.get('toolbar').get('print')
            for report in reports:
                if report.get('string') == 'Attendance Error Report':
                    # if report.get('report_file', False) and report.get('report_file') == 'hr_attendance.report_attendanceerrors':
                    res['toolbar']['print'].remove(report)
        return res


    
        
            

    address_boolean = fields.Boolean(string="Same as present address")

    monthly_status_ids = fields.One2many('month.leave.status', 'status_id', 'Status')

    attendance_ids = fields.One2many('hiworth.hr.attendance', 'name')
    # branch = fields.Many2one('branch.project',string='Branch Name',required=True)
    emp_code = fields.Char('Order Reference', required=False, copy=False, readonly=True, )
    emp_code_old = fields.Char('Employee Old Ref')
    street = fields.Char('Street')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state')
    zip = fields.Char('Zip')
    street2 = fields.Char()
    street1 = fields.Char('Street')
    city1 = fields.Char('City')
    state_id1 = fields.Many2one('res.country.state')
    zip1 = fields.Char('Zip')
    street3 = fields.Char()
    country_id1 = fields.Many2one('res.country')
    type_of_card = fields.Selection(
        [('passport', 'Passport'), ('aadharcard', 'Aadhar Card'), ('voterid', 'VoterId'), ('pancard', 'PanCard'),
         ('license', 'License')], string="Type Of Card")
    present = fields.Boolean(default=False)
    location = fields.Many2one('stock.location', 'Location')
    # monthly_leave = fields.Float('Monthly Leave Taken')
    father = fields.Char('Name Of Father')
    mother = fields.Char('Name Of Mother')
    hus_wife = fields.Char('Name Of Husband/Wife')
    emergency_person = fields.Char('Emergency Contact Person')
    emergency_no = fields.Char('Emergency Contact No.')
    height = fields.Char('Height(cm)')
    weight = fields.Char('Weight')
    adhar_no = fields.Char('Adhar No.')
    pan = fields.Char('PAN')
    passport = fields.Char('Passport No.')
    licence = fields.Char('Licence No')
    vehicle_no = fields.Char('Vehicle No')

    hus_wife = fields.Char('Name Of Husband/Wife')
    joining_date = fields.Date('Date of Joining', store=True,required=True)
    employee_type = fields.Selection(
        [('trainee', 'Trainee'), ('employee', 'Employee'), ('manager', 'Manager'), ('others', 'Others')],
        'Employee Type', required=False)
    worker_type = fields.Selection([('mason', 'Mason'), ('helper', 'Helper')], 'Worker Type')
    edu_qualify = fields.One2many('edu.qualify', 'edu_id')
    wedding_anniversary = fields.Date('Wedding Anniversary')
    petty_cash_account = fields.Many2one('account.account', 'Petty Cash Account')
    payment_account = fields.Many2one('account.account', 'Payment Account')
    # user_category = fields.Many2one('employee.position',string='Position', required=True)

    user_category = fields.Selection([('admin', 'MD'),
                                      ('gm', 'GM'),
                                      ('partner', 'Partner'),
                                      ('associate', 'Associate'),
                                      ('project_cordinator_seni', 'Senior Project Manager'),
                                      ('project_manager', 'Project Manager'),
                                      ('project_cordinator_assist', 'Assistant Project Manager'),
                                      ('construction_manger', 'Construction Manager'),
                                      ('site_eng', 'Site Engineer'),
                                      ('project_eng', 'Project Engineer'),
                                      ('junior_site_eng', 'Junior Site Engineer'),
                                      ('junior_project_eng', 'Junior Project Engineer'),
                                      ('senior_supervisor', 'Senior Supervisor'),
                                      ('supervisor', 'Supervisor'),
                                      ('senior_foreman', 'Senior Foreman'),
                                      ('foreman', 'Foreman'),
                                      ('charge_hand', 'Charge Hand'),
                                      ('technician', 'Technician'),
                                      ('helper', 'Helper'),
                                      ('operation_manager', 'Operation Manager'),
                                      ('operation_officer', 'Operation Officer'),
                                      ('logis_operator', 'Logistic Operator'),
                                      ('logis_coordinator', 'Logistic Coordinator'),
                                      ('camp_boss', 'Camp Boss'),
                                      ('store_manager', 'Store Manager'),
                                      ('store_keeper', 'Store Keeper'),
                                      ('store_officer', 'Store Officer'),
                                      ('driver', 'Driver'),
                                      ('watchman', 'Watchman'),
                                      ('security', 'Security'),
                                      ('messenger', 'Messenger'),
                                      ('procure_manager', 'Procurement Manager'),
                                      ('procure_eng', 'Procurement Engineer'),
                                      ('procure_officer', 'Procurement Officer'),
                                      ('comme_contracts', 'Commercial Contracts'),
                                      ('comme_cost_cntrl', 'Commercial Cost Control'),
                                      ('business_developer', 'Business Developer'),
                                      ('sales_engineer', 'Sales Engineer'),
                                      ('estimation_engineer', 'Estimation Engineer'),
                                      ('quantity_surveyor', 'Quantity Surveyor'),
                                      ('hr', 'HR Manager'),
                                      ('hr_executive', 'HR Executive'),
                                      ('qa_qc_manager', 'QA/QC Manager'),
                                      ('qa_qc_officer', 'QA/QC Officer'),
                                      ('planning_eng', 'Planning Engineer'),
                                      ('admin receptionist', 'Admin Receptionist'),
                                      ('admin officer', 'Admin Officer'),
                                      ('others', 'Others'),
                                      # ('cheif_acc', 'Cheif Accountant'),
                                      ('sen_acc', 'Senior Accountant'),
                                      ('jun_acc', 'Accountant'),
                                      # ('cashier', 'Cashier'),
                                      #
                                      # ('technical_team', 'Technical Team'),
                                      # ('telecome_bill', 'Telecome Billing'),
                                      # ('survey_team', 'Survey Team'),
                                      # ('quality', 'Quality'),
                                      # ('tendor', 'Tendor'),
                                      # ('interlocks', 'Interlocks'),
                                      # ('liaisoning', 'Liaisoning'),
                                      #
                                      # ('district_manager', 'District Manager'),
                                      # ('site_eng', 'Captain/Site Engineer'),
                                      #
                                      # ('super_telecome', 'Supervisor(Telecome)'),
                                      # ('super_trainee', 'Supervisor(Trainee)'),
                                      # ('operators', 'Operators'),
                                      # ('helpers', 'Helpers'),
                                      # ('vehicle_admin', 'Vehicle Administration'),
                                      # ('purchase', 'Purchase'),
                                      # ('civil_store', 'Civil Store'),
                                      # ('telecome_store', 'Telecome Store'),
                                      # ('security', 'Security'),
                                      # ('labour', 'Labour'),
                                      # ('civil_workshop', 'Civil Workshop'),
                                      # ('vehicle_workshop', 'Vehicle Workshop'),
                                      # ('fuels', 'Fuels')
                                      ], string='Position', required=True)

    attendance_category = fields.Selection([('office_staff', 'Office Employee'),
                                            ('project_eng', 'Project Team'),
                                            ('site_employee', 'Site Employee'),
                                            ], string='Attendance Category')

    old_emp = fields.Boolean('Old Employee ?')
    payroll_required = fields.Boolean('Generate Payroll ?',default=True)
    company_contractor_id = fields.Many2one('res.partner', domain="[('company_contractor','=',True)]",
                                            string="Company")
    sign = fields.Binary('Sign')
    per_day_eicher_rate = fields.Float('Per Day Rate')
    labour_accnt = fields.Many2one('account.account', 'Labour Account')
    # =======
    # user_category = fields.Selection([('driver','Driver'),('supervisor','Supervisor'),('project_manager','Project Nanager'),('district_manager','District Manager')],string='User Category',required=True)
    reset_pswd = fields.Boolean(default=False)
    cost_type = fields.Selection([('permanent', 'Permanent'),
                                  ('wages', 'Daily Wage'), ('probation', 'Probationary Period')], 'Wage Type')
    leave_ids = fields.One2many('employee.leave', 'employee_id', 'Leaves')

    driver_ok = fields.Boolean('Driver Ok')
    zone_id = fields.Many2one('hr.employee.zone','Zone')

    # emp_id_no = fields.Char('ID No')
    age = fields.Char('Age', compute="_get_age")
    blood_group = fields.Char('Blood Group')
    no_mnth_job = fields.Char('No of months in job', compute="_get_working_month_year")
    year_service = fields.Char('Year of service', compute="_get_working_month_year")
    remarks = fields.Text('Remarks')
    resigning_date = fields.Date('Date of Resignation')
    status1 = fields.Selection([('active','Active'),
                                ('resign','Resigned')
                                ], default="active", string="Status")

    insurance_ids = fields.One2many('employee.insurance','employee_id', string="Employee Insurance")

    pf = fields.Boolean(string="PF")
    pf_no = fields.Char(string="PF No.")
    mediclaim = fields.Boolean(string="Mediclaim")
    esi = fields.Boolean(string="ESI")
    esi_no = fields.Char(string="ESI No.")

    tech_training = fields.One2many('technical.training','emp_id')
    canteen = fields.Boolean(string="Canteen", default=False)

    phn_no2 = fields.Char('Phone No.')
    mobile_no = fields.Char('Mobile No.')
    house_ownership = fields.Selection([('rented','Rented'),('own','Own')], string="Rented/Own")
    house_area = fields.Char('Total Area of House in Sqft')
    building_roof = fields.Selection([('concrete','Concrete'),('sheet','Sheet'),('tile','Tile')], string="Buliding Roof")
    is_truss_house = fields.Boolean(string="Truss House(Pipe & Sheet / Tile) if yes kindly tick", default=False)

    family_ids = fields.One2many('hr.employee.family','family_id')
    no_sibilings = fields.Char('No. of Brothers & Sisters')
    present_week_days = fields.Float(string="Week Days")
    casual_leave = fields.Float(string="No of Casual leaves")
    pf_required = fields.Boolean(string="PF", default=False)
    labour_category_account_id = fields.Many2one('account.account',domain="[('labour_categ','=',True)]",string="Labour Account Category")
    pt_check = fields.Boolean("Professional Tax")
    labour_welfare_fund = fields.Boolean("Labour Welfare Fund")

    emergency_con_person = fields.Char('Emergency Contact Person')
    emergency_con_person_ph = fields.Char('Emergency Contact Person Number')
    emergency_con_address = fields.Char('Emergency Contact Address')
    emergency_native_contact = fields.Char('Emergency Native place Contact Number')

    salary_account_no = fields.Char('Salary Account Number')
    p_bank_name = fields.Char('Bank')
    p_iban = fields.Char('IBAN')
    p_ifsc_code = fields.Char('IFSC')
    wps = fields.Char('WPS Salary Account')
    bank_exch = fields.Char('Bank/Exchange')
    card_no = fields.Char('Account/Card Number')

    salary_account_no2 = fields.Char('Alternative Account Number')
    p_bank_name2 = fields.Char('Bank')
    p_iban2 = fields.Char('IBAN')
    p_ifsc_code2 = fields.Char('IFSC')
    wps2 = fields.Char('WPS Salary Account')
    bank_exch2 = fields.Char('Bank/Exchange')
    card_no2 = fields.Char('Account/Card Number')


    @api.onchange('address_boolean')
    def _onchange_address_boolean(self):
        if self.address_boolean:
            self.country_id1 = self.country_id or self.state_id.country_id
            self.zip1 = self.zip
            self.state_id1 = self.state_id
            self.city1 = self.city
            self.street3 = self.street2
            self.street1 = self.street
        else:
            self.country_id1 = ""
            self.zip1 = ""
            self.state_id1 = ""
            self.city1 = ""
            self.street3 = ""
            self.street1 = ""

    @api.multi
    def view_action_resign(self):
        res = {
            'name': 'Resignation',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.employee.resignation',
            # 'domain': [('line_id', '=', self.id),('date','=',self.date)],
            # 'res_id': res_id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': {'default_resign_id': self.id},

        }

        return res

    @api.multi
    def view_action_appraisal(self):
        active_contract = self.env['hr.contract'].search([('employee_id','=', self.id),('state','=','active')], limit=1)
        if active_contract:
            print 'active_contract------------------------------------', active_contract.date_end
            if not active_contract.date_end:
                raise exceptions.ValidationError('Please enter end date of existing active contract of this employee.')
            active_contract.action_deactive()

            line_ids = []
            if active_contract.struct_id:
                for rule in active_contract.struct_id.rule_ids:
                    if rule.related_type == 'canteen':
                        values = {
                            'rule_id': rule.id,
                            'name': rule.name,
                            'is_related': True,
                            'per_day_amount': self.env['general.hr.configuration'].search([],limit=1).canteen_amount,
                        }
                    else:
                        values = {
                            'rule_id': rule.id,
                            'name': rule.name,
                        }
                    line_ids.append((0, False, values))
            # res_id = active_contract.copy()
            res_id = self.env['hr.contract'].create({'name': active_contract.name,
                                                     'employee_id': active_contract.employee_id.id,
                                                     'job_id': active_contract.job_id.id,
                                                     'type_id': active_contract.type_id.id,
                                                     'struct_id': active_contract.struct_id.id,
                                                     'wage': active_contract.wage,
                                                     'rule_lines': line_ids,
                                                     })
            print 'res_id------------------------------------', res_id
            res = {
                'name': 'Appraisal',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.contract',
                # 'domain': [('line_id', '=', self.id),('date','=',self.date)],
                'res_id': res_id.id,
                'target': 'new',
                'type': 'ir.actions.act_window',
                # 'context': {'default_resign_id': self.id},

            }

        else:
            raise exceptions.ValidationError('There is no active contract for this employee.')


        return res


    @api.multi

    def _get_age(self):
        for record in self:
            if record.birthday:
                d1 = datetime.strptime(record.birthday, "%Y-%m-%d")
                date_today = fields.Date.today()
                d2 = datetime.strptime(date_today, "%Y-%m-%d")
                # r = relativedelta(d2, d1)
                # print 'r.months----------------', r,r.months,r.year
                # record.no_mnth_job = r.months + (12*(int(d2.year)-int(d1.year)))
                record.age = (int(d2.year)-int(d1.year))

    @api.depends('joining_date')
    def _get_working_month_year(self):
        for record in self:
            if record.joining_date:
                d1 = datetime.strptime(record.joining_date, "%Y-%m-%d")
                d2 = datetime.strptime(fields.Date.today(), "%Y-%m-%d")
                time = relativedelta(d2, d1)
                record.no_mnth_job = str((time.years*12)+time.months)
                record.year_service = str(time.years)+"."+str(time.months)


    @api.onchange('user_category')
    def onchange_user_category(self):
        if self.user_category:
            if self.user_category == 'driver':
                self.driver_ok = True
            else:
                self.driver_ok = False

    @api.onchange('job_id')
    def onchange_job_id(self):
        if self.job_id.name == 'Manager.':
            print "manager=================",self.job_id.name
            self.employee_type = 'manager'
        elif self.job_id.name == 'Employee.':
            self.employee_type = 'employee'
        elif self.job_id.name == 'Trainee.':
            self.employee_type = 'trainee'
        else:
            self.employee_type = 'others'



    @api.multi
    def unlink(self):
        for rec in self:
            rec.active = False
            # hr_employee_line = self.env['hr.attendance'].search([('employee_id', '=', rec.id)])
            # if hr_employee_line:
            #     hr_employee_line._cr.execute("DELETE FROM hr_attendance WHERE employee_id=%s", (rec.id,))
            # hr_contract_line = self.env['hr.contract'].search([('employee_id', '=', rec.id)])
            # if hr_contract_line:
            #     hr_contract_line._cr.execute("DELETE FROM hr_contract WHERE employee_id=%s", (rec.id,))
            # #     # stock_move_record.unlink()
            # # stock_quant_record = self.env['stock.quant'].search([('product_id', '=', rec.id)])
            # # if stock_quant_record:
            # #     stock_quant_record._cr.execute("DELETE FROM stock_quant WHERE product_id=%s", (rec.id,))
            # models.Model.unlink(rec) 
        return

    @api.multi
    def get_employee_code(self, o):
        return self.env['hr.employee'].search([('id','=',o.id)]).emp_code

    @api.multi 
    def get_location_ml(self,o,day):
        rec = self.env['hiworth.hr.attendance'].search([('name','=',o.id)])
        for r in rec:
            if dateutil.parser.parse(r.sign_in).date() == day[0]:
                return r.location.name



    @api.model
    def create(self, vals):
        group_id_admin = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_admin').id
        group_id_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_driver').id
        group_id_supervisor = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_supervisor').id
        group_id_project_manager = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_project_manager').id
        group_id_district_manager = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_district_manager').id
        group_eicher_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_eicher_driver').id
        group_pickup_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_pickup_driver').id
        group_lmv_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_lmv_driver').id
        group_directors = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_directors').id
        group_office_manger = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_office_manger').id
        group_project_eng = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_project_eng').id
        group_cheif_acc = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_cheif_acc').id
        group_sen_acc = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_sen_acc').id
        group_jun_acc = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_jun_acc').id
        group_cashier = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_cashier').id
        group_project_cordinator = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_project_cordinator').id
        group_technical_team = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_technical_team').id
        group_telecome_bill = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_telecome_bill').id
        group_survey_team = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_survey_team').id
        group_quality = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_quality').id
        group_tendor = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_tendor').id
        group_interlocks = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_interlocks').id
        group_liaisoning = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_liaisoning').id
        group_hr = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_hr').id
        group_site_eng = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_site_eng').id
        group_super_telecome = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_super_telecome').id
        group_super_trainee = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_super_trainee').id
        group_operators = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_operators').id
        group_helpers = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_helpers').id
        group_vehicle_admin = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_vehicle_admin').id
        group_purchase = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_purchase').id
        group_civil_store = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_civil_store').id
        group_telecome_store = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_telecome_store').id
        group_security = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_security').id
        group_labour = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_labour').id
        group_civil_workshop = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_civil_workshop').id
        group_vehicle_workshop = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_vehicle_workshop').id
        group_fuels = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_fuels').id
        
        result = super(HrEmployee, self).create(vals)
        if result.emp_code == False:
            result.emp_code = self.env['ir.sequence'].next_by_code('hr.employee') or '/'
        if result.work_email:
            v = {
             'active': True,
             'name': result.name,
             'login': result.work_email,
             'company_id': 1,
             'employee_id':result.id,
             'groups_id': [(6, 0, [group_id_driver])] if result.user_category == 'driver' 
                            else [(6, 0, [group_id_admin])] if result.user_category == 'admin'
                            else [(6, 0, [group_id_supervisor])] if result.user_category == 'supervisor' 
                            else [(6, 0, [group_id_project_manager])] if result.user_category == 'project_manager'
                            else [(6, 0, [group_id_district_manager])] if result.user_category == 'district_manager'
                            else [(6, 0, [group_eicher_driver])] if result.user_category == 'eicher_driver'
                            else [(6, 0, [group_pickup_driver])] if result.user_category == 'pickup_driver'
                            else [(6, 0, [group_lmv_driver])] if result.user_category == 'lmv_driver'
                            else [(6, 0, [group_directors])] if result.user_category == 'directors'
                            else [(6, 0, [group_office_manger])] if result.user_category == 'office_manger'
                            else [(6, 0, [group_project_eng])] if result.user_category == 'project_eng'
                            else [(6, 0, [group_cheif_acc])] if result.user_category == 'cheif_acc'
                            else [(6, 0, [group_sen_acc])] if result.user_category == 'sen_acc'
                            else [(6, 0, [group_jun_acc])] if result.user_category == 'jun_acc'
                            else [(6, 0, [group_cashier])] if result.user_category == 'cashier'
                            else [(6, 0, [group_project_cordinator])] if result.user_category == 'project_cordinator'
                            else [(6, 0, [group_technical_team])] if result.user_category == 'technical_team'
                            else [(6, 0, [group_telecome_bill])] if result.user_category == 'telecome_bill'
                            else [(6, 0, [group_survey_team])] if result.user_category == 'survey_team'
                            else [(6, 0, [group_quality])] if result.user_category == 'quality'
                            else [(6, 0, [group_tendor])] if result.user_category == 'tendor'
                            else [(6, 0, [group_interlocks])] if result.user_category == 'interlocks'
                            else [(6, 0, [group_liaisoning])] if result.user_category == 'liaisoning'
                            else [(6, 0, [group_hr])] if result.user_category == 'hr'
                            else [(6, 0, [group_site_eng])] if result.user_category == 'site_eng'
                            else [(6, 0, [group_super_telecome])] if result.user_category == 'super_telecome'
                            else [(6, 0, [group_super_trainee])] if result.user_category == 'super_trainee'
                            else [(6, 0, [group_operators])] if result.user_category == 'operators'
                            else [(6, 0, [group_helpers])] if result.user_category == 'helpers'
                            else [(6, 0, [group_vehicle_admin])] if result.user_category == 'vehicle_admin'
                            else [(6, 0, [group_purchase])] if result.user_category == 'purchase'
                            else [(6, 0, [group_civil_store])] if result.user_category == 'civil_store'
                            else [(6, 0, [group_telecome_store])] if result.user_category == 'telecome_store'
                            else [(6, 0, [group_security])] if result.user_category == 'security'
                            else [(6, 0, [group_labour])] if result.user_category == 'labour'
                            else [(6, 0, [group_civil_workshop])] if result.user_category == 'civil_workshop'
                            else [(6, 0, [group_vehicle_workshop])] if result.user_category == 'vehicle_workshop'
                            else [(6, 0, [group_fuels])] if result.user_category == 'fuels'
                            else False
            
            }
            user_id1 = self.env['res.users'].sudo().create(v)
            result.user_id = user_id1.id

        return result


    @api.multi
    def write(self, vals):
        group_id_admin = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_admin').id
        group_id_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_driver').id
        group_id_supervisor = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_supervisor').id
        group_id_project_manager = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_project_manager').id
        group_id_district_manager = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_district_manager').id
        group_eicher_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_eicher_driver').id
        group_pickup_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_pickup_driver').id
        group_lmv_driver = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_lmv_driver').id
        group_directors = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_directors').id
        group_office_manger = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_office_manger').id
        group_project_eng = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_project_eng').id
        group_cheif_acc = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_cheif_acc').id
        group_sen_acc = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_sen_acc').id
        group_jun_acc = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_jun_acc').id
        group_cashier = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_cashier').id
        group_project_cordinator = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_project_cordinator').id
        group_technical_team = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_technical_team').id
        group_telecome_bill = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_telecome_bill').id
        group_survey_team = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_survey_team').id
        group_quality = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_quality').id
        group_tendor = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_tendor').id
        group_interlocks = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_interlocks').id
        group_liaisoning = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_liaisoning').id
        group_hr = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_hr').id
        group_site_eng = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_site_eng').id
        group_super_telecome = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_super_telecome').id
        group_super_trainee = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_super_trainee').id
        group_operators = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_operators').id
        group_helpers = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_helpers').id
        group_vehicle_admin = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_vehicle_admin').id
        group_purchase = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_purchase').id
        group_civil_store = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_civil_store').id
        group_telecome_store = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_telecome_store').id
        group_security = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_security').id
        group_labour = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_labour').id
        group_civil_workshop = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_civil_workshop').id
        group_vehicle_workshop = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_vehicle_workshop').id
        group_fuels = self.env['ir.model.data'].get_object('hiworth_hr_attendance',  'group_fuels').id
        result = super(HrEmployee, self).write(vals)
        if vals.get('user_category') or vals.get('name'):
            rec = self.env['res.users'].sudo().search([('employee_id','=',self.id)])
            if vals.get('name'):
                rec.write({'name':vals.get('name')})
            if rec:
                rec.write({'groups_id':[(6, 0, [group_id_driver])] if vals.get('user_category') == 'driver' 
                        else [(6, 0, [group_id_supervisor])] if vals.get('user_category') == 'supervisor' 
                        else [(6, 0, [group_id_admin])] if vals.get('user_category') == 'admin'
                        else [(6, 0, [group_id_project_manager])] if vals.get('user_category') == 'project_manager'
                        else [(6, 0, [group_id_district_manager])] if vals.get('user_category') == 'district_manager'
                        else [(6, 0, [group_eicher_driver])] if vals.get('user_category') == 'eicher_driver'
                        else [(6, 0, [group_pickup_driver])] if vals.get('user_category') == 'pickup_driver'
                        else [(6, 0, [group_lmv_driver])] if vals.get('user_category') == 'lmv_driver'
                        else [(6, 0, [group_directors])] if vals.get('user_category') == 'directors'
                        else [(6, 0, [group_office_manger])] if vals.get('user_category') == 'office_manger'
                        else [(6, 0, [group_project_eng])] if vals.get('user_category') == 'project_eng'
                        else [(6, 0, [group_cheif_acc])] if vals.get('user_category') == 'cheif_acc'
                        else [(6, 0, [group_sen_acc])] if vals.get('user_category') == 'sen_acc'
                        else [(6, 0, [group_jun_acc])] if vals.get('user_category') == 'jun_acc'
                        else [(6, 0, [group_cashier])] if vals.get('user_category') == 'cashier'
                        else [(6, 0, [group_project_cordinator])] if vals.get('user_category') == 'project_cordinator'
                        else [(6, 0, [group_technical_team])] if vals.get('user_category') == 'technical_team'
                        else [(6, 0, [group_telecome_bill])] if vals.get('user_category') == 'telecome_bill'
                        else [(6, 0, [group_survey_team])] if vals.get('user_category') == 'survey_team'
                        else [(6, 0, [group_quality])] if vals.get('user_category') == 'quality'
                        else [(6, 0, [group_tendor])] if vals.get('user_category') == 'tendor'
                        else [(6, 0, [group_interlocks])] if vals.get('user_category') == 'interlocks'
                        else [(6, 0, [group_liaisoning])] if vals.get('user_category') == 'liaisoning'
                        else [(6, 0, [group_hr])] if vals.get('user_category') == 'hr'
                        else [(6, 0, [group_site_eng])] if vals.get('user_category') == 'site_eng'
                        else [(6, 0, [group_super_telecome])] if vals.get('user_category') == 'super_telecome'
                        else [(6, 0, [group_super_trainee])] if vals.get('user_category') == 'super_trainee'
                        else [(6, 0, [group_operators])] if vals.get('user_category') == 'operators'
                        else [(6, 0, [group_helpers])] if vals.get('user_category') == 'helpers'
                        else [(6, 0, [group_vehicle_admin])] if vals.get('user_category') == 'vehicle_admin'
                        else [(6, 0, [group_purchase])] if vals.get('user_category') == 'purchase'
                        else [(6, 0, [group_civil_store])] if vals.get('user_category') == 'civil_store'
                        else [(6, 0, [group_telecome_store])] if vals.get('user_category') == 'telecome_store'
                        else [(6, 0, [group_security])] if vals.get('user_category') == 'security'
                        else [(6, 0, [group_labour])] if vals.get('user_category') == 'labour'
                        else [(6, 0, [group_civil_workshop])] if vals.get('user_category') == 'civil_workshop'
                        else [(6, 0, [group_vehicle_workshop])] if vals.get('user_category') == 'vehicle_workshop'
                        else [(6, 0, [group_fuels])] if vals.get('user_category') == 'fuels'
                        else False,
                        })
        return result

    @api.multi
    def change_password(self):
        for rec in self:
            return {
                    'name': rec.name,
                    'view_mode': 'form,tree',
                    'res_model': 'hr.password.reset',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    # "views": [[self.env.ref("hiworth_hr_attendance.hiworth_hr_attendance_view_employee_attendance_tree").id, "tree"], [False, "form"]],
                    # 'domain': [('name','=',self[0].id)],
                    "context": {'default_employee_id': rec.id,'default_user_id': rec.user_id.id,}
                }
            print 'asdadad===================', rec.user_id
        # user_id = self.env['res.user'].search([('employee_id','=','')])
        user_id = rec.user_id
        user_id.write({'password': "admin3"})
        # self.env.cr.execute('UPDATE res_users SET password=%s WHERE id=%s', ('admin2', user_id,))



    @api.multi
    def load_employee_attendance(self):
        # for employee in self:
        #     recs = self.env['hiworth.hr.attendance'].search([('name','=',employee.id)])
        #     last_rec = recs and max(recs)
        return {
                    'name': self[0].name,
                    'view_mode': 'calendar,form,tree',
                    'res_model': 'hiworth.hr.attendance',
                    'type': 'ir.actions.act_window',
                    "views": [[self.env.ref("hiworth_hr_attendance.hiworth_hr_attendance_view_employee_attendance_tree").id, "tree"], [False, "form"]],
                    'domain': [('name','=',self[0].id)],
                    "context": {'default_name': self[0].id}
                }

    @api.multi
    def employee_attendance_regulise(self,start_date,end_date,emp):
        attendance_obj = self.env['hiworth.hr.attendance']
        absent_attendance_days = attendance_obj.search([('name', '=', emp.id),
                                                        ('date', '>=', start_date),
                                                        ('date', '<=', end_date),
                                                        ('attendance', '=', 'absent')])

        half_attendance_days = attendance_obj.search([('name', '=', emp.id),
                                                      ('date', '>=', start_date),
                                                      ('date', '<=', end_date),
                                                      ('attendance', '=', 'half')])

        exgratia = self.env['exgratia.payment']

        exgratia_days_full = exgratia.search([('date', '>=', start_date),
                                              ('date', '<=', end_date),
                                              ('employee_id', '=', emp.id),
                                              ('state', '=', 'approved'), ('attendance', '=', 'full')], )

        exgratia_days_half = exgratia.search([('date', '>=', start_date),
                                              ('date', '<=', end_date),
                                              ('employee_id', '=', emp.id),
                                              ('state', '=', 'approved'), ('attendance', '=', 'half')], )

        sunday_holiday_att = (len(exgratia_days_full) + (len(exgratia_days_half) * 0.5))

        active_contract = self.env['hr.contract'].search(
            [('employee_id', '=', emp.id), ('state', '=', 'active')])

        employee_leave_id = active_contract.employee_leave_ids.search(
            [('id', 'in', active_contract.employee_leave_ids.ids), ], limit=1, order='id desc')
        remaining = employee_leave_id.remaining
        sun_hol_att = sunday_holiday_att
        if sunday_holiday_att or len(half_attendance_days.ids) or len(absent_attendance_days.ids):
            for absent_attendance in absent_attendance_days:
                if sun_hol_att >= 1:
                    absent_attendance.attendance = 'full'
                    absent_attendance.compensatory_off = True
                    sun_hol_att = sun_hol_att - 1

                elif sun_hol_att == 0.5:
                    absent_attendance.attendance = 'half'
                    absent_attendance.half_compensatory_off = True
                    sun_hol_att = sun_hol_att - 0.5
                if not sun_hol_att:
                    if remaining >= 1:
                        absent_attendance.attendance = 'full'
                        absent_attendance.compensatory_off = True
                        employee_leave_id.availed += 1
                        remaining = remaining - 1

                    elif remaining == 0.5:
                        absent_attendance.attendance = 'half'
                        absent_attendance.half_compensatory_off = True
                        employee_leave_id.availed += 0.5
                        remaining = remaining - 0.5

            for half_attendance in half_attendance_days:
                if sun_hol_att:
                    half_attendance.attendance = 'full'
                    half_attendance.compensatory_off = True
                    sun_hol_att = sun_hol_att - 0.5
                else:
                    if remaining:
                        half_attendance.attendance = 'full'
                        half_attendance.compensatory_off = True
                        employee_leave_id.availed += 0.5
                        remaining = remaining - 0.5

        return sunday_holiday_att,sun_hol_att


class HrEmployeeFamily(models.Model):
    _name = 'hr.employee.family'

    family_id = fields.Many2one('hr.employee')
    relation = fields.Char('Relation')
    name = fields.Char('Name')
    age = fields.Char('Age')
    dob = fields.Date('DOB')
    occupation_institution = fields.Char('Occupation Institution')
    studying_institution = fields.Char('Studying Institution')


class HrPasswordReset(models.Model):
    _name = 'hr.password.reset'

    employee_id = fields.Many2one('hr.employee')
    user_id = fields.Many2one('res.users')
    new_password = fields.Char('New Password')

    @api.multi
    def change_password(self):
        for rec in self:
            rec.employee_id.reset_pswd = True
            user_id = rec.user_id
            user_id.write({'password': rec.new_password})    


class EduQualify(models.Model):
    _name = 'edu.qualify'

    edu_id = fields.Many2one('hr.employee')
    qualification = fields.Char('Qualification')
    year = fields.Char('Year Of Passing')
    unvrsty = fields.Char('University/College')



class LossPay(models.Model):
    _name = 'loss.pay'

    name = fields.Float(string="Loss Of Pay/Not")
    rec = fields.Many2one('hr.holidays')

    @api.multi
    def confirm_edit(self):
        self.rec.holidays_validate()
        self.rec.lop_emp = self.name


class SalaryDeduction(models.Model):
    _name = 'salary.deductions'

    name = fields.Char()
    amount = fields.Float()
    payslip_id = fields.Many2one('hr.payslip')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    #
    # def onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False,
    #                          context=None):
    #     res = super(HrPayslip, self).onchange_employee_id(self, cr, uid, ids, date_from, date_to, employee_id=False, contract_id=False,
    #                          context=None)
    #     for rec in self:
    #         rec.pf_required = rec.employee_id.pf_required
    #
    #     return res

    def get_contract(self, cr, uid, employee, date_from, date_to, context=None):
        pass
        """
        @param employee: browse record of employee
        @param date_from: date field
        @param date_to: date field
        @return: returns the ids of all the contracts for the given employee that need to be considered for the given dates
        """
        contract_obj = self.pool.get('hr.contract')
        clause = []
        clause_final =  ['&',('employee_id', '=', employee.id),('state', '=', 'active')]
        contract_ids = contract_obj.search(cr, uid, clause_final, context=context)
        return contract_ids




        # hr_salary_rule = payslip.contract_id.rule_lines
        # contract_ids = [payslip.contract_id.id]
        # lines = [(0, 0, line) for line in
        #          self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]

    # @api.onchange('month')
    # def onchange_month(self):
    #     if self.month:
    #         date = '1 '+self.month+' '+str(datetime.now().year)
    #         date_object = datetime.strptime(date, '%d %B %Y')
    #         print 'date_object---------------------------------------',date, date_object, date_object + relativedelta(day=31)
    #         self.date_from = date_object
    #         end_date = date_object + relativedelta(day=31)
    #         self.date_to = end_date

    # @api.depends('attendance')
    # def compute_attendance(self):
    #     for rec in self:
    #         # attendance = self.env['hiworth.hr.attendance'].search([('date','>=',self.date_from),('date','<=',self.date_to),('attendance','=','full'),('name','=',self.employee_id.id)])
    #         # rec.attendance = len(attendance.ids)
    #         date_to = datetime.strptime(rec.date_to,"%Y-%m-%d")
    #         date_from = datetime.strptime(rec.date_from,"%Y-%m-%d")
    #         rec.wages_due = (rec.contract_id.wage * rec.attendance)/(((date_to - date_from).days )+1)
    #         working_days = (date_to - date_from).days
    #         if rec.attendance < working_days:
    #             if rec.employee_id.casual_leave > 0.0:
    #                 if (working_days - rec.attendance) > rec.employee_id.casual_leave:
    #                     rec.employee_id.casual_leave = rec.employee_id.casual_leave - +1
    #                 rec.attendance = rec.attendance + 1
    #         else:
    #             rec.employee_id.casual_leave = rec.employee_id.casual_leave + 1

    @api.depends('contract_id')
    def compute_basic_salary(self):
        for rec in self:
            rec.basic_salary = rec.contract_id.wage
    @api.onchange('contract_id')
    def onchange_contract_id(self):
        for rec in self:
            if rec.contract_id.struct_id:
                rec.struct_id=rec.contract_id.struct_id
                line_ids = []
                # rec.hr_salary_rule = rec.contract_id.struct_id.rule_ids
                rec.contract_salary_rule_ids = False
                if rec.contract_id:
                    for rule in rec.contract_id.rule_lines:
                        values = {
                            'rule_id': rule.rule_id.id,
                            'amount':rule.amount,
                        }
                        line_ids.append((0, 0, values))
                    rec.contract_salary_rule_ids = line_ids

    # @api.onchange('month')
    # def onchange_month(self):
    #     for rec in self:
    #         if rec.month:
    #             today_date_month = datetime.today().month
    #             if rec.month == 'February':
    #                 date = "1"
    #             elif rec.month in ['December','October','August','July','May','March','January']:
    #
    #             else:

    date = fields.Date(default=fields.Date.today())
    salary_deductions = fields.One2many('salary.deductions','payslip_id')
    contract_salary_rule_ids = fields.One2many('contract.salary.rule', 'hr_payslip_id')
    lop = fields.Float('LOP Days')
    lop_amount = fields.Float('LOP Amount')
    advance = fields.Float('Advance', compute="_compute_advance_amount")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('verify', 'Generated'),
            ('done', 'Confirmed'),
            ('paid', 'Paid'),
            ('cancel', 'Rejected'),
        ], 'Status', select=True, readonly=True, copy=False)
    month = fields.Selection([('January','January'),
                                ('February','February'),
                                ('March','March'),
                                ('April','April'),
                                ('May','May'),
                                ('June','June'),
                                ('July','July'),
                                ('August','August'),
                                ('September','September'),
                                ('October','October'),
                                ('November','November'),
                                ('December','December')], 'Month')
    line_ids = fields.One2many('hr.payslip.line', 'slip_id', 'Payslip Lines', readonly=True, states={'draft':[('readonly', False)], 'verify':[('readonly',False)]})
    # contract_id = fields.Many2one('hr.contract', 'Contract', required=False, readonly=True, states={'draft': [('readonly', False)]})
    staff_donation = fields.Float(string="Staff Donation")
    mobile_over = fields.Float(string="Mobile Over")
    society_kit = fields.Float(string="Society Kit")
    canteen_food = fields.Float(string="Canteen Food")
    lic_amount = fields.Float(string="LIC Amount")
    mediclaim_amount = fields.Float(string="MediClaim Amount")
    loan_refund = fields.Float(string="Loan Refund")
    fine = fields.Float(string="Fine")
    chitty = fields.Float(string="Chitty")
    sealed_amount = fields.Float(string="Sealed PF Amount")
    sealed_esi_amount = fields.Float(string="Sealed ESI Amount")
    attendance = fields.Float(string="Attndance")
    wages_due = fields.Float(string="wages Due")
    pf_required = fields.Boolean(string="PF Required Or Not", default=False)
    amount_advance = fields.Float(string="Advance")
    ###############TRIANGLE#####################
    basic_salary = fields.Float(string="CTC",compute="compute_basic_salary",store=True)
    other_allowance = fields.Float(string="Other Allowance")
    house_rent_allowance = fields.Float(string="House Rent Allowance")
    per_day_salary = fields.Float(string="Per Day Salary")
    overtime_amount = fields.Float(string="Overtime Amount")
    on_public_holidays = fields.Float(string="On Public Holidays")
    per_hr_salary = fields.Float(string="Per Hour Salary")
    no_hr_overtime = fields.Float(string="No of Overtime Hours")
    vehicle_allowance = fields.Float(string="Vehicle Allowance")
    petrol_allowance = fields.Float(string="Petrol Allowance")
    travel_allowance = fields.Float(string="Travel Allowance")
    da = fields.Float(string="DA")
    overtime = fields.Float(string="Overtime Allowance")
    total_deduction = fields.Float(string="Total deduction")
    total = fields.Float(string="Total")
    gratuity = fields.Float(string="Gratuity")
    gross_salary = fields.Float(string="Gross Salary")
    net_salary = fields.Float(string="Net Salary")
    over_time_hours = fields.Float(string="Over time hours")
    hr_salary_rule = fields.Many2one('hr.salary.rule')
    employee_payslip_batches_id = fields.Many2one('hr.payslip.batches')

    def compute_sheet(self, cr, uid, ids, context=None):
        # res = super(HrPayslip, self).compute_sheet()
        res = super(HrPayslip, self).compute_sheet(cr, uid, ids, context=context)
        payslip = self.browse(cr, uid, ids[0])
        # sequence_obj = self.pool.get('ir.sequence')
        # payslip.number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')

        hr_salary_advace_id = self.pool.get('hr.salary.advance').search(cr, uid,[
            ('employee_id', '=', payslip.employee_id.id),
            ('emi_start_date', '<=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
            ('state','=','active'),
            ('balance_amount', '>', 0)], context=context)
        if hr_salary_advace_id:
            hr_salary_advace = self.pool.get('hr.salary.advance').browse(cr, uid, hr_salary_advace_id, context=context)
            payslip.salary_deductions.create({'name':'Salary Advance EMI ',
                                           'amount':hr_salary_advace.emi_amount,
                                           'payslip_id':payslip.id})

            hr_salary_advace.emi_lines.create({'date':payslip.date,
                                           'payment':hr_salary_advace.emi_amount,
                                           'salary_slip':payslip.id,
                                           'salary_advance_id':hr_salary_advace.id})

        start_date = datetime.strptime(payslip.date_from, "%Y-%m-%d")
        end_date = datetime.strptime(payslip.date_to, "%Y-%m-%d")
        sunday_holiday_att,sun_hol_att = payslip.employee_id.employee_attendance_regulise(start_date, end_date, payslip.employee_id)
        exgratia = self.pool.get('exgratia.payment')
        # # exgratia_days = exgratia.search(cr, uid,
        #
        # exgratia_days_full = exgratia.search(cr, uid,[('date', '>=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
        #                                  ('date', '<=', datetime.strptime(payslip.date_to, "%Y-%m-%d")),
        #                                  ('employee_id', '=', payslip.employee_id.id),
        #                                  ('state', '!=', 'cancel'),('attendance','=','full')], context=context)
        #
        # exgratia_days_half = exgratia.search(cr, uid,[('date', '>=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
        #                                  ('date', '<=', datetime.strptime(payslip.date_to, "%Y-%m-%d")),
        #                                  ('employee_id', '=', payslip.employee_id.id),
        #                                  ('state', '!=', 'cancel'),('attendance','=','half')], context=context)

        over_time = exgratia.search(cr, uid,[('date', '>=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
                                         ('date', '<=', datetime.strptime(payslip.date_to, "%Y-%m-%d")),
                                         ('employee_id', '=', payslip.employee_id.id),
                                         ('state', '=', 'approved'),('attendance', 'not in',['full', 'half'])], context=context)

        attendance = self.pool.get('hiworth.hr.attendance')

        full_present = attendance.search(cr, uid,[
            ('name', '=', payslip.employee_id.id),
            ('date', '>=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
            ('date','<=',datetime.strptime(payslip.date_to, "%Y-%m-%d")),
            ('attendance','=','full')], context=context)

        half = attendance.search(cr, uid,
            [('name', '=', payslip.employee_id.id),
             ('date', '>=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
             ('date','<=',datetime.strptime(payslip.date_to, "%Y-%m-%d")),
             ('attendance','=','half')], context=context)

        full_absent = attendance.search(cr, uid,
            [('name', '=', payslip.employee_id.id),
             ('date', '>=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
             ('date','<=',datetime.strptime(payslip.date_to, "%Y-%m-%d")),
             ('attendance','=','absent')], context=context)

        payslip.attendance = len(full_present)+(len(half)*0.5)
        per_day_salary = payslip.basic_salary * 12 / 365
        per_hour_salary = per_day_salary / 8
        over_time =  sum(exgratia.browse(cr,uid,over_time).mapped('hours')) *  per_hour_salary
        payslip.overtime = over_time
        lop_days = len(full_absent)+(len(half)*0.5)
        payslip.lop = lop_days
        lop_amount = lop_days * per_day_salary
        payslip.lop_amount = lop_amount

        payslip.gross_salary = sum(payslip.contract_salary_rule_ids.mapped('amount')) + over_time
        payslip.total_deduction = sum(payslip.salary_deductions.mapped('amount')) + lop_amount
        payslip.net_salary = payslip.gross_salary - payslip.total_deduction
        payslip.state = 'verify'






        # exgratia_days = exgratia.search(cr, uid,
        #                                 [('date', '>=', datetime.strptime(payslip.date_from, "%Y-%m-%d")),
        #                                  ('date', '<=', datetime.strptime(payslip.date_to, "%Y-%m-%d")),
        #                                  ('employee_id', '=', payslip.employee_id.id),
        #                                  ('state', '!=', 'cancel'), ], context=context)
        # holiday = 0
        # week_day = 0
        # public_holiday = self.pool.get('public.holiday')
        # for number in exgratia_days:
        #     day = exgratia.browse(cr, uid, number)
        #     public_holidays = public_holiday.search(cr, uid,[('date', '=', day.date)], context=context)
        #     if datetime.strptime(day.date, "%Y-%m-%d").weekday() == 6 or public_holidays:
        #         holiday += day.hours
        #     else:
        #         week_day += day.hours

        # for rec in payslip:
        #     for rule in rec.contract_id.rule_lines:
        #         if not rec.house_rent_allowance or rec.house_rent_allowance == 0.0:
        #             if rule.rule_id.code == "HRA":
        #                 if rule.rule_id.amount_select == 'fix':
        #                     if rule.amount_fix:
        #                         rec.house_rent_allowance = rule.amount_fix
        #                     else:
        #                         rec.house_rent_allowance = rule.rule_id.amount_fix
        #                 elif rule.rule_id.amount_select == 'percentage':
        #                     if rule.amount_percentage:
        #                         rec.house_rent_allowance = rec.basic_salary * (rule.amount_percentage/100)
        #                     else:
        #                         rec.house_rent_allowance = rec.basic_salary * (rule.rule_id.amount_percentage/100)
        #
        #         if not rec.travel_allowance or rec.travel_allowance == 0.0:
        #             if rule.rule_id.code == "TA":
        #                 if rule.rule_id.amount_select == 'fix':
        #                     if rule.amount_fix:
        #                         rec.travel_allowance = rule.amount_fix
        #                     else:
        #                         rec.travel_allowance = rule.rule_id.amount_fix
        #                 elif rule.rule_id.amount_select == 'percentage':
        #                     if rule.amount_percentage:
        #                         rec.travel_allowance = rec.basic_salary * (rule.amount_percentage/100)
        #                     else:
        #                         rec.travel_allowance = rec.basic_salary * (rule.rule_id.amount_percentage/100)
        #
        #         if not rec.petrol_allowance or rec.petrol_allowance == 0.0:
        #             if rule.rule_id.code == "PA":
        #                 if rule.rule_id.amount_select == 'fix':
        #                     if rule.amount_fix:
        #                         rec.petrol_allowance = rule.amount_fix
        #                     else:
        #                         rec.petrol_allowance = rule.rule_id.amount_fix
        #                 elif rule.rule_id.amount_select == 'percentage':
        #                     if rule.amount_percentage:
        #                         rec.petrol_allowance = rec.basic_salary * (rule.amount_percentage/100)
        #                     else:
        #                         rec.petrol_allowance = rec.basic_salary * (rule.rule_id.amount_percentage/100)
        #
        #         if not rec.other_allowance or rec.other_allowance == 0.0:
        #             if rule.rule_id.code == "OA":
        #                 if rule.rule_id.amount_select == 'fix':
        #                     if rule.amount_fix:
        #                         rec.other_allowance = rule.amount_fix
        #                     else:
        #                         rec.other_allowance = rule.rule_id.amount_fix
        #                 elif rule.rule_id.amount_select == 'percentage':
        #                     if rule.amount_percentage:
        #                         rec.other_allowance = rec.basic_salary * (rule.amount_percentage/100)
        #                     else:
        #                         rec.other_allowance = rec.basic_salary * (rule.rule_id.amount_percentage/100)
        #
        #         if not rec.da or rec.da == 0.0:
        #             if rule.rule_id.code == "DA":
        #                 if rule.rule_id.amount_select == 'fix':
        #                     if rule.amount_fix:
        #                         rec.da = rule.amount_fix
        #                     else:
        #                         rec.da = rule.rule_id.amount_fix
        #                 elif rule.rule_id.amount_select == 'percentage':
        #                     if rule.amount_percentage:
        #                         rec.da = rec.basic_salary * (rule.amount_percentage/100)
        #                     else:
        #                         rec.da = rec.basic_salary * (rule.rule_id.amount_percentage/100)
        #
        #         if not rec.vehicle_allowance or rec.vehicle_allowance == 0.0:
        #             if rule.rule_id.code == "VA":
        #                 if rule.rule_id.amount_select == 'fix':
        #                     if rule.amount_fix:
        #                         rec.vehicle_allowance = rule.amount_fix
        #                     else:
        #                         rec.vehicle_allowance = rule.rule_id.amount_fix
        #                 elif rule.rule_id.amount_select == 'percentage':
        #                     if rule.amount_percentage:
        #                         rec.vehicle_allowance = rec.basic_salary * (rule.amount_percentage/100)
        #                     else:
        #                         rec.vehicle_allowance = rec.basic_salary * (rule.rule_id.amount_percentage/100)
        #
        #     gross_salary = rec.basic_salary + rec.house_rent_allowance + rec.vehicle_allowance + rec.petrol_allowance \
        #                    + rec.other_allowance + rec.da + rec.travel_allowance
        #     per_day_salary = gross_salary * 12 / 365
        #     per_hour_salary = per_day_salary / 8
        #     rec.overtime = per_hour_salary * 1.25 * week_day
        #     rec.on_public_holidays = per_hour_salary * 1.50 * holiday
        #     rec.attendance = len(full)+(len(half)*0.5)
        #     lop_amount = rec.attendance * per_day_salary
        #     rec.wages_due = lop_amount
        #     rec.gross_salary = gross_salary + rec.on_public_holidays + rec.overtime
        #     total_deduction = rec.wages_due+rec.amount_advance+rec.staff_donation+rec.mobile_over+rec.loan_refund+rec.fine
        #     rec.total_deduction = total_deduction
        #     rec.net_salary = rec.gross_salary-rec.total_deduction
        #     rec.state='verify'


    # @api.depends('basic_salary')
    # def compute_allowances(self):
    #     for rec in self:
    #         gross_salary = rec.staff_donation + rec.mobile_over + rec.society_kit + rec.loan_refund + rec.fine + \
    #                        rec.amount_advance + rec.house_rent_allowance + rec.vehicle_allowance + rec.petrol_allowance\
    #                        + rec.overtime
    #         per_day_salary = gross_salary * 12 / 365
    #         per_hour_salary = per_day_salary / 8
    #         overtime_amount = rec.over_time_hours * per_hour_salary * 1.25
    #         on_public_holidays = rec.over_time_hours * per_hour_salary * 1.50

    resigned = fields.Boolean(string="Resigned")
    terminated = fields.Boolean(string="Terminated")

    STATES = [
        ('resigned', 'Resigned'),
        ('terminated', 'Terminated'),
    ]
    state_emp = fields.Selection(STATES, )

    # gratuity calculation
    @api.onchange('terminated', 'resigned', 'state_emp')
    def do_stuff(self):
        # if self.state_emp == 'terminated':
        if self.terminated == True:
            print("employee has been terminated")
            emp_obj = self.env['hr.employee'].browse(self.employee_id.id)
            con_obj = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'active')], limit=1)
            print("NAME FROM CONTRACT", con_obj.employee_id.name)
            print("ID  CONTRACT", con_obj.id)
            basic_wages = con_obj.wage
            print("basic wage is", basic_wages)
            print(emp_obj.name)
            if emp_obj:
                date_join = emp_obj.joining_date
                today = datetime.today().strftime('%Y-%m-%d')
                print("joining date is", date_join)
                print("BASIC SALARY", self.basic_salary)
                print("todays date is", today)
                worked_years = int(datetime.today().year) - int(str(date_join).split('-')[0])
                print("work exp", worked_years)
                if worked_years < 1:
                    self.gratuity = 0
                if ((worked_years >= 1) and (worked_years < 5)):
                    per_day_sal = basic_wages / 30
                    oneyear_gratuity = per_day_sal * 21

                    self.gratuity = oneyear_gratuity * worked_years
                if (worked_years >= 5):
                    print("inside 3rd loop")
                    per_day_sal = basic_wages / 30
                    print("perday", per_day_sal)
                    oneyear_gratuity = per_day_sal * 30
                    print("oneyr", oneyear_gratuity)
                    total_grat = oneyear_gratuity * worked_years
                    print("total", total_grat)
                    self.gratuity = total_grat
        # if self.state_emp == 'resigned':
        if self.resigned == True:
            emp_obj = self.env['hr.employee'].browse(self.employee_id.id)
            con_obj = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'active')], limit=1)
            print("NAME FROM CONTRACT", con_obj.employee_id.name)
            print("ID  CONTRACT", con_obj.id)
            basic_wages = con_obj.wage
            print(emp_obj.name)
            if emp_obj:
                date_join = emp_obj.joining_date
                today = datetime.today().strftime('%Y-%m-%d')
                print("joining date is", date_join)
                print("BASIC SALARY", self.basic_salary)
                print("todays date is", today)
                worked_years = int(datetime.today().year) - int(str(date_join).split('-')[0])
                print("work exp-resigned", worked_years)
                if worked_years < 1:
                    self.gratuity = 0
                    # raise except_orm(_('Warning'), _('he has served for less than one year,he is not entitled to any gratuity pay'))
                    #
                if ((worked_years >= 1) and (worked_years < 3)):
                    print("worked 1 to 2.9")
                    per_day_sal = basic_wages / 30
                    # oneyear_gratuity_1 = per_day_sal * 30
                    sal_of_21 = per_day_sal*21
                    grat = sal_of_21 * 0.333333333
                    total = grat * worked_years

                    # total_grat = oneyear_gratuity_1 * worked_years
                    # total = total_grat * 0.333333333
                    print("total", total)
                    self.gratuity = total
                if ((worked_years >= 3) and (worked_years < 5)):
                    print("worked 3 to 4.9")
                    print("greater than ........")
                    per_day_sal = basic_wages / 30
                    # oneyear_gratuity_1 = per_day_sal * 30
                    sal_of_21 = per_day_sal * 21
                    grat = sal_of_21 * 0.666666667
                    total = grat * worked_years
                    # total = total_grat * 0.666666667
                    print("total", total)
                    self.gratuity = total
                if (worked_years >= 5):
                    per_day_sal = basic_wages / 30
                    oneyear_gratuity = per_day_sal * 21
                    self.gratuity = oneyear_gratuity * worked_years
        if((self.resigned == False) and (self.terminated == False)):
            self.gratuity = 0.00
    @api.multi
    def do_cash_payment(self):
        res = {
            'name': 'Cash Payment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.payslip.cash.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',

        }
        return res

    @api.multi
    def do_bank_payment(self):
        res = {
            'name': 'Bank Payment',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'employee.payslip.bank.wizard',
            'target': 'new',
            'type': 'ir.actions.act_window',

        }
        return res

    @api.depends('employee_id')
    def _compute_advance_amount(self):
        recs = self.env['advance.pay'].search([])
        date_today = fields.Date.today()
        for rec in recs:
            if datetime.strptime(rec.date, "%Y-%m-%d").month == datetime.strptime(date_today, "%Y-%m-%d").month and datetime.strptime(rec.date, "%Y-%m-%d").year == datetime.strptime(date_today, "%Y-%m-%d").year:
                for lines in rec.advance_line:
                    if lines.employee.id == self.employee_id.id:
                        self.advance += lines.amount
            return

    @api.multi
    def do_confirm(self):
        for rec in self:
            rec.state ='done'

    @api.multi
    def do_payment(self):
        for rec in self:
            rec.state ='paid'

    # @api.depends('employee_id')
    # def _onchange_lop(self):
    #     # start_date = self.date_from
    #     # end_date = self.date_to
    #     # days_count = 0
    #     # while (start_date < end_date):
    #     #     day = dateutil.parser.parse(start_date).date().weekday()
    #     #     if day != 1:
    #     #         days_count += 1
    #     #     start_date = start_date  + datetime.timedelta(days=1)
    #     #     print 'days_count------------', days_count
    #     recs = self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('date_from','>=',self.date_from),('date_to','<=',self.date_to)])
    #     for rec in recs:
    #         self.lop += rec.lop_emp
        
           


    # @api.depends('employee_id')
    # def _compute_advance_amount(self):
    #     recs = self.env['hr.holidays'].search([('employee_id','=',self.employee_id.id),('date_from','>=',self.date_from),('date_to','<=',self.date_to)])
    #     for rec in recs:
    #         self.lop += rec.lop_emp

    # # _defaults = {
    # #     'date_from': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=-1, day=1, days=15))[:10],
    # #     'date_to': lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+0, day=1, days=14))[:10],
        
    # # }

    # @api.depends('employee_id')
    # def _onchange_lop(self):
    #     recs = self.env['advance.pay'].search([])
    #     print "recssssss===============", recs
    #     date_today = fields.Date.today()
    #     for rec in recs:
    #         if datetime.strptime(rec.date, "%Y-%m-%d").month == datetime.strptime(date_today, "%Y-%m-%d").month and datetime.strptime(rec.date, "%Y-%m-%d").year == datetime.strptime(date_today, "%Y-%m-%d").year:
    #             print "year month ok=================="
    #             for lines in rec.advance_line:
    #                 if lines.employee.id == self.employee_id.id:
    #                     self.advance += lines.amount
    #         return
    #         # print "rec.date.month==============", rec.date.month
    #         # print "fields.Date.today().month============", fields.Date.today().month
    #         # if rec.date.month == fields.Date.today().month:
    #         #     print "aaaaaaaaaaa====================="
    #             # pass




    @api.multi
    def hr_verify_sheet(self):
        move = self.env['account.move']
        move_line = self.env['account.move.line']
        
        for rec in self:
            journal = self.env['account.journal'].sudo().search([('name','=','Miscellaneous Journal'),('company_id','=',rec.company_id.id)])
            if not journal:
                pass
                # raise except_orm(_('Warning'),_('Please Create Journal With name Miscellaneous Journal'))
            if len(journal) > 1:
                raise except_orm(_('Warning!'),_('Multiple Journal with same name(Miscellaneous Journal)'))
            
            if rec.employee_id.payment_account.id == False:
                raise except_orm(_('Warning'),_('There is no payment account for this employee'))

            values = {
                    'journal_id': journal.id,
                    # 'date': rec.date,
                    }
            move_id = move.create(values)
            
            amount = 0
            contract_id = self.env['hr.contract'].search([('employee_id','=',rec.employee_id.id),('state','=','active')], limit=1).id
            for line in rec.line_ids:
              
                if line.total != 0:
                    if not contract_id:
                        raise except_orm(_('Warning'),_('There is no Active contract for this employee'))
                    amount += line.total 
            values = {
                    'account_id': rec.employee_id.payment_account.id,
                    'name': rec.name,
                    'debit': amount,
                    'credit': 0,
                    'move_id': move_id.id,
                    }
            print 'values---------------', values
            line_id = move_line.create(values)

            values2 = {
                    'account_id': rec.employee_id.payment_account.id,
                    'name': 'Employee Salary',
                    'debit': 0,
                    'credit': amount,
                    'move_id': move_id.id,
                    }
            line_id = move_line.create(values2)
            move_id.button_validate()
            rec.state = 'done'


    # @api.multi
    # def compute_sheet(self):
    #     slip_line_pool = self.env['hr.payslip.line']
    #     for rec in self:
    #         date_from = datetime.strptime(rec.date_from, '%Y-%m-%d')
    #         date_to = datetime.strptime(rec.date_to, '%Y-%m-%d')
    #         if date_from.month != date_to.month:
    #             raise exceptions.ValidationError('You cannot create employee payslip for multiple months')
    #
    #         # leave creation
    #         days = {'mon':0,'tue':1,'wed':2,'thu':3,'fri':4,'sat':5,'sun':6}
    #         date_start = datetime.strptime(rec.date_from,'%Y-%m-%d').date()
    #         date_end  = datetime.strptime(rec.date_to,'%Y-%m-%d').date()
    #         delta_day = timedelta(days=1)
    #         dt = date_start
    #         while dt <= date_end:
    #             # print 'dt.weekday()---------------------', dt.weekday()
    #             if dt.weekday() != days['sun']:
    #                 full = self.env['hiworth.hr.attendance'].search([('attendance','=','full'),('name','=', rec.employee_id.id),('date','=',dt)])
    #                 if not full:
    #                     half = self.env['hiworth.hr.attendance'].search([('attendance','=','half'),('name','=', rec.employee_id.id),('date','=',dt)])
    #                     if half:
    #                         leave = self.env['hr.holidays'].search([('attendance','=','half'),('date_from','<=',dt),('date_to','>=',dt),('type','=','remove'),('employee_id','=', rec.employee_id.id),('state','=','validate')])
    #                         if not leave:
    #                             vals = self.env['hr.holidays'].create({'attendance' : 'half',
    #                                                             'employee_id' : rec.employee_id.id,
    #                                                             'name' : 'Leave for' + '' + rec.employee_id.name,
    #                                                             'date_from' : dt,
    #                                                             'date_to' : dt,
    #                                                             'type' : 'remove',
    #                                                             'leave_id': self.env.ref('hr_holidays.holiday_status_cl').id,
    #                                                             'state' : 'validate'
    #                                                             })
    #                             vals.action_validate()
    #                     else:
    #                         leave = self.env['hr.holidays'].search([('attendance','=','full'),('date_from','<=',dt),('date_to','>=',dt),('type','=','remove'),('employee_id','=', rec.employee_id.id),('state','=','validate')])
    #                         if not leave:
    #                             vals = self.env['hr.holidays'].create({'attendance' : 'full',
    #                                                             'employee_id' : rec.employee_id.id,
    #                                                             'name' : 'Leave for' + '' + rec.employee_id.name,
    #                                                             'date_from' : dt,
    #                                                             'date_to' : dt,
    #                                                             'type' : 'remove',
    #                                                             'leave_id': self.env.ref('hr_holidays.holiday_status_cl').id,
    #                                                             'state' : 'validate'
    #                                                             })
    #                             vals.action_validate()
    #
    #             dt += delta_day
    #
    #
    #
    #
    #         amount = 0
    #         quantity=1
    #         day_count=0
    #         cant_amt = 0
    #
    #         basic_amount = 0
    #         canteen_amount = 0
    #         canteen_amt = 0
    #         canteen_qty = 0
    #         lop_amount = 0
    #         insurance_amount = 0
    #         welfare_amount = 0
    #         other_amount = 0
    #         pf_amount = 0
    #         esi_amount = 0
    #
    #
    #         today = date.today()
    #         d = datetime.strptime(rec.date_from, '%Y-%m-%d')
    #         start = date(d.year, d.month, 1)
    #         end = date(today.year, today.month, 1) - relativedelta(days=1)
    #         print 'date.today()------------------------------', date.today(), d, start, end
    #         lop_days = 0
    #
    #         allocation = self.env['hr.employee'].search([('id','=', rec.employee_id.id)])
    #
    #         for leave_type in allocation.leave_ids:
    #             taken = 0.0
    #             days = 0
    #             holiday = self.env['hr.holidays'].search([('date_from','<=', rec.date_from),('date_to','>=', rec.date_from),('type','=','remove'),('leave_id','=',leave_type.leave_id.id),('employee_id','=', rec.employee_id.id),('state','=','validate')])
    #             for hol_id in holiday:
    #                 if hol_id.attendance == 'full':
    #                     taken += hol_id.nos
    #                 elif hol_id.attendance == 'half':
    #                     taken += float(hol_id.nos)/2
    #                 else:
    #                     pass
    #
    #             holiday = self.env['hr.holidays'].search([('date_from','<=', rec.date_from),('date_to','>=', rec.date_from),('type','=','remove'),('leave_id','=',leave_type.leave_id.id),('employee_id','=', rec.employee_id.id),('state','=','validate')])
    #             for hol_id in holiday:
    #                 if hol_id.attendance == 'full':
    #                     taken += hol_id.nos
    #                 elif hol_id.attendance == 'half':
    #                     taken += float(hol_id.nos)/2
    #                 else:
    #                     pass
    #             print 'taken-------------------------', taken, lop_days
    #             status = self.env['month.leave.status'].search([('leave_id','=', leave_type.leave_id.id),('month_id','=',d.month),('status_id','=', allocation.id)], limit=1)
    #             if status.allowed < taken:
    #                 days = taken - status.allowed
    #             lop_days = lop_days + days
    #         print 'lop_days----------------------------', lop_days
    #
    #         days = {'mon':0,'tue':1,'wed':2,'thu':3,'fri':4,'sat':5,'sun':6}
    #         date_start = datetime.strptime(rec.date_from,'%Y-%m-%d').date()
    #         date_end  = datetime.strptime(rec.date_to,'%Y-%m-%d').date()
    #
    #         delta_day = timedelta(days=1)
    #         dt = date_start
    #         while dt <= date_end:
    #             if dt.weekday() == days['sun']:
    #                 week_start = dt - relativedelta(days=6)
    #                 week_end = dt
    #                 # print 'weekk------------------------------------', week_start, week_end
    #                 full = self.env['hiworth.hr.attendance'].search([('attendance','=','full'),('name','=', rec.employee_id.id),('date','>',week_start),('date','<',week_end)])
    #                 half = self.env['hiworth.hr.attendance'].search([('attendance','=','half'),('name','=', rec.employee_id.id),('date','>',week_start),('date','<',week_end)])
    #                 print 'len(full) + len(half)-----------------', full, half, len(full) + len(half)
    #                 # print 'chck22---------------------------------', lop_days
    #                 if (len(full) + (len(half)/2)) < 3:
    #                     lop_days = lop_days + 1
    #                 # print 'chck11---------------------------------', lop_days
    #             dt += delta_day
    #
    #
    #         lop_amount = rec.contract_id.wage/((abs((date_end - date_start).days)) + 1)
    #         print 'z-------------------------------------------------', lop_amount, ((abs((date_end - date_start).days)) + 1)
    #
    #
    #
    #         # for leave_type in allocation.leave_ids:
    #         #     taken = 0.0
    #         #     days = 0
    #         #     holiday = self.env['hr.holidays'].search([('type','=','remove'),('leave_id','=',leave_type.leave_id.id),('employee_id','=', rec.employee_id.id),('state','=','validate')])
    #         #     for hol_id in holiday:
    #         #         if hol_id.attendance == 'full':
    #         #             taken += hol_id.nos
    #         #         elif hol_id.attendance == 'half':
    #         #             taken += float(hol_id.nos)/2
    #         #         else:
    #         #             pass
    #
    #         #     status = self.env['month.leave.status'].search([('leave_id','=', leave_type.leave_id.id),('month_id','=',d.month),('status_id','=', allocation.id)], limit=1)
    #         #     if status.allowed < taken:
    #         #         days = taken - status.allowed
    #         #     lop_days = lop_days + days
    #         # print 'lop_days----------------------------', lop_days
    #         # if lop_days != 0:
    #
    #         #     date_start = datetime.strptime(rec.date_from,'%Y-%m-%d').date()
    #         #     date_end  = datetime.strptime(rec.date_to,'%Y-%m-%d').date()
    #         #     delta_day = timedelta(days=1)
    #         #     days = {'mon':0,'tue':1,'wed':2,'thu':3,'fri':4,'sat':5,'sun':6}
    #         #     dt = date_start
    #         #     while dt <= date_end:
    #         #         if dt.weekday() != days['sun']:
    #         #             day_count+=1
    #         #         dt += delta_day
    #         #     holidays = self.env['public.holiday'].search([('date','>=', rec.date_from),('date','<=', rec.date_to)])
    #         #     working_days = day_count - len(holidays)
    #         #     lop_amount = rec.contract_id.wage/working_days
    #
    #         for i in range(2):
    #             print 'i----------------', i
    #             if i == 0:
    #                 for lines in rec.contract_id.rule_lines:
    #
    #                     insurance_id = ''
    #
    #                     if lines.rule_id.related_type == 'basic':
    #                         basic_amount = rec.contract_id.wage
    #                         amount = basic_amount
    #                         quantity = 1
    #
    #                     elif lines.rule_id.related_type == 'canteen':
    #                         canteen = self.env['canteen.daily'].search([('employee_id','=', rec.employee_id.id),('date','>=', rec.date_from),('date','<=', rec.date_to)])
    #                         # print 'len(canteen)------------------------------', len(canteen)
    #                         # for canteen_id in canteen:
    #                         #     cateen_amount += canteen_id.amount
    #                         # amount = cateen_amount
    #                         amount = self.env['general.hr.configuration'].search([],limit=1).canteen_amount
    #                         quantity = len(canteen)
    #                         canteen_amt = amount
    #                         canteen_qty = quantity
    #                         print 'canteen--------------------', canteen_amt, canteen_qty
    #
    #                     elif lines.rule_id.related_type == 'attendance':
    #
    #                             amount = lop_amount
    #                             quantity = lop_days
    #
    #                     elif lines.rule_id.related_type == 'esi':
    #                         quantity = 1
    #                         contract_amt = 0
    #                         if basic_amount <= lines.rule_id.salary_limit:
    #                             contract_amt = basic_amount
    #
    #                         else:
    #                             month = datetime.strptime(rec.date_from,'%Y-%m-%d').month
    #                             print 'month-----------------------------------', month
    #                             fin1 = self.env['general.hr.configuration'].search([('fin1_start','<=', month),('fin1_end','>=', month)])
    #                             if fin1:
    #                                 fin_date = date(datetime.strptime(rec.date_from, '%Y-%m-%d').year, fin1, 1)
    #                                 contract = self.env['hr.contract'].search([('date_start','<=',fin_date),('date_end','>=',fin_date),('employee_id','=', rec.employee_id.id)], limit=1).wage
    #                                 if contract <= lines.rule_id.salary_limit:
    #                                     contract_amt = lines.rule_id.salary_limit
    #
    #                             fin2 = self.env['general.hr.configuration'].search([('fin2_start','<=', month),('fin2_end','>=', month)])
    #                             if fin2:
    #                                 year = datetime.strptime(rec.date_from, '%Y-%m-%d').year
    #                                 fin_date = date(year, fin2, 1)
    #                                 contract = self.env['hr.contract'].search([('date_start','<=',fin_date),('date_end','>=',fin_date),('employee_id','=', rec.employee_id.id)], limit=1).wage
    #                                 if contract <= lines.rule_id.salary_limit:
    #                                     contract_amt = lines.rule_id.salary_limit
    #
    #
    #
    #                         amount = (contract_amt - (lop_amount * lop_days))*(lines.rule_id.emloyee_ratio/100)
    #                         esi_amount = amount
    #
    #                     elif lines.rule_id.related_type == 'pf':
    #                         quantity = 1
    #                         print 'asdfg---------------------------',basic_amount,lines.rule_id.pf_sealing_limit,lop_amount * lop_days,amount,pf_amount
    #                         if basic_amount <= lines.rule_id.pf_sealing_limit:
    #                             print '11111111111111'
    #                             amount = (basic_amount - (lop_amount * lop_days))*(lines.rule_id.emloyee_ratio/100)
    #                         else:
    #                             print '222222222222', lines.rule_id.pf_sealing_limit, (lop_amount * lop_days)
    #                             amount = (lines.rule_id.pf_sealing_limit - (lop_amount * lop_days))*(lines.rule_id.emloyee_ratio/100)
    #                         print 'asdfg1111111111---------------------------',amount,pf_amount
    #                         pf_amount = amount
    #
    #                     elif lines.rule_id.related_type == 'insurance':
    #                         insurance = self.env['employee.insurance'].search([('policy_id','=',lines.rule_id.policy_id.id),('employee_id','=', rec.employee_id.id),('is_company_policy','=',True),('state','=','paid')], order='commit_date asc',limit=1)
    #                         amount = insurance.empol_contribution - insurance.emp_paid_amt
    #                         insurance_amount = insurance_amount + amount
    #                         insurance_id = insurance.id
    #                         quantity = 1
    #
    #                     elif lines.rule_id.related_type == 'welfare':
    #                         amount = 0
    #                         welfares = self.env['employee.welfare.fund'].search([('state','=','active'),('employee_id','=', rec.employee_id.id)])
    #                         for welf_id in welfares:
    #                             amount += (welf_id.amount - welf_id.repay_amount)
    #                             quantity = 1
    #                         welfare_amount = amount
    #
    #                     else:
    #                         amount = 0
    #                         if lines.is_related == True:
    #                             pass
    #                         else:
    #                             # print 'ded-exp-----------------------', lines.rule_id.name, lines.rule_id.rule_nature, lines.rule_type
    #                             if lines.rule_id.rule_nature == 'allowance':
    #
    #                                 if lines.rule_type == 'fixed':
    #                                     other_amount = other_amount + lines.amount
    #                                     amount = lines.amount
    #                                 if lines.rule_type == 'percent':
    #                                     # print 'other--------------------', other_amount, ((lines.percentage * rec.contract_id.wage)/100)
    #                                     other_amount = other_amount + ((lines.percentage * rec.contract_id.wage)/100)
    #                                     amount = ((lines.percentage * rec.contract_id.wage)/100)
    #
    #                             if lines.rule_id.rule_nature == 'deduction':
    #
    #                                 if lines.rule_type == 'fixed':
    #                                     other_amount = other_amount - lines.amount
    #                                     amount = lines.amount
    #                                 if lines.rule_type == 'percent':
    #                                     other_amount = other_amount - ((lines.percentage * rec.contract_id.wage)/100)
    #                                     amount = ((lines.percentage * rec.contract_id.wage)/100)
    #                     # print 'amt-----------------------------', lines.rule_id.name, amount, other_amount
    #
    #                     if amount != 0 and quantity != 0 and lines.rule_id.related_type != 'net':
    #                         values = {
    #                             'salary_rule_id': lines.rule_id.id,
    #                             'contract_id': rec.contract_id.id,
    #                             'name': lines.rule_id.name,
    #                             'rule_id': lines.rule_id.id,
    #                             'code': lines.rule_id.code,
    #                             'category_id': lines.rule_id.category_id.id,
    #                             'sequence': lines.rule_id.sequence,
    #                             'appears_on_payslip': lines.rule_id.appears_on_payslip,
    #                             'condition_select': lines.rule_id.condition_select,
    #                             'condition_python': lines.rule_id.condition_python,
    #                             'condition_range': lines.rule_id.condition_range,
    #                             'condition_range_min': lines.rule_id.condition_range_min,
    #                             'condition_range_max': lines.rule_id.condition_range_max,
    #                             'amount_select': lines.rule_id.amount_select,
    #                             'amount_fix': lines.rule_id.amount_fix,
    #                             'amount_python_compute': lines.rule_id.amount_python_compute,
    #                             'amount_percentage': lines.rule_id.amount_percentage,
    #                             'amount_percentage_base': lines.rule_id.amount_percentage_base,
    #                             'register_id': lines.rule_id.register_id.id,
    #                             'amount': amount,
    #                             'insurance_id':insurance_id,
    #                             # 'amount': lines.amount,
    #                             # 'total': total,
    #                             'employee_id': rec.employee_id.id,
    #                             'quantity': quantity,
    #                             'rate': lines.amount,
    #                             'slip_id': rec.id
    #                         }
    #                         payslip = slip_line_pool.create(values)
    #                         payslip._calculate_total()
    #             if i == 1:
    #                 print 'canteen111111111111111111--------------------', canteen_amt, canteen_qty, canteen_amt * canteen_qty
    #                 for lines in rec.contract_id.rule_lines:
    #                     amount = 0
    #                     insurance_id = ''
    #                     quantity=1
    #
    #                     if lines.rule_id.related_type == 'net':
    #                         quantity=1
    #                         print 'amt-------------------------------------------------', basic_amount, (canteen_amt * canteen_qty), (lop_amount * lop_days), insurance_amount, welfare_amount, pf_amount, esi_amount, other_amount
    #                         amount = basic_amount - (canteen_amt * canteen_qty) - (lop_amount * lop_days) - insurance_amount - welfare_amount - pf_amount - esi_amount + other_amount
    #
    #                         # print 'amt-----------------------------', basic_amount, cateen_amount, lop_amount, insurance_amount
    #                         values = {
    #                             'salary_rule_id': lines.rule_id.id,
    #                             'contract_id': rec.contract_id.id,
    #                             'name': lines.rule_id.name,
    #                             'rule_id': lines.rule_id.id,
    #                             'code': lines.rule_id.code,
    #                             'category_id': lines.rule_id.category_id.id,
    #                             'sequence': lines.rule_id.sequence,
    #                             'appears_on_payslip': lines.rule_id.appears_on_payslip,
    #                             'condition_select': lines.rule_id.condition_select,
    #                             'condition_python': lines.rule_id.condition_python,
    #                             'condition_range': lines.rule_id.condition_range,
    #                             'condition_range_min': lines.rule_id.condition_range_min,
    #                             'condition_range_max': lines.rule_id.condition_range_max,
    #                             'amount_select': lines.rule_id.amount_select,
    #                             'amount_fix': lines.rule_id.amount_fix,
    #                             'amount_python_compute': lines.rule_id.amount_python_compute,
    #                             'amount_percentage': lines.rule_id.amount_percentage,
    #                             'amount_percentage_base': lines.rule_id.amount_percentage_base,
    #                             'register_id': lines.rule_id.register_id.id,
    #                             'amount': amount,
    #                             'insurance_id':insurance_id,
    #                             # 'amount': lines.amount,
    #                             # 'total': total,
    #                             'employee_id': rec.employee_id.id,
    #                             'quantity': quantity,
    #                             'rate': lines.amount,
    #                             'slip_id': rec.id
    #                         }
    #                         payslip = slip_line_pool.create(values)
    #                         payslip._calculate_total()
    #                     else:
    #                         pass
    #
    #         rec.state = 'verify'
    #     return True


    # @api.multi
    # def compute_sheet(self):
    #     slip_line_pool = self.env['hr.payslip.line']
    #     for rec in self:
    #         date_from = datetime.strptime(rec.date_from, '%Y-%m-%d')
    #         date_to = datetime.strptime(rec.date_to, '%Y-%m-%d')
    #         if date_from.month != date_to.month:
    #             raise exceptions.ValidationError('You cannot create employee payslip for multiple months')
    #         for lines in rec.contract_id.rule_lines:
                
    #             day_count=0
    #             quantity=1
    #             cant_amt = 0
    #             amount = 0

    #             basic_amount = 0
    #             cateen_amount = 0
    #             lop_amount = 0
    #             insurance_amount = 0
    #             insurance = ''
    #             basic_amount = rec.contract_id.wage

    #             canteen = self.env['canteen.daily'].search([('employee_id','=', rec.employee_id.id),('date','>=', rec.date_from),('date','<=', rec.date_to)])
    #             for canteen_id in canteen:
    #                 cateen_amount += canteen_id.amount

    #             today = date.today()
    #             # d = today - relativedelta(months=1)
    #             d = datetime.strptime(rec.date_from, '%Y-%m-%d') 
    #             start = date(d.year, d.month, 1)
    #             end = date(today.year, today.month, 1) - relativedelta(days=1)
    #             lop_days = 0

    #             # allocation = self.env['hr.holidays'].search([('type','=','add'),('employee_id','=', rec.employee_id.id)],limit=1)
    #             allocation = self.env['hr.employee'].search([('id','=', rec.employee_id.id)])

    #             for leave_type in allocation.leave_ids:
    #                 taken = 0.0
    #                 days = 0
    #                 holiday = self.env['hr.holidays'].search([('type','=','remove'),('leave_id','=',leave_type.leave_id.id),('employee_id','=', rec.employee_id.id),('state','=','validate')])
    #                 for hol_id in holiday:
    #                     # if (str(start) <= hol_id.date_from <= str(end)) or (str(start) <= hol_id.date_to<= str(end)):
    #                     # if (rec.date_from <= hol_id.date_from <= rec.date_to) or (rec.date_from <= hol_id.date_to<= rec.date_to):
    #                     #     date_from = datetime.strptime(hol_id.date_from, '%Y-%m-%d').date()
    #                     #     date_to = datetime.strptime(hol_id.date_to, '%Y-%m-%d').date()
    #                     #     delta = date_to - date_from
                            
    #                     if hol_id.attendance == 'full':
    #                         # for i in range(delta.days + 1):
    #                         #     if (date_from + timedelta(i)).month == d.month:
    #                         taken += hol_id.nos
                        
    #                     elif hol_id.attendance == 'half':
    #                         taken += float(hol_id.nos)/2
    #                         # for i in range(delta.days + 1):
    #                         #     if (date_from + timedelta(i)).month == d.month:
    #                         #         taken += 0.5
                        
    #                     else:
    #                         pass
                       
    #                 status = self.env['month.leave.status'].search([('leave_id','=', leave_type.leave_id.id),('month_id','=',d.month),('status_id','=', allocation.id)], limit=1)
    #                 if status.allowed < taken:
    #                     days = taken - status.allowed
    #                 lop_days = lop_days + days

    #             date_start = datetime.strptime(rec.date_from,'%Y-%m-%d').date()
    #             date_end  = datetime.strptime(rec.date_to,'%Y-%m-%d').date()
    #             delta_day = timedelta(days=1)
    #             days = {'mon':0,'tue':1,'wed':2,'thu':3,'fri':4,'sat':5,'sun':6}
    #             dt = date_start
    #             while dt <= date_end:
    #                 if dt.weekday() != days['sun']:
    #                     day_count+=1
    #                 dt += delta_day
    #             holidays = self.env['public.holiday'].search([('date','>=', rec.date_from),('date','<=', rec.date_to)])
    #             working_days = day_count - len(holidays)
    #             lop_amount = rec.contract_id.wage/working_days

    #             if lines.rule_id.related_type == 'insurance':
    #                 insurance = self.env['employee.insurance'].search([('policy_id','=',lines.rule_id.policy_id.id),('employee_id','=', rec.employee_id.id),('is_company_policy','=',True),('state','=','paid')], order='commit_date asc',limit=1)
    #                 insurance_amount = insurance.empol_contribution - insurance.emp_paid_amt


    #             if lines.rule_id.related_type == 'basic':
    #                 amount = basic_amount

    #             elif lines.rule_id.related_type == 'canteen':
    #                 amount += cateen_amount

    #             elif lines.rule_id.related_type == 'attendance':
    #                 amount = lop_amount
    #                 quantity = lop_days
    #             elif lines.rule_id.related_type == 'esi':
    #                 if basic_amount <= lines.rule_id.salary_limit:
    #                     amount = basic_amount*((lines.rule_id.emloyee_ratio+lines.rule_id.emloyer_ratio)/100)
    #             elif lines.rule_id.related_type == 'pf':
    #                 if basic_amount >= lines.rule_id.salary_limit:
    #                     amount = basic_amount*(lines.rule_id.emloyee_ratio+lines.rule_id.emloyer_ratio)/100
    #             elif lines.rule_id.related_type == 'insurance':
    #                 amount = insurance_amount
    #             elif lines.rule_id.related_type == 'net':
    #                 amount = basic_amount - cateen_amount - lop_amount - insurance_amount

    #             else:
    #                 pass
                
    #             values = {
    #                 'salary_rule_id': lines.rule_id.id,
    #                 'contract_id': rec.contract_id.id,
    #                 'name': lines.rule_id.name,
    #                 'rule_id': lines.rule_id.id,
    #                 'code': lines.rule_id.code,
    #                 'category_id': lines.rule_id.category_id.id,
    #                 'sequence': lines.rule_id.sequence,
    #                 'appears_on_payslip': lines.rule_id.appears_on_payslip,
    #                 'condition_select': lines.rule_id.condition_select,
    #                 'condition_python': lines.rule_id.condition_python,
    #                 'condition_range': lines.rule_id.condition_range,
    #                 'condition_range_min': lines.rule_id.condition_range_min,
    #                 'condition_range_max': lines.rule_id.condition_range_max,
    #                 'amount_select': lines.rule_id.amount_select,
    #                 'amount_fix': lines.rule_id.amount_fix,
    #                 'amount_python_compute': lines.rule_id.amount_python_compute,
    #                 'amount_percentage': lines.rule_id.amount_percentage,
    #                 'amount_percentage_base': lines.rule_id.amount_percentage_base,
    #                 'register_id': lines.rule_id.register_id.id,
    #                 'amount': amount,
    #                 'insurance_id':insurance.id,
    #                 # 'amount': lines.amount,
    #                 # 'total': total,
    #                 'employee_id': rec.employee_id.id,
    #                 'quantity': quantity,
    #                 'rate': lines.amount,
    #                 'slip_id': rec.id
    #             }
    #             payslip = slip_line_pool.create(values)
    #             payslip._calculate_total()

    #         rec.state = 'verify'
    #     return True

   

class ResCompany(models.Model):
    _inherit = 'res.company'

    salary_expense_id = fields.Many2one('account.account', 'Salary Expense Account')


class EmployeeConfigLeave(models.Model):
    _name = 'employee.config.leave'

    @api.depends('available', 'availa_exgre')
    def compute_total_available(self):
        for rec in self:
            rec.total_available = rec.available + rec.availa_exgre + rec.nos

    @api.depends('total_available','availed')
    def compute_remaining(self):
        for rec in self:
            rec.remaining = rec.total_available - rec.availed

    leave_id = fields.Many2one('hr.holidays.status',"Leave Type")
    nos = fields.Float("Allocated")
    available = fields.Float("Available CL")
    availa_exgre = fields.Float("Available Exgratia")
    total_available = fields.Float("Total Available",compute='compute_total_available')
    availed = fields.Float("Availed")
    remaining = fields.Float("Remaining",compute='compute_remaining')
    contract_id = fields.Many2one('hr.contract',"Contract")
    employee_id = fields.Many2one('hr.employee', related='contract_id.employee_id')


class EmployeeLeave(models.Model):
    _name = 'employee.leave'

    leave_id = fields.Many2one('hr.holidays.status', 'Leave Type')
    nos = fields.Float('No of Days')
    remaining = fields.Float('Remaining')
    taken_leaves = fields.Float('Taken Leaves')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    holiday_id = fields.Many2one('hr.holidays', 'Leave Approve')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    state = fields.Selection([('active','Active'),
                              ('deactivate','Deactivate')], 'State')
    contract_id = fields.Many2one('hr.contract',"Contract")


    @api.multi
    def action_deactivate(self):
        self.state = 'deactivate'


class hr_payslip_line(models.Model):
    _inherit = 'hr.payslip.line'

    @api.multi
    @api.depends('quantity','amount')
    def _calculate_total(self):
        for record in self:
            print 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
            record.total = record.quantity * record.amount
            


    amount = fields.Float('Amount', digits_compute=dp.get_precision('Payroll'), store=True)
    total = fields.Float(compute="_calculate_total", string='Total', digits_compute=dp.get_precision('Payroll'),store=True )
    rule_id = fields.Many2one('hr.salary.rule', string="Name")
    related_type = fields.Selection(related="rule_id.related_type", string="Related Process")
    insurance_id = fields.Many2one('employee.insurance','Employee Insurance')
    state = fields.Selection(related="slip_id.state")


    # @api.multi
    # def write(self, vals):
    #     if self.related_type == 'insurance':
    #         print 'amt123456-------------------------------', vals.get('amount'), self.amount
    #         if vals.get('amount') != None and vals.get('amount') != self.amount:

    #             lines = self.env['hr.payslip.line'].search([('slip_id','=',self.slip_id.id),('related_type','=','net')],limit=1)
    #             lines.amount = lines.amount - self.amount + vals.get('amount')   
    #     result = super(hr_payslip_line, self).write(vals)

    #     return result

    @api.multi
    def write(self, vals):
        result = super(hr_payslip_line, self).write(vals)
        # self.ensure_one()
        if vals.get('amount') != None and vals.get('amount') != self.amount:
            deduction = 0
            allowance = 0
            lines = self.env['hr.payslip.line'].search([('slip_id','=',self.slip_id.id),('related_type','!=','net'),('related_type','!=',self.related_type)])
            print 'lines-----------------------------------------', lines
            for line_id in lines:
                if line_id.rule_id.rule_nature == 'deduction':
                    deduction += (line_id.amount * line_id.quantity)
                if line_id.rule_id.rule_nature == 'allowance':
                    allowance += (line_id.amount * line_id.quantity)

            if self.related_type == 'insurance':
                if self.rule_id.rule_nature == 'deduction':
                    deduction += (vals.get('amount') * self.quantity)
                if self.rule_id.rule_nature == 'allowance':
                    allowance += (vals.get('amount') * self.quantity)

            net = self.env['hr.payslip.line'].search([('slip_id','=',self.slip_id.id),('related_type','=','net')],limit=1)
            net.amount = allowance - deduction

            return result


    # @api.onchange('quantity','amount')
    # def onchange_net_amount(self):
    #     amount = 0
    #     basic_amount = 0
    #     cateen_amount = 0
    #     lop_amount = 0
    #     insurance_amount = 0
    #     print 'chck------------------------------', self._origin
    #     lines = self.env['hr.payslip.line'].search([('slip_id','=',self._origin.slip_id.id)])

    #     print 'lines-------------------------------'
    #     for i in range(2):
    #         print 'i----------------', i
    #         if i == 0:
    #             for line in lines:
    #                 if self._origin.id != line.id:
    #                     print '1-------------------------------', self._origin.id, line.id
    #                     if line.rule_id.related_type == 'basic':
    #                         basic_amount = line.amount

    #                     elif line.rule_id.related_type == 'canteen':
    #                         cateen_amount = line.amount

    #                     elif line.rule_id.related_type == 'attendance':
    #                         lop_amount = line.amount

    #                     elif line.rule_id.related_type == 'insurance':
    #                         insurance_amount += line.amount

    #                     else:
    #                         pass
    #                 if self._origin.id == line.id:
    #                     print '2-------------------------------', self._origin.id, line.id
    #                     print '3-------------------------------', self._origin.amount, line.amount
    #                     if self._origin.rule_id.related_type == 'basic':
    #                         basic_amount = self._origin.amount

    #                     elif self._origin.rule_id.related_type == 'canteen':
    #                         cateen_amount = self._origin.amount

    #                     elif self._origin.rule_id.related_type == 'attendance':
    #                         lop_amount = self._origin.amount

    #                     elif self._origin.rule_id.related_type == 'insurance':
    #                         insurance_amount += self._origin.amount

    #                     else:
    #                         pass


    #         if i == 1:
    #             for line in lines:
    #                 if line.rule_id.related_type == 'net':
    #                     print 'amts-------------', basic_amount,cateen_amount,lop_amount,insurance_amount, line.amount
    #                     amount = basic_amount - cateen_amount - lop_amount - insurance_amount
    #                     line.update({'amount' : amount})
    #                     print 'line.amount--------', line.amount

    #                 else:
    #                     pass



class EmployeeZone(models.Model):
    _name = 'hr.employee.zone'

    name = fields.Char('Zone Name')

class HrEmployeeResignation(models.TransientModel):
    _name='hr.employee.resignation'

    resign_date = fields.Date('Released Date', default=fields.Date.today)
    resign_id =fields.Many2one('hr.employee')
    user_category = fields.Selection(related="resign_id.user_category")
    emp_code = fields.Char(related="resign_id.emp_code")
    mob_sim_return = fields.Boolean('Mobile - SIM Card Returned?')
    id_return = fields.Boolean('ID Card Returned?')
    atm_return = fields.Boolean('ATM Card Returned?')
    accounts_settled = fields.Boolean('Accounts Settled?')
    emp_satisfaction = fields.Text('Are you satisfied with this job?')
    reason_resign = fields.Text('Reason for resignation?')
    company_faults = fields.Text('Is there any fault from company side?')
    resigned = fields.Boolean(string="Resigned")
    terminated = fields.Boolean(string="Terminated")

    @api.multi
    def button_confirm(self):
        self.resign_id.resigning_date = self.resign_date
        self.resign_id.status1 = 'resign'
        self.resign_id.active = True


class hr_payslip_employees(models.Model):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self, cr, uid, ids, context=None):
        emp_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        slip_ids = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        run_data = {}
        if context and context.get('active_id', False):
            run_data = run_pool.read(cr, uid, [context['active_id']], ['date_start', 'date_end', 'credit_note'])[0]
        from_date = run_data.get('date_start', False)
        to_date = run_data.get('date_end', False)
        credit_note = run_data.get('credit_note', False)
        if not data['employee_ids']:
            raise osv.except_osv(_("Warning!"), _("You must select employee(s) to generate payslip(s)."))
        for emp in emp_pool.browse(cr, uid, data['employee_ids'], context=context):
            slip_data = slip_pool.onchange_employee_id(cr, uid, [], from_date, to_date, emp.id, contract_id=False,
                                                       context=context)
            res = {
                'employee_id': emp.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'month':datetime.strptime(to_date, "%Y-%m-%d").strftime('%B') or datetime.strptime(from_date, "%Y-%m-%d").strftime('%B'),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
            }
            slip_ids.append(slip_pool.create(cr, uid, res, context=context))
        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
