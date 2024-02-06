from openerp import models, fields, api, _
from datetime import datetime, date, timedelta
from openerp.osv import osv
from dateutil.relativedelta import relativedelta
from datetime import *
from openerp.exceptions import except_orm, ValidationError
import openerp.addons.decimal_precision as dp


class ContractSalaryRule(models.Model):
    _name = 'contract.salary.rule'

    hr_payslip_id = fields.Many2one('hr.payslip')
    rule_id = fields.Many2one('hr.salary.rule', 'Name')
    percentage_base = fields.Selection([
        ('basic', 'Basic'),
        ('gross', 'Gross'),
    ], 'Percentage based on')
    account_id = fields.Many2one('account.account', 'Related Account')
    contract_id = fields.Many2one('hr.contract', 'Contract')
    amount = fields.Float('Amount')
    # amount = fields.Float('Amount', compute="amount_compute", inverse="compute_inverse_amount",readonly=False)
    amount_percentage = fields.Float('Percentage(%)')
    related_type = fields.Selection('Rule Process Type', related='rule_id.related_type')
    amount_select = fields.Selection([
        ('fix', 'Fixed'),
        ('percentage', 'Percentage'),
        ('code','Code'),
    ], 'Amount Type')
    is_related = fields.Boolean('Is related to any daily activities', default=False)
    rule_type = fields.Selection([('gross', 'Gross'),('net', 'Net'),('Earning', 'Earning'), ('Deduction', 'Deduction')], 'Salary Type')
    # related_type = fields.Selection([('canteen','canteen')], 'Related Process')
    per_day_amount = fields.Float('Per Day Amount')
    employer_amt_paid_by = fields.Selection([('employer', 'Paid by employer'),
                                             ('govt', 'Paid by government')
                                             ], default="employer", string="Employer Percent")

    # amount_select = fields.Selection([
    # 	('percentage', 'Percentage (%)'),
    # 	('fix', 'Fixed Amount'),
    # 	('code', 'Python Code'), ], string='Amount Type', select=True, required=True,
    # 	help="The computation method for the rule amount.")
    #
    amount_fix = fields.Float('Fixed Amount', digits_compute=dp.get_precision('Payroll'), )
    # amount_percentage = fields.Float('Percentage (%)', digits_compute=dp.get_precision('Payroll Rate'))
    # amount_python_compute = fields.Text('Python Code')
    # amount_percentage_base = fields.Char('Percentage based on')
    # quantity = fields.Char('Quantity')
    code = fields.Char('Code', size=64)

    @api.depends('amount_fix', 'amount_percentage')
    def amount_compute(self):
        for rec in self:
            if rec.amount_select == 'amount_percentage':
                rec.amount = rec.contract_id.wage * (rec.amount_percentage / 100)
            else:
                rec.amount = rec.amount_fix

    @api.onchange('rule_id')
    def onchange_rule_id(self):
        for rec in self:
            if rec.rule_id:
                for rule in rec.rule_id:
                    rec.amount_percentage = rule.amount_percentage or 0.0
                    # if rule.amount_select == 'code':
                    # 	rec.amount_python_compute = rule.amount_python_compute
                    rec.amount_fix = rule.amount_fix or 0.0
                    rec.quantity = rule.quantity or 0
                    rec.amount_select = rule.amount_select or ""
                    rec.amount_percentage_base = rule.amount_percentage_base or ""
                    rec.code = rule.code or ""
                    rec.percentage_base = rule.percentage_base or ""
                    rec.rule_type = rule.rule_type or ""

    @api.onchange('related_type', 'rule_id')
    def onchange_per_day_amount(self):
        if self.related_type == 'canteen':
            self.is_related = True
            self.per_day_amount = self.env['general.hr.configuration'].search([], limit=1).canteen_amount


# @api.model
# def create(self, vals):
# 	print 'vals======================', vals
# 	if vals.get('related_type') == 'canteen':
# 		rule = self.env['contract.salary.rule'].search([('contract_id','=',vals.get('contract_id')),('related_type','=','canteen')])
# 		if rule:
# 			raise osv.except_osv(('Error'), ('Already Exist a rule with type "Canteen".'));
# 	return super(ContractSalaryRule, self).create(vals)

# @api.model
# def create(self, vals):
# 	print 'vals======================', vals
# 	if vals.get('related_type') == 'canteen':
# 		rule = self.env['contract.salary.rule'].search([('contract_id','=',self.contract_id.id),('related_type','=','canteen')])
# 		if rule:
# 			raise osv.except_osv(('Error'), ('Already Exist a rule with type "Canteen".'));
# 	return super(ContractSalaryRule, self).create(vals)

# @api.onchange('rule_type')
# def onchange_amount(self):
# 	if self.rule_type == 'lop':
# 		self.amount = amount
# 		days_count = 0
# 		start_date = 01/05/2017
# 		end_date = 30/05/2017
# 		while (start_date < end_date):
# 			day = dateutil.parser.parse(start_date).date().weekday()
# 			if day != 1:
# 				days_count += 1
# 			start_date = start_date  + datetime.timedelta(days=1)
# 			print 'days_count------------', days_count
# lop =

class HrContract(models.Model):
    _inherit = 'hr.contract'
    _order = 'date_start desc'

    @api.onchange('struct_id')
    def onchange_struct_id(self):
        line_ids = []
        self.rule_lines = False
        self.hr_salary_rule = False
        if self.struct_id:
            for rule in self.struct_id.rule_ids:
                values = {
                    'rule_id': rule.id,
                    'amount_percentage': rule.amount_percentage,
                    'amount_python_compute': rule.amount_python_compute,
                    'amount_fix': rule.amount_fix,
                    'quantity': rule.quantity,
                    'amount_select': rule.amount_select,
                    'amount_percentage_base': rule.amount_percentage_base,
                    'percentage_base': rule.percentage_base,
                    'code': rule.code,
                    'sequence': rule.sequence,
                    'rule_type': rule.rule_type,
                }
                line_ids.append((0, 0, values))
            self.rule_lines = line_ids

        # for rule in self.struct_id.rule_ids:

    # 	if rule.related_type == 'canteen':
    # 		values = {
    # 			'rule_id': rule.id,
    # 			'name': rule.name,
    # 			'is_related': True,
    # 			'per_day_amount': self.env['general.hr.configuration'].search([],limit=1).canteen_amount,
    # 		}
    # 	else:
    # 		values = {
    # 			'rule_id': rule.id,
    # 			'name': rule.name,
    # 		}
    # 	line_ids.append((0, 0, values ))
    # self.rule_lines = line_ids

    @api.onchange('employee_id')
    def _generate_reference(self):
        for rec in self:
            if rec.employee_id:
                latest_contract = self.search([], limit=1, order='id desc')
                rec.reference_number = rec.employee_id.name + "/" + str(date.today()) + "/" + str(
                    latest_contract.id + 1)
                rec.name = rec.reference_number

    @api.onchange('employee_id')
    def onchange_new_employee(self):
        for rec in self:
            rec.name = rec.employee_id.name

    @api.depends('employee_id')
    def _onchange_employee(self):
        ids = []
        for employee in self.env['hr.employee'].search([('cost_type', '=', 'permanent')]):
            ids.append(employee.id)
        return {'domain': {'employee_id': [('id', 'in', ids)]}}

    @api.depends('available_exgratia', 'availed_exgratia')
    def compute_availed(self):
        for rec in self:
            if rec.available_exgratia >= rec.availed_exgratia:
                rec.remaining = rec.available_exgratia - rec.availed_exgratia
            else:
                raise osv.except_osv(('Error'), ('Available Exgratia should be greater than Availed Exgratia'))

    state = fields.Selection([('approve', 'To Approve'),
                              ('active', 'Active'),
                              ('deactive', 'Deactive')], 'State', default='approve', )
    rule_lines = fields.One2many('contract.salary.rule', 'contract_id', 'Salary Rule')
    contract_id = fields.Many2one('hr.contract', "Contract")
    company_contractor_id = fields.Many2one('res.partner', domain="[('company_contractor','=',True)]",
                                            string="Contract Company", related='employee_id.company_contractor_id')
    employee_leave_ids = fields.One2many('employee.config.leave', 'contract_id', "Leave Types")
    department_id = fields.Many2one('hr.department', "Department", related='employee_id.department_id')
    available_exgratia = fields.Float("Available")
    availed_exgratia = fields.Float("Availed")
    remaining = fields.Float("Remaining", compute='compute_availed')
    overtime_ids = fields.One2many("exgratia.payment", 'contract_id')
    hr_salary_rule = fields.One2many('hr.salary.rule', 'contract_id')

    reference_number = fields.Char()

    emirate_id_no = fields.Char('Emirates ID Number')
    emirate_id_exp = fields.Date('Emirates ID Expiry')
    passport_no = fields.Char('Passport Number')
    passport_expiry = fields.Date('Passport Expiry')
    medical_insurance_no = fields.Char('Medical Insurance Number')
    medical_insurance_exp = fields.Date('Medical Insurance Expiry')

    @api.multi
    def action_active(self):
        for rec in self:
            rec.state = 'active'
            canteen = self.env['contract.salary.rule'].search(
                [('related_type', '=', 'canteen'), ('contract_id', '=', self.id)])
            if canteen:
                rec.employee_id.canteen = True
            esi = self.env['contract.salary.rule'].search([('related_type', '=', 'esi'), ('contract_id', '=', self.id)])
            if esi:
                rec.employee_id.esi = True
            pf = self.env['contract.salary.rule'].search([('related_type', '=', 'pf'), ('contract_id', '=', self.id)])
            if pf:
                rec.employee_id.pf = True

    @api.multi
    def action_deactive(self):
        for rec in self:
            if not rec.date_end:
                raise osv.except_osv(('Error'), ('Please enter the end date of contract.'))
            rec.state = 'deactive'

            rec.employee_id.user_id.active = False
            rec.employee_id.active = False

    @api.model
    def renew_contract(self):
        print "gggggggggggggggggggggggggggggg", self._context.get('active_ids')

    @api.multi
    def action_renew(self):
        for rec in self:
            today_date = (datetime.now()).strftime("%Y-%m-%d")

            if rec.date_end <= today_date:
                if rec.employee_id.active == False:
                    rec.employee_id.active = True
                    rec.employee_id.user_id.active = True
                date_end = datetime.strptime(rec.date_end, "%Y-%m-%d") + timedelta(days=1)

                leaves_list = []
                for leave in rec.employee_leave_ids:
                    leaves_list.append((0, 0, {'leave_id': leave.leave_id.id,
                                               'available': leave.remaining}))

                for monthly_leave in rec.employee_id.monthly_status_ids:
                    monthly_leave.active = False

                month = date_end.month
                self.env['month.leave.status'].create({'status_id': rec.employee_id.id,
                                                       'month_id': month,
                                                       'leave_id': leave.leave_id.id,
                                                       'available': leave.remaining,
                                                       })
                new_contract = {'default_employee_id': rec.employee_id.id,
                                'default_type_id': rec.type_id.id,
                                'default_job_id': rec.job_id.id,
                                'default_wage': rec.wage,
                                'default_date_start': date_end.strftime("%Y-%m-%d"),
                                'default_struct_id': rec.struct_id.id,
                                'default_schedule_pay': rec.schedule_pay,
                                'default_rule_lines': [(6, 0, rec.rule_lines.ids)],
                                'default_notes': rec.notes,
                                'default_contract_id': rec.id,
                                'default_employee_leave_ids': leaves_list}
                return {

                    'view_mode': 'form',

                    'view_type': 'form',
                    'res_model': 'hr.contract',
                    'type': 'ir.actions.act_window',
                    'context': new_contract,
                }
        else:
            raise osv.except_osv(_('Warning!'), _("You can't renew the contract"))

    @api.model
    def create(self, vals):
        res = super(HrContract, self).create(vals)
        latest_contract = self.search([], limit=1, order='id desc')
        res.name = res.employee_id.name + "/" + str(date.today()) + "/" + str(res.id)
        if res.contract_id:
            res.contract_id.state = 'deactive'
        contract = self.env['hr.contract'].search(
            [('employee_id', '=', res.employee_id.id), ('state', '=', 'active')])
        if len(contract) > 1:
            raise osv.except_osv(('Error'), ('There is already exist a active contract for this employee.'));
        return res

    @api.model
    def cron_employee_contract(self):
        for rec in self.env['hr.contract'].search([('active', '=', True)]):
            today_date = datetime.strptime(datetime.now(), "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")
            if rec.date_end < today_date:
                rec.action_deactive()

    @api.model
    def cron_employee_contract_renew(self):
        for rec in self.env['hr.contract'].search([('active', '=', True)]):
            return True


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    hr_salary_rule = fields.Many2one('hr.salary.rule')
    contract_id = fields.Many2one('hr.salary.rule')
    percentage_base = fields.Selection([
        ('basic', 'Basic'),
        ('gross', 'Gross'),
    ], 'Percentage based')
    rule_type = fields.Selection([('Earning', 'Earning'), ('Deduction', 'Deduction')], 'Salary Type')

    @api.depends('labour_emp_contri', 'labour_employer_contri')
    def compute_total_contri(self):
        for rec in self:
            rec.total_contri = rec.labour_emp_contri + rec.labour_employer_contri

    related_type = fields.Selection([('basic', 'Basic'),
                                     ('gross', 'Gross'),
                                     ('canteen', 'canteen'),
                                     ('attendance', 'Attendance'),
                                     ('net', 'Net'),
                                     ('esi', 'ESI'),
                                     ('pf', 'PF'),
                                     ('labour_welfare', 'Labour Welfare'),
                                     ('insurance', 'Insurance'),
                                     ('welfare', 'Welfare Fund'),
                                     ('admin', 'Admin charges'),
                                     ('pt', 'Professional Tax')
                                     ], 'Related Process')
    rule_nature = fields.Selection([('deduction', 'Deduction'),
                                    ('allowance', 'Allowance'),
                                    ], 'Nature Of Rule')
    emloyee_ratio = fields.Float('Employee Contribution %')
    emloyer_ratio = fields.Float('Employer Contribution %')
    ratio = fields.Float('Percentage %')
    salary_limit = fields.Float('ESI Salary Limit')
    pf_sealing_limit = fields.Float('PF Sealing Limit')
    policy_id = fields.Many2one('policy.type', string='Type of Policy')

    employer_epf_ratio = fields.Float('Employer EPF %')
    eps_ratio = fields.Float('EPS %')
    edli_ratio = fields.Float('EDLI %')
    morning_food = fields.Float("Breakfast")
    lunch_food = fields.Float("Lunch")
    snack_food = fields.Float("Snacks")
    dinner_food = fields.Float("Dinner")
    # emp_percent_limit = fields.Float('Employer Percent Limit')
    contribution_line_ids = fields.One2many('contribution.line', 'rule_id', "Contribution Line")
    esi_contribution_line_ids = fields.One2many('esi.contribution.line', 'rule_id', "Contribution Line")
    admin_charges_line_ids = fields.One2many('admin.charges.line', 'rule_id', "Admin Charges Line")
    esi_account_id = fields.Many2one('account.account', string="ESI Account", domain=[('type', '!=', 'view')])
    epf_account_id = fields.Many2one('account.account', string="EPF Account", domain=[('type', '!=', 'view')])
    welfare_account_id = fields.Many2one('account.account', string="Welfare Account", domain=[('type', '!=', 'view')])
    insure_account_id = fields.Many2one('account.account', string="Insurance Account", domain=[('type', '!=', 'view')])
    eps_account = fields.Many2one('account.account', string="EPS Account", domain=[('type', '!=', 'view')])
    admin_charge_account_id = fields.Many2one('account.account', string="Admin Charges Account",
                                              domain=[('type', '!=', 'view')])
    professional_tax_line_ids = fields.One2many('professional.tax.line', 'rule_id', string="Professional Tax ")
    common_account_id = fields.Many2one('account.account', "Debit Account", domain=[('type', '!=', 'view')])
    labour_emp_contri = fields.Float("Employee Contribution")
    labour_employer_contri = fields.Float("Employer Contribution")
    total_contri = fields.Float("Total Contribution", compute='compute_total_contri')
    date_of_deduct = fields.Char("Date of Deduction")
    with_effect_from = fields.Date("With Effect From")
    pf_salary_rule_history_ids = fields.One2many('salary.rule.history', 'rule_id', "Salary Rule History")
    salary_rule_history_ids = fields.One2many('salary.rule.history', 'rule_id', "Salary Rule History")
    admin_charges_line_history_ids = fields.One2many('admin.charges.line.history', 'rule_id', "Admin Charges Line")
    esi_salary_rule_history_ids = fields.One2many('salary.rule.history', 'rule_id', "Salary Rule History")
    labour_welfare_type = fields.Selection([('per', '%'),
                                            ('lumpsum', 'Lumpsum')], string="Type", default='lumpsum')
    labour_celing_limit = fields.Float("Celing Limit")
    labour_welfare_fund_history_ids = fields.One2many('labour.welfare.fund.history', 'rule_id',
                                                      "Labour Welfare Fund History")
    professional_tax_payment_ids = fields.One2many('professional.tax.payment', 'hr_salary_rule_id', "Tax Payment")

    @api.model
    def create(self, vals):
        if vals.get('related_type'):
            rule_obj = self.env['hr.salary.rule'].search(
                [('related_type', '=', vals.get('related_type')), ('related_type', '!=', 'insurance'),
                 ('company_id', '=', vals.get('company_id'))])
            if len(rule_obj) > 0:
                raise osv.except_osv(_('Warning!'), _("There is already a Salary Rule with the same Related Type"))

        return super(HrSalaryRule, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('related_type'):
            rule_obj = self.env['hr.salary.rule'].search(
                [('id', '!=', self.id), ('related_type', '=', vals.get('related_type')),
                 ('related_type', '!=', 'insurance'), ('company_id', '=', self.company_id.id)])
            print 'self---------------------', self.id, self.related_type, rule_obj
            if len(rule_obj) > 0:
                raise osv.except_osv(_('Warning!'), _("There is already a Salary Rule with the same Related Type"))

        return super(HrSalaryRule, self).write(vals)


class ProfessionalTaxPayment(models.Model):
    _name = 'professional.tax.payment'

    payment_month = fields.Selection([('1', 'January'),
                                      ('2', 'February'),
                                      ('3', 'March'),
                                      ('4', 'April'),
                                      ('5', 'May'),
                                      ('6', 'June'),
                                      ('7', 'July'),
                                      ('8', 'August'),
                                      ('9', 'September'),
                                      ('10', 'October'),
                                      ('11', 'November'),
                                      ('12', 'December')], 'Payment Month')

    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")
    month_from = fields.Selection([('January', 'January'),
                                   ('February', 'February'),
                                   ('March', 'March'),
                                   ('April', 'April'),
                                   ('May', 'May'),
                                   ('June', 'June'),
                                   ('July', 'July'),
                                   ('August', 'August'),
                                   ('September', 'September'),
                                   ('October', 'October'),
                                   ('November', 'November'),
                                   ('December', 'December')], 'From')
    month_to = fields.Selection([('January', 'January'),
                                 ('February', 'February'),
                                 ('March', 'March'),
                                 ('April', 'April'),
                                 ('May', 'May'),
                                 ('June', 'June'),
                                 ('July', 'July'),
                                 ('August', 'August'),
                                 ('September', 'September'),
                                 ('October', 'October'),
                                 ('November', 'November'),
                                 ('December', 'December')], 'To')
    hr_salary_rule_id = fields.Many2one('hr.salary.rule', "Salary Rule")


class SalaryRuleHistory(models.Model):
    _name = 'salary.rule.history'

    range_from = fields.Float('HALF YEARLY Income Range From')
    range_to = fields.Float('To')
    tax_amount = fields.Float('HALF YEARLY Professional Tax')
    witheffct_date = fields.Date("With Effect From")
    rule_id = fields.Many2one('hr.salary.rule')
    celing_limit = fields.Float("Celing Limit")
    epf_employee = fields.Float("Employee Contribution EPF (%)")
    epf_employer = fields.Float("Employer Contribution EPF(%)")
    eps_employer = fields.Float("Employer Contribution EPS (%)")
    employee_esi = fields.Float("Employee Contribution ESI (%)")
    employer_esi = fields.Float("Employer Contribution ESI (%)")


class ProfessionalTaxLine(models.Model):
    _name = 'professional.tax.line'

    range_from = fields.Float('HALF YEARLY Income Range From')
    range_to = fields.Float('To')
    tax_amount = fields.Float('HALF YEARLY Professional Tax')
    witheffct_date = fields.Date("With Effect From")
    rule_id = fields.Many2one('hr.salary.rule')


class ESIContributionLine(models.Model):
    _name = 'esi.contribution.line'

    emloyee_ratio = fields.Float('Employee Contribution ESI %')
    emloyer_ratio = fields.Float('Employer Contribution ESI %')

    celing_limit = fields.Float('Celing Limit')
    witheffct_date = fields.Date("With Effect From")
    rule_id = fields.Many2one('hr.salary.rule')


class ContributionLine(models.Model):
    _name = 'contribution.line'

    emloyee_ratio = fields.Float('Employee Contribution EPF %')
    emloyer_ratio = fields.Float('Employer Contribution EPF %')
    emloyer_eps_ratio = fields.Float('Employer Contribution EPS %')
    celing_limit = fields.Float('Celing Limit')
    witheffct_date = fields.Date("With Effect From")
    rule_id = fields.Many2one('hr.salary.rule')


class AdminChargesLine(models.Model):
    _name = 'admin.charges.line'

    type = fields.Selection([('per', '%'), ('lump', 'Lumpsum')], default='per', string="Type")
    name = fields.Char("Name")
    amount = fields.Float("Percentage/Amount")
    witheffct_date = fields.Date("With Effect From")
    rule_id = fields.Many2one('hr.salary.rule')


class AdminChargesLineHistory(models.Model):
    _name = 'admin.charges.line.history'

    type = fields.Selection([('per', '%'), ('lump', 'Lumpsum')], default='per', string="Type")
    name = fields.Char("Name")
    amount = fields.Float("Percentage/Amount")
    witheffct_date = fields.Date("With Effect From")
    rule_id = fields.Many2one('hr.salary.rule')


class LabourWelfareFundHistory(models.Model):
    _name = 'labour.welfare.fund.history'

    type = fields.Selection([('per', '%'), ('lump', 'Lumpsum')], default='per', string="Type")
    labour_emp_contri = fields.Float("Employee Contribution")
    labour_employer_contri = fields.Float("Employer Contribution")

    with_effect_from = fields.Date("With Effect From")
    labour_celing_limit = fields.Float("Ceiling Limit")
    rule_id = fields.Many2one('hr.salary.rule')


class CanteenDaily(models.Model):
    _name = 'canteen.daily'
    _order = "date desc"

    date = fields.Date('Date')
    employee_id = fields.Many2one('hr.employee', 'Employee')
    morning_food = fields.Float("Breakfast")
    lunch_food = fields.Float("Lunch")
    snack_food = fields.Float("Snack")
    dinner_food = fields.Float("Dinner")
    amount = fields.Float('Amount')
    user_id = fields.Many2one('res.users', 'User')


class CanteenEntryWizard(models.TransientModel):
    _name = 'canteen.entry.wizard'

    @api.model
    def default_get(self, default_fields):
        vals = super(CanteenEntryWizard, self).default_get(default_fields)
        line_ids2 = []
        for line in self.env.context.get('active_ids'):
            contract = self.env['hr.contract'].search([('employee_id', '=', line), ('state', '=', 'active')])

            general_config = self.env['hr.salary.rule'].search([('related_type', '=', 'canteen')], limit=1,
                                                               order='id desc')
            # amount = self.env['employee.deduction.line'].search([('employee_id','=',line),('related_type','=','canteen')], limit=1).amount
            values = {
                'employee_id': line,
                'morning_food': general_config.morning_food,
                'lunch_food': general_config.lunch_food,
                'snack_food': general_config.snack_food,
                'dinner_food': general_config.dinner_food,

            }
            line_ids2.append((0, False, values))
            vals['line_ids'] = line_ids2
        return vals

    date = fields.Date('Date', default=fields.Datetime.now())
    line_ids = fields.One2many('canteen.entry.wizard.line', 'wizard_id', 'Employees')
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)

    @api.multi
    def do_mass_update(self):
        for rec in self:
            canteen = self.env['canteen.daily']
            # canteen_account = self.env['general.hr.configuration'].search([], limit=1).canteen_account
            # if not canteen_account:
            # 	raise osv.except_osv(_('Warning!'), _("Please configure canteen Income account"))

            # move_line = self.env['account.move.line']
            # move = self.env['account.move']
            # journal = self.env['account.journal'].sudo().search([('name','=','Miscellaneous Journal')])
            # if not journal:
            # 	raise except_orm(_('Warning'),_('Please Create Journal With name Miscellaneous Journal'))
            # if len(journal) > 1:
            # 	raise except_orm(_('Warning'),_('Multiple Journal with same name(Miscellaneous Journal)'))

            # values = {
            # 		'journal_id': journal.id,
            # 		'date': self.date,
            # 		}
            # move_id = move.create(values)

            # amount = 0
            # name = ""
            for lines in rec.line_ids:
                entry = self.env['canteen.daily'].search(
                    [('employee_id', '=', lines.employee_id.id), ('date', '=', rec.date)])
                if len(entry) != 0:
                    raise osv.except_osv(_('Warning!'), _("Already entered canteen attendance for Employee '%s'") % (
                    lines.employee_id.name,))

                values = {'date': rec.date,
                          'employee_id': lines.employee_id.id,
                          'user_id': rec.user_id.id,
                          'morning_food': lines.morning_food,
                          'lunch_food': lines.lunch_food,
                          'snack_food': lines.snack_food,
                          'dinner_food': lines.dinner_food,
                          'amount': lines.amount}
                canteen.create(values)

    # 	contract = self.env['hr.contract'].search([('employee_id','=',lines.employee_id.id),('state','=','active')])
    # 	if not contract:
    # 		raise osv.except_osv(_('Warning!'), _("No Active contract is created for '%s'") % (lines.employee_id.name,))
    # 	salary_rule = self.env['contract.salary.rule'].search([('related_type','=','canteen'),('contract_id','=',contract.id)])

    # 	if not salary_rule:
    # 		raise osv.except_osv(_('Warning!'), _("No salary rule is defined for type 'canteen' in '%s''s contract") % (lines.employee_id.name,))
    # 	# account = self.env['contract.salary.rule'].search([('contract_id','=',contract.id),('rule_id','=',salary_rule.id)]).account_id
    # 	# print 'test===================',salary_rule
    # 	if not salary_rule.account_id:
    # 		raise osv.except_osv(_('Warning!'), _("No account linked for canteen entry to '%s'") % (lines.employee_id.name,))
    # 	values2 = {
    # 		'account_id': salary_rule.account_id.id,
    # 		'name': 'Canteen Expense',
    # 		'debit': lines.amount,
    # 		'credit': 0,
    # 		'move_id': move_id.id,
    # 		}
    # 	line_id = move_line.create(values2)
    # 	amount += lines.amount
    # 	name += lines.employee_id.name+', '

    # values3 = {
    # 		'account_id': canteen_account.id,
    # 		'name': 'Canteen Collection from ' + name,
    # 		'debit': 0,
    # 		'credit': amount,
    # 		'move_id': move_id.id,
    # 		}
    # line_id = move_line.create(values3)


class CanteenEntryWizardLine(models.TransientModel):
    _name = 'canteen.entry.wizard.line'

    @api.depends('morning_food', 'lunch_food', 'snack_food', 'dinner_food')
    def compute_amount(self):
        for rec in self:
            rec.amount = rec.morning_food + rec.lunch_food + rec.snack_food + rec.dinner_food

    employee_id = fields.Many2one('hr.employee', string='Employees', domain=[('cost_type', '=', 'permanent')])
    morning_food = fields.Float("Breakfast")
    lunch_food = fields.Float("Lunch")
    snack_food = fields.Float("Snack")
    dinner_food = fields.Float("Dinner")
    amount = fields.Float('Amount', compute='compute_amount', store=True)
    wizard_id = fields.Many2one('canteen.entry.wizard', string='Wizard')


class HrESIPayment(models.Model):
    _name = 'hr.esi.payment'

    @api.depends('paid_amount')
    def compute_balance(self):
        for rec in self:
            balance = rec.amount_total - rec.paid_amount
            rec.balance = balance

    date = fields.Date('Date', default=fields.Date.today)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type','in',['cash','bank'])]")
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default="draft")
    month = fields.Selection([('January', 'January'),
                              ('February', 'February'),
                              ('March', 'March'),
                              ('April', 'April'),
                              ('May', 'May'),
                              ('June', 'June'),
                              ('July', 'July'),
                              ('August', 'August'),
                              ('September', 'September'),
                              ('October', 'October'),
                              ('November', 'November'),
                              ('December', 'December')], 'Month')
    line_ids = fields.One2many('esi.payment.line', 'line_id')
    employer_amount = fields.Float('Employer Contribution to ESI', compute="_compute_amount_total", store=True)
    employee_amount = fields.Float('Employee Contribution to ESI', compute="_compute_amount_total", store=True)
    amount_total = fields.Float('Total amount payable ESI', compute="_compute_amount_total", store=True)
    year = fields.Selection([(num, str(num)) for num in range(1900, 2080)], 'Year', default=(datetime.now().year))
    company_contractor_id = fields.Many2one('res.partner', "Contract Company",
                                            domain="[('company_contractor','=',True)]")
    paid_amount = fields.Float("Paid Amount")
    balance = fields.Float("Balance", compute='compute_balance', store=True)

    @api.multi
    @api.depends('line_ids')
    def _compute_amount_total(self):
        for record in self:
            employer_amount = 0
            employee_amount = 0
            for rec in record.line_ids:
                employee_amount += rec.employee_amount
                employer_amount += rec.employer_amount
            record.employee_amount = employee_amount
            record.employer_amount = employer_amount
            record.amount_total = employer_amount + employee_amount

    @api.onchange('month')
    def onchange_esi(self):
        list = []
        self.line_ids = list

        if self.month:
            date = '1 ' + self.month + ' ' + str(datetime.now().year)
            date_from = datetime.strptime(date, '%d %B %Y')
            date_to = date_from + relativedelta(day=31)
            date_from = date_from.date()
            date_to = date_to.date()
            wages_due = 0
            basic = 0
            employee_amount = 0
            employer_amount = 0
            for record in self.env['hr.employee'].search(
                    [('esi', '=', True), ('company_contractor_id', '=', self.company_contractor_id.id)]):

                payroll_info = self.env['employee.payroll.info.line'].search(
                    [('employee_id', '=', record.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to)])
                if payroll_info:
                    wages_due = payroll_info.wages_due
                    basic = payroll_info.basic
                    employee_amount = payroll_info.esi

                    rule = self.env['hr.salary.rule'].search([('related_type', '=', 'esi')], limit=1)
                    rule_contri = self.env['esi.contribution.line'].search(
                        [('rule_id', '=', rule.id)], order='witheffct_date desc', limit=1)
                    esi_wages = 0
                    if basic <= rule_contri.celing_limit:
                        esi_wages = wages_due

                    employer_amount = esi_wages * (
                                (rule_contri.emloyer_ratio + rule_contri.emloyee_ratio) / 100) - employee_amount
                    if esi_wages != 0:
                        values = {
                            'employee_id': record.id,

                            'basic': basic,
                            'wages_due': wages_due,
                            'employee_amount': employee_amount,
                            'employer_amount': round(employer_amount),

                        }
                        list.append((0, False, values))
                self.line_ids = list

    @api.multi
    def button_payment(self):
        print 'z-----------------------------------------------------------'
        move = self.env['account.move']
        move_line = self.env['account.move.line']

        for rec in self:

            if self.env['general.hr.configuration'].search([], limit=1).esi_account.id == False:
                raise osv.except_osv(('Error'), ('Please configure a general account for ESI'));

            values = {
                'journal_id': self.journal_id.id,
                # 'date': rec.date,
            }
            move_id = move.create(values)

            values = {
                'account_id': self.env['general.hr.configuration'].search([], limit=1).esi_account.id,
                'name': 'ESI Payment',
                'debit': self.amount_total,
                'credit': 0,
                'move_id': move_id.id,
            }
            line_id = move_line.create(values)

            values2 = {
                'account_id': self.journal_id.default_credit_account_id.id,
                'name': 'ESI Payment',
                'debit': 0,
                'credit': self.amount_total,
                'move_id': move_id.id,
            }
            line_id = move_line.create(values2)
            move_id.button_validate()
            self.state = 'paid'


class ESIPaymentLine(models.Model):
    _name = 'esi.payment.line'

    line_id = fields.Many2one('hr.esi.payment')
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    attendance = fields.Float('Attendance')
    basic = fields.Float('Basic Pay')
    wages_due = fields.Float('Wages Due')
    employee_amount = fields.Float('Employee Amount')
    employer_amount = fields.Float('Employer Amount')


class PFPayment(models.Model):
    _name = 'pf.payment'

    @api.depends('paid_amount')
    def compute_balance(self):
        for rec in self:
            balance = rec.amount_total - rec.paid_amount
            rec.balance = balance

    date = fields.Date('Date', default=fields.Date.today)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type','in',['cash','bank'])]")
    state = fields.Selection([('draft', 'Draft'), ('paid', 'Paid')], default="draft")
    month = fields.Selection([('January', 'January'),
                              ('February', 'February'),
                              ('March', 'March'),
                              ('April', 'April'),
                              ('May', 'May'),
                              ('June', 'June'),
                              ('July', 'July'),
                              ('August', 'August'),
                              ('September', 'September'),
                              ('October', 'October'),
                              ('November', 'November'),
                              ('December', 'December')], 'Month')
    year = fields.Selection([(num, str(num)) for num in range(1900, 2080)], 'Year', default=(datetime.now().year))
    line_ids = fields.One2many('pf.payment.line', 'line_id')
    employer_amount = fields.Float('Employer Contribution to EPF', compute="_compute_amount_total", store=True)
    employee_amount = fields.Float('Employee Contribution to EPF', compute="_compute_amount_total", store=True)
    eps_amount = fields.Float('Employer Contribution to EPS', compute="_compute_amount_total", store=True)
    edli_amount = fields.Float('Empolyer Contribution to EDLI', compute="_compute_amount_total", store=True)
    amount_total = fields.Float('Total amount payable PF', compute="_compute_amount_total", store=True)
    admin_amount = fields.Float('Administrative Charges', compute="_compute_amount_total", store=True)
    new_admin_amount = fields.Float("Administrative Charges", compute='_compute_amount_total', store=True)
    admin_charges_ids = fields.One2many('admin.charges', 'payment_id', "Administrative charges")
    company_contractor_id = fields.Many2one('res.partner', "Contract Company",
                                            domain="[('company_contractor','=',True)]")
    paid_amount = fields.Float("Paid Amount")
    balance = fields.Float("Balance", compute='compute_balance', store=True)

    @api.multi
    @api.depends('line_ids')
    def _compute_amount_total(self):
        for record in self:
            if record.month:
                date = '1 ' + record.month + ' ' + str(datetime.now().year)

                date_from = datetime.strptime(date, '%d %B %Y')
                date_to = date_from + relativedelta(day=31)
                date_from = date_from.date()
                date_to = date_to.date()
                employer_amount = 0
                employee_amount = 0
                eps_amount = 0
                edli_amount = 0
                pf_wages = 0
                admin_percent = 0
                total_employer_amt = 0
                new_epf = 0
                new_eps = 0
                for rec in record.line_ids:
                    employee_amount += rec.employee_epf

                    pf_wages += rec.pf_wages
                    employer_amount += rec.employer_epf
                    eps_amount += rec.employer_eps
                    if rec.employer_amt_paid_by == 'employer':
                        new_epf += rec.employer_epf
                        new_eps += rec.employer_eps

                record.employee_amount = employee_amount
                record.employer_amount = employer_amount
                record.eps_amount = eps_amount
                record.edli_amount = edli_amount
                amount_total = 0
                rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pf')], limit=1)
                rule_contri = self.env['admin.charges.line'].search(
                    [('rule_id', '=', rule.id), ('witheffct_date', '<=', date_to)],
                    order='witheffct_date desc', limit=6)
                admin_charge_list = []
                for contri in rule_contri:
                    amount = 0
                    if contri.type == 'per':
                        amount = round(pf_wages * (contri.amount / 100))
                    else:
                        amount = round(contri.amount)
                    amount_total += amount
                    admin_charge_dict = {'name': contri.name,
                                         'type': contri.type,
                                         'per_amount': contri.amount,
                                         'amount': amount,
                                         'payment_id': record.id}
                    admin_charge_list.append((0, 0, admin_charge_dict))

                record.admin_charges_ids = admin_charge_list
                total_employer_amt = new_epf + new_eps
                record.amount_total = total_employer_amt + employee_amount + amount_total

    @api.multi
    def button_payment(self):
        print 'z-----------------------------------------------------------'
        move = self.env['account.move']
        move_line = self.env['account.move.line']

        for rec in self:

            if self.env['general.hr.configuration'].search([], limit=1).epf_account.id == False:
                raise osv.except_osv(('Error'), ('Please configure a general account for EPF'));

            values = {
                'journal_id': self.journal_id.id,
                # 'date': rec.date,
            }
            move_id = move.create(values)

            values = {
                'account_id': self.env['general.hr.configuration'].search([], limit=1).epf_account.id,
                'name': 'EPF Payment',
                'debit': self.amount_total,
                'credit': 0,
                'move_id': move_id.id,
            }
            line_id = move_line.create(values)

            values2 = {
                'account_id': self.journal_id.default_credit_account_id.id,
                'name': 'PF Payment',
                'debit': 0,
                'credit': self.amount_total,
                'move_id': move_id.id,
            }
            line_id = move_line.create(values2)
            move_id.button_validate()
            self.state = 'paid'

    @api.onchange('month')
    def onchange_pf(self):
        list = []

        self.line_ids = list

        if self.month:
            date = '1 ' + self.month + ' ' + str(datetime.now().year)

            date_from = datetime.strptime(date, '%d %B %Y')
            date_to = date_from + relativedelta(day=31)
            date_from = date_from.date()
            date_to = date_to.date()
            basic = 0
            pf_wages = 0
            for record in self.env['hr.employee'].search([('esi', '=', True), ]):

                payroll_info = self.env['employee.payroll.info.line'].search(
                    [('employee_id', '=', record.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to)])
                if payroll_info:
                    wages_due = payroll_info.wages_due
                    basic = payroll_info.basic
                    employee_amount = payroll_info.esi

            for record in self.env['hr.employee'].search(
                    [('pf', '=', True), ('company_contractor_id', '=', self.company_contractor_id.id)]):
                employee_payroll_info = self.env['employee.payroll.info.line'].search(
                    [('employee_id', '=', record.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to)])
                if employee_payroll_info:
                    wages_due = employee_payroll_info.wages_due
                    basic = employee_payroll_info.basic
                    rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pf')], limit=1)
                    rule_contri = self.env['contribution.line'].search(
                        [('rule_id', '=', rule.id), ('witheffct_date', '<=', date_to)], order='witheffct_date desc',
                        limit=1)
                    if wages_due <= rule_contri.celing_limit:
                        pf_wages = wages_due
                    if wages_due > rule_contri.celing_limit:
                        pf_wages = rule_contri.celing_limit

                    employee_epf = employee_payroll_info.pf
                    employer_epf = round(pf_wages * rule_contri.emloyer_ratio / 100)
                    employer_eps = employee_payroll_info.pf - round(pf_wages * rule_contri.emloyer_ratio / 100)
                    if pf_wages != 0:
                        values = {
                            'employee_id': record.id,

                            'basic': basic,
                            'wages_due': wages_due,
                            'pf_wages': pf_wages,

                            'employee_epf': employee_epf,
                            'employer_epf': employer_epf,
                            'employer_eps': employer_eps,

                        }
                        list.append((0, False, values))
                self.line_ids = list


class AdminCharges(models.Model):
    _name = 'admin.charges'

    payment_id = fields.Many2one('pf.payment', "PF Payment")
    name = fields.Char("Name")
    per_amount = fields.Float("Percentage/Amount")
    type = fields.Selection([('per', '%'), ('lump', 'Lumpsum')], default='per', string="Type")
    amount = fields.Float("Amount")


class PFPaymentLine(models.Model):
    _name = 'pf.payment.line'

    line_id = fields.Many2one('pf.payment')
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    attendance = fields.Float('Attendance')
    basic = fields.Float('Basic Pay')
    wages_due = fields.Float('Wages Due')
    pf_wages = fields.Float('PF Wages')
    edli = fields.Float('EDLI Amount')
    employee_epf = fields.Float('Employee EPF Amount')
    employer_epf = fields.Float('Employer EPF Amount')
    employer_eps = fields.Float('Employer EPS Amount')
    employer_amt_paid_by = fields.Selection([('employer', 'Paid by employer'),
                                             ('govt', 'Paid by government')
                                             ], string="Employer Percent")


class EmployeeWelfareFund(models.Model):
    _name = 'employee.welfare.fund'

    date = fields.Date('Date', default=fields.Date.today)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type','in',['cash','bank'])]")
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'), ('closed', 'Closed')], default="draft")
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    amount = fields.Float('Released Amount')
    repay_amount = fields.Float('Amount Paid by Employee')
    remarks = fields.Text('Remarks')

    @api.multi
    def button_release(self):
        print 'z-----------------------------------------------------------'
        move = self.env['account.move']
        move_line = self.env['account.move.line']

        for rec in self:

            if self.env['general.hr.configuration'].search([], limit=1).welfare_account.id == False:
                raise osv.except_osv(('Error'), ('Please configure a general account for EPF'));

            values = {
                'journal_id': self.journal_id.id,
                # 'date': rec.date,
            }
            move_id = move.create(values)

            values = {
                'account_id': self.env['general.hr.configuration'].search([], limit=1).welfare_account.id,
                'name': 'Welfare Fund Release',
                'debit': self.amount,
                'credit': 0,
                'move_id': move_id.id,
            }
            line_id = move_line.create(values)

            values2 = {
                'account_id': self.journal_id.default_credit_account_id.id,
                'name': 'Welfare Fund Release',
                'debit': 0,
                'credit': self.amount,
                'move_id': move_id.id,
            }
            line_id = move_line.create(values2)
            move_id.button_validate()
            self.state = 'active'


class GeneralHrConfigurationWizard(models.TransientModel):
    _name = 'general.hr.configuration.wizard'

    @api.onchange('morning_food', 'lunch_food', 'snack_food', 'dinner_food')
    def onchange_food(self):
        for rec in self:
            rec.canteen_amount = rec.morning_food + rec.lunch_food + rec.snack_food + rec.dinner_food

    canteen_account = fields.Many2one('account.account', 'Canteen Account')
    canteen_amount = fields.Float('Canteen Amount')
    morning_food = fields.Float("Morning")
    lunch_food = fields.Float("Lunch")
    snack_food = fields.Float("Snack")
    dinner_food = fields.Float("Dinner")
    esi_payment_date = fields.Integer('Last Date of Payment')
    pf_payment_date = fields.Integer('Last Date of Payment')
    esi_account = fields.Many2one('account.account', 'ESI Account')
    epf_account = fields.Many2one('account.account', 'EPF Account')
    welfare_account = fields.Many2one('account.account', 'Employee Welfare Account')

    pf_extra_ids = fields.One2many('general.hr.configuration.wizard.line', 'line_id')

    fin1_start = fields.Selection([('1', 'January'),
                                   ('2', 'February'),
                                   ('3', 'March'),
                                   ('4', 'April'),
                                   ('5', 'May'),
                                   ('6', 'June'),
                                   ('7', 'July'),
                                   ('8', 'August'),
                                   ('9', 'September'),
                                   ('10', 'October'),
                                   ('11', 'November'),
                                   ('12', 'December'),
                                   ])

    fin1_end = fields.Selection([('1', 'January'),
                                 ('2', 'February'),
                                 ('3', 'March'),
                                 ('4', 'April'),
                                 ('5', 'May'),
                                 ('6', 'June'),
                                 ('7', 'July'),
                                 ('8', 'August'),
                                 ('9', 'September'),
                                 ('10', 'October'),
                                 ('11', 'November'),
                                 ('12', 'December'),
                                 ])
    fin2_start = fields.Selection([('1', 'January'),
                                   ('2', 'February'),
                                   ('3', 'March'),
                                   ('4', 'April'),
                                   ('5', 'May'),
                                   ('6', 'June'),
                                   ('7', 'July'),
                                   ('8', 'August'),
                                   ('9', 'September'),
                                   ('10', 'October'),
                                   ('11', 'November'),
                                   ('12', 'December'),
                                   ])
    fin2_end = fields.Selection([('1', 'January'),
                                 ('2', 'February'),
                                 ('3', 'March'),
                                 ('4', 'April'),
                                 ('5', 'May'),
                                 ('6', 'June'),
                                 ('7', 'July'),
                                 ('8', 'August'),
                                 ('9', 'September'),
                                 ('10', 'October'),
                                 ('11', 'November'),
                                 ('12', 'December'),
                                 ])

    @api.model
    def default_get(self, vals):
        res = super(GeneralHrConfigurationWizard, self).default_get(vals)
        config = self.env['general.hr.configuration'].search([], limit=1)
        line_ids2 = []
        for line in config.pf_extra_ids:
            values = {
                'name': line.name,
                'percent': line.percent
            }
            line_ids2.append((0, False, values))

        res.update({
            'canteen_account': config.canteen_account.id,
            'morning_food': config.morning_food,
            'lunch_food': config.lunch_food,
            'snack_food': config.snack_food,
            'dinner_food': config.dinner_food,
            'canteen_amount': config.morning_food + config.lunch_food + config.snack_food + config.dinner_food,
            'esi_account': config.esi_account.id,
            'epf_account': config.epf_account.id,
            'welfare_account': config.welfare_account.id,
            'esi_payment_date': config.esi_payment_date,
            'pf_payment_date': config.pf_payment_date,
            'fin1_start': config.fin1_start,
            'fin1_end': config.fin1_end,
            'fin2_start': config.fin2_start,
            'fin2_end': config.fin2_end,
            'pf_extra_ids': line_ids2,
        })
        return res

    @api.multi
    def excecute(self):
        # print 'test=========================', asd
        config = self.env['general.hr.configuration'].search([])
        for line in config:
            line.unlink()

        line_ids2 = []
        for line in self.pf_extra_ids:
            values = {
                'name': line.name,
                'percent': line.percent
            }
            line_ids2.append((0, False, values))
        self.env['general.hr.configuration'].create({'canteen_account': self.canteen_account.id,
                                                     'morning_food': self.morning_food,
                                                     'lunch_food': self.lunch_food,
                                                     'snack_food': self.snack_food,
                                                     'dinner_food': self.dinner_food,
                                                     'canteen_amount': self.morning_food + self.lunch_food + self.snack_food + self.dinner_food,
                                                     'esi_account': self.esi_account.id,
                                                     'epf_account': self.epf_account.id,
                                                     'welfare_account': self.welfare_account.id,
                                                     'esi_payment_date': self.esi_payment_date,
                                                     'pf_payment_date': self.pf_payment_date,
                                                     'fin1_start': self.fin1_start,
                                                     'fin1_end': self.fin1_end,
                                                     'fin2_start': self.fin2_start,
                                                     'fin2_end': self.fin2_end,
                                                     'pf_extra_ids': line_ids2
                                                     })

        rule_lines = self.env['contract.salary.rule'].search([('related_type', '=', 'canteen')])
        for rule in rule_lines:
            if rule.contract_id.state != 'deactive':
                rule.is_related = True
                rule.per_day_amount = self.canteen_amount

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.multi
    def cancel(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }


class GeneralHrConfigurationWizardLine(models.TransientModel):
    _name = 'general.hr.configuration.wizard.line'

    line_id = fields.Many2one('general.hr.configuration.wizard')
    name = fields.Char('Name')
    percent = fields.Float('Percentage')


class GeneralHrConfiguration(models.Model):
    _name = 'general.hr.configuration'

    canteen_account = fields.Many2one('account.account', 'Canteen')
    canteen_amount = fields.Float('Canteen Amount')
    morning_food = fields.Float("Morning")
    lunch_food = fields.Float("Lunch")
    snack_food = fields.Float("Snack")
    dinner_food = fields.Float("Dinner")

    esi_account = fields.Many2one('account.account', 'ESI Account')
    pf_payment_date = fields.Integer('Last Date of Payment')
    esi_payment_date = fields.Integer('Last Date of Payment')
    epf_account = fields.Many2one('account.account', 'EPF Account')
    welfare_account = fields.Many2one('account.account', 'Employee Welfare Account')

    fin1_start = fields.Selection([('1', 'January'),
                                   ('2', 'February'),
                                   ('3', 'March'),
                                   ('4', 'April'),
                                   ('5', 'May'),
                                   ('6', 'June'),
                                   ('7', 'July'),
                                   ('8', 'August'),
                                   ('9', 'September'),
                                   ('10', 'October'),
                                   ('11', 'November'),
                                   ('12', 'December'),
                                   ])

    fin1_end = fields.Selection([('1', 'January'),
                                 ('2', 'February'),
                                 ('3', 'March'),
                                 ('4', 'April'),
                                 ('5', 'May'),
                                 ('6', 'June'),
                                 ('7', 'July'),
                                 ('8', 'August'),
                                 ('9', 'September'),
                                 ('10', 'October'),
                                 ('11', 'November'),
                                 ('12', 'December'),
                                 ])
    fin2_start = fields.Selection([('1', 'January'),
                                   ('2', 'February'),
                                   ('3', 'March'),
                                   ('4', 'April'),
                                   ('5', 'May'),
                                   ('6', 'June'),
                                   ('7', 'July'),
                                   ('8', 'August'),
                                   ('9', 'September'),
                                   ('10', 'October'),
                                   ('11', 'November'),
                                   ('12', 'December'),
                                   ])
    fin2_end = fields.Selection([('1', 'January'),
                                 ('2', 'February'),
                                 ('3', 'March'),
                                 ('4', 'April'),
                                 ('5', 'May'),
                                 ('6', 'June'),
                                 ('7', 'July'),
                                 ('8', 'August'),
                                 ('9', 'September'),
                                 ('10', 'October'),
                                 ('11', 'November'),
                                 ('12', 'December'),
                                 ])
    pf_extra_ids = fields.One2many('general.hr.configuration.line', 'line_id')


class GeneralHrConfigurationLine(models.Model):
    _name = 'general.hr.configuration.line'

    line_id = fields.Many2one('general.hr.configuration')
    name = fields.Char('Name')
    percent = fields.Float('Percentage')








