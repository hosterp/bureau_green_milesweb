from openerp import models, fields, api, _
from datetime import datetime,date,timedelta
from dateutil.relativedelta import relativedelta
from openerp import exceptions
from openerp.exceptions import except_orm, ValidationError
import time
import calendar


class Employeelnsurance(models.Model):
	_name = 'employee.insurance'
	_order = 'commit_date desc'
	# _rec_name = 'policy_id'


	@api.constrains('renew_date')
	def check_renew_date(self):
		for rec in self:
			if rec.renew_date < rec.commit_date:
				raise exceptions.ValidationError('Maturity Date should be grater than or equal to Commencement Date')

	@api.constrains('new_renew_date')
	def check_new_renew_date(self):
		for rec in self:
			if rec.new_renew_date < rec.commit_date:
				raise exceptions.ValidationError('Renewal Date should be grater than or equal to Commit Date')


	@api.onchange('renew_date')
	def onchange_renew_date(self):
		for rec in self:
			if rec.renew_date:
				rec.new_renew_date = datetime.strptime(rec.renew_date,"%Y-%m-%d") - timedelta(days=15)

	name = fields.Char('Name', compute="_get_name", store=True)
	employee_id = fields.Many2one('hr.employee', string='Employees', required=True)
	gender = fields.Selection(related="employee_id.gender", string="Gender")
	# qualification = fields.Char('Qualification')
	# techinical_training = fields.Char('Techinical Training')
	# birthday = fields.Date('DOB')
	# age =fields.Char('Age')
	# work_phone = fields.Char('Phone No')
	birthday = fields.Date(related="employee_id.birthday", string="DOB")
	age =fields.Char(related="employee_id.age", string="Age")
	work_phone = fields.Char(related="employee_id.work_phone",string="Phone No")
	# address = fields.Text('Address')
	user_category = fields.Selection(related="employee_id.user_category", string='Employee Category',required=True)
	# designation = fields.Char('Designation')
	# sponsor = fields.Char('Sponsored By')
	# date = fields.Date(string='Date',default=datetime.today(),required=True,readonly=True)
	insurer_id = fields.Many2one('res.partner',string="Insurer",domain="[('is_insurer','=',True)]")
	policy_id = fields.Many2one('policy.type', string='Type of Policy')
	is_company_policy = fields.Boolean(string='Is a company policy?')
	claim_duration = fields.Float(related="policy_id.duration", string='Claim Duration')
	premium_amount = fields.Float(string='Premium Amount')
	emp_paid_amt = fields.Float(string='Amount Paid By Employee')

	comp_contribution = fields.Float(string='Company Contribution')
	empol_contribution = fields.Float(string='Staff Contribution')
	no_of_person = fields.Integer('No of Persons')
	policy_no = fields.Char('Policy No')
	insured_code = fields.Char('Insured Code')
	commit_date = fields.Date('Commencement Date')
	renew_date = fields.Date('Maturity Date')
	new_renew_date = fields.Date("Renewal Date")
	state = fields.Selection([('draft','Draft'),
							('paid','Paid'),
							('closed','Closed')
							], default='draft',string="Status")


	insurance_status = fields.Selection([('draft','Active'),
							('renew','Renewed'),
							('closed','Closed')
							], default='draft', string="Insurance Status")

	payment_mode = fields.Selection([('mly', 'Monthly'),
									 ('qly', 'Quarterly'),
									 ('hly', 'Half Yearly'),
									 ('yly', 'Yearly'),
									 ], 'Payment Mode')

	@api.multi
	@api.depends('policy_id','policy_no','insured_code')
	def _get_name(self):
		for record in self:
			if record.policy_id.name and record.policy_no and record.insured_code:
				record.name = record.policy_id.name + '/' + record.insured_code + '/' + record.policy_no


	@api.multi
	def view_renewal(self):
		if datetime.now() >= datetime.strptime(self.new_renew_date,"%Y-%m-%d"):
			prev_commit_date = datetime.strptime(self.commit_date,"%Y-%m-%d")
			prev_maturity_date = datetime.strptime(self.renew_date,"%Y-%m-%d")
			date_diff = prev_maturity_date - prev_commit_date

			new_commit_date = datetime.strptime(self.renew_date,'%Y-%m-%d') + timedelta(days=1)

			new_renew_date = datetime.strptime(self.renew_date,'%Y-%m-%d') + timedelta(days=(date_diff.days+1))

			new_renewal_date = datetime.strptime(self.renew_date,'%Y-%m-%d') + timedelta(days=(date_diff.days+1)) - timedelta(days=15)
			self.env['employee.insurance'].create({'employee_id': self.employee_id.id,
												'policy_id': self.policy_id.id,
												'insurer_id': self.insurer_id.id,
												   'policy_no':self.policy_no,

												'is_company_policy': self.is_company_policy,
												'premium_amount': self.premium_amount,
												'empol_contribution': self.empol_contribution,
												'comp_contribution': self.comp_contribution,
												'no_of_person': self.no_of_person,
												'insured_code': self.insured_code,
												'commit_date': new_commit_date,
												'renew_date': new_renew_date,
												   'new_renew_date':new_renewal_date,
												})
			self.insurance_status = 'renew'
		else:
			raise exceptions.ValidationError('Insurance Renewal can be done only on or after the Renewal Date')

	@api.multi
	def view_close(self):
		self.insurance_status = 'closed'
		self.state = 'closed'
	
	@api.model
	def _cron_employee_insurance_renewal_pop_up(self):
		prev_popups = self.env['popup.notifications'].search([('emp_insu', '=', True)])
		for popup in prev_popups:
			popup.unlink()
		
		today = date.today()
		
		employees = self.env['hr.employee'].search([])
		for emp in employees:
			
			insurance = self.env['employee.insurance'].search(
				[('employee_id', '=', emp.id), ('insurance_status', '=', 'draft')])
			for insu in insurance:
				insurance_date = datetime.strptime(insu.renew_date, '%Y-%m-%d').date()
				
				
				if insu.renew_date and abs((insurance_date - today).days) <= 15:
					self.env['popup.notifications'].sudo().create({
						'name': self.env.user.id,
						'status': 'draft',
						'emp_insu': True,
						'message': 'Insurance renewal date of' + ' ' + str(emp.name) + ' ' + 'is on' + ' ' + str(
							insurance_date),
					})
			
			


class PolicyType(models.Model):
	_name = 'policy.type'

	name = fields.Char('Policy')
	duration = fields.Float('Duration')
	account_id = fields.Many2one('account.account', string="Account")


class EmployeeInsurancePayment(models.Model):
	_name = 'insurance.policy.payment'

	date = fields.Date('Payment Request Date',default=fields.Date.today)
	payment_ids = fields.One2many('insurance.policy.payment.line','line_id')
	state = fields.Selection([('draft','Draft'),
							('send_approval','Send To Approval'),
							('approved','Approved'),
							('paid','Paid')], default="draft",string="Status")
	policy_id = fields.Many2one('policy.type', string='Type of Policy')

	@api.multi
	def view_action_payment(self):
		amount = 0
		for record  in self.payment_ids:
			amount += record.amount
		res = {
			'name': 'Insurance Payment',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'policy.payment.wizard',
			# 'domain': [('line_id', '=', self.id),('date','=',self.date)],
			# 'res_id': res_id,
			'target': 'new',
			'type': 'ir.actions.act_window',
			'context': {'default_payment_id': self.id,'default_payment_amount': amount},

		}

		return res

	@api.multi
	def view_action_send_approval(self):
		self.state = 'send_approval'

	@api.multi
	def view_action_approve(self):
		self.state = 'approved'



class EmployeeInsurancePaymentLine(models.Model):
	_name = 'insurance.policy.payment.line'

	line_id = fields.Many2one('insurance.policy.payment')
	emp_policy_id = fields.Many2one('employee.insurance', string="Policy No")
	employee_id = fields.Many2one(related="emp_policy_id.employee_id", string='Employee')
	amount = fields.Float(related="emp_policy_id.premium_amount", string='Premium Amount')
	staff_contribution = fields.Float(related='emp_policy_id.empol_contribution',string="Staff Contribution")
	employee_contribution = fields.Float(related='emp_policy_id.comp_contribution',string="Company Contribution")
	insured_code = fields.Char(related="emp_policy_id.insured_code", string='Insured Code')
	commit_date = fields.Date(related="emp_policy_id.commit_date", string='Commencement Date')
	renew_date = fields.Date(related="emp_policy_id.renew_date", string='Maturity Date')
	insurer_id = fields.Many2one('res.partner',related="emp_policy_id.insurer_id", string='Insurer')

	@api.onchange('emp_policy_id')
	def onchange_emp_policy_id(self):
		policy_ids = []
		policy_ids = [policy.id for policy in self.env['employee.insurance'].search([('policy_id','=',self.line_id.policy_id.id)])]
		return {
				'domain': {
					'emp_policy_id': [('id','in',policy_ids)]
				}
			}

	@api.onchange('employee_id')
	def onchange_employee_id(self):
		if self.employee_id:
			self.emp_policy_id = self.env['employee.insurance'].search([('policy_id','=',self.line_id.policy_id.id),('employee_id','=',self.employee_id.id),('state','=','draft'),('insurance_status','=','draft')], order="commit_date asc", limit=1).id

		record = self.env['employee.insurance'].search([('policy_id','=',self.line_id.policy_id.id),('state','=','draft')])
		ids = []
		for item in record:
			ids.append(item.employee_id.id)
		return {'domain': {'employee_id': [('id', 'in', ids)]}}

class EmployeeClaim(models.Model):
	_name = 'insurance.policy.claim'

	date = fields.Date('Claim Submission Date',default=fields.Date.today)
	emp_policy_id = fields.Many2one('employee.insurance', string="Policy")
	employee_id = fields.Many2one(related="emp_policy_id.employee_id", string='Employee')
	insurer_id = fields.Many2one('res.partner',related="emp_policy_id.insurer_id", string='Insurer')
	insured_code = fields.Char(related="emp_policy_id.insured_code", string='Insured No')
	commit_date = fields.Date(related="emp_policy_id.commit_date", string='Commencement Date')
	renew_date = fields.Date(related="emp_policy_id.renew_date", string='Maturity Date')
	employee_claim_amount = fields.Float(string="Employee Claim amount",related='emp_policy_id.premium_amount')
	state = fields.Selection([('draft','draft'),
							('active','Active'),
							('claim_request','Pending'),
							('claim_release','Closed')
							], default='draft')
	amount_paid = fields.Float(string='Amount Paid To Employee', compute="_compute_paid_amount")
	requested_claim_amount = fields.Float(string='Requested Claim Amount')
	released_claim_amount = fields.Float(string='Released Claim Amount')
	claim_received_date = fields.Date("Claim Received Date")
	claim_asset_account_id = fields.Many2one('account.account', string="Employee Claim Refund Account")
	company_expense_account_id = fields.Many2one('account.account', string="Company Expense Account Account")
	payment_ids = fields.One2many('claim.payment.wizard', 'claim_id', string="Payments To Employee")


	@api.multi
	@api.depends('payment_ids')
	def _compute_paid_amount(self):
		for record in self:
			amount = 0
			for rec in record.payment_ids:
				amount += rec.amount_paid
			record.amount_paid = amount

	@api.onchange('employee_id')
	def onchange_employee_id(self):
		if self.employee_id:
			self.emp_policy_id = self.env['employee.insurance'].search([('employee_id','=',self.employee_id.id),('state','=','paid')], order="commit_date asc", limit=1).id

		record = self.env['employee.insurance'].search([('state','=','paid')])
		ids = []
		for item in record:
			ids.append(item.employee_id.id)
		return {'domain': {'employee_id': [('id', 'in', ids)]}}


	@api.multi
	def view_action_payment(self):
		# 

		res = {
			'name': 'Claim Amount Payment To Employee',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'claim.payment.wizard',
			# 'domain': [('line_id', '=', self.id),('date','=',self.date)],
			# 'res_id': res_id,
			'target': 'new',
			'type': 'ir.actions.act_window',
			'context': {'default_claim_id': self.id,
						# 'default_amount_paid': self.amount_paid,
						'default_claim_asset_account_id': self.claim_asset_account_id.id,
						},

		}

		return res

	@api.multi
	def button_claim_request(self):
		self.state = 'claim_request'



	@api.multi
	def button_claim_release(self):
		for rec in self:
			rec.state = 'claim_release'
		return True


class EmployeeClaimPaymentWizard1(models.Model):
	_name = 'claim.payment.wizard'

	date = fields.Date('Date',default=fields.Date.today)
	claim_id = fields.Many2one('insurance.policy.claim')
	payment_mode = fields.Many2one('account.journal', string="Mode of Payment", domain=[('type','in',['cash','bank'])])
	claim_asset_account_id = fields.Many2one('account.account', string="Employee Claim Refund Account")
	amount_paid = fields.Float(string='Maximum Claim Amount')

	@api.multi
	def button_payment(self):
		self.claim_id.state = 'active'
		# self.claim_id.amount_paid = self.amount_paid
		# self.claim_id.claim_asset_account_id = self.claim_asset_account_id.id
		move = self.env['account.move']
		move_line = self.env['account.move.line']
		
		move_id = move.create({
							'journal_id': self.payment_mode.id,
							'date': datetime.now(),
							})
		# print 'account---------------------', self.payment_mode.default_credit_account_id.id, self.payment_id.policy_id.account_id.id
		
		line_id = move_line.create({
								'account_id': self.payment_mode.default_credit_account_id.id,
								'name': 'Claim Amount',
								'credit': self.amount_paid,
								'debit': 0,
								'move_id': move_id.id,
								})
			
		line_id = move_line.create({
								'account_id': self.claim_asset_account_id.id,
								'name': 'Claim Amount',
								'credit': 0,
								'debit': self.amount_paid,
								'move_id': move_id.id,
								})
		move_id.button_validate()


class EmployeeClaimReleaseWizard(models.TransientModel):
	_name = 'claim.release.wizard'

	date = fields.Date('Date',default=fields.Date.today)
	claim_id = fields.Many2one('insurance.policy.claim')
	payment_mode = fields.Many2one('account.journal', string="Mode of Payment", domain=[('type','in',['cash','bank'])])
	released_claim_amount = fields.Float(string='Released Claim Amount')
	company_expense_account_id = fields.Many2one('account.account', string="Company Expense Account Account")

	@api.multi
	def button_release(self):
		self.claim_id.state = 'claim_release'
		self.claim_id.released_claim_amount = self.released_claim_amount
		self.claim_id.company_expense_account_id = self.company_expense_account_id.id
		move = self.env['account.move']
		move_line = self.env['account.move.line']
		
		move_id = move.create({
							'journal_id': self.payment_mode.id,
							'date': datetime.now(),
							})
		# print 'account---------------------', self.payment_mode.default_credit_account_id.id, self.payment_id.policy_id.account_id.id
		
		line_id = move_line.create({
								'account_id': self.payment_mode.default_credit_account_id.id,
								'name': 'Released Claim Amount',
								'debit': self.released_claim_amount,
								'credit': 0,
								'move_id': move_id.id,
								})
			
		line_id = move_line.create({
								'account_id': self.claim_id.claim_asset_account_id.id,
								'name': 'Claim Amount',
								'credit': self.claim_id.amount_paid,
								'debit': 0,
								'move_id': move_id.id,
								})
		print 'z----------------------------------', self.released_claim_amount, self.claim_id.amount_paid
		if self.released_claim_amount < self.claim_id.amount_paid:
			print 'z1111-------------------', self.claim_id.amount_paid - self.released_claim_amount
			line_id = move_line.create({
									'account_id': self.company_expense_account_id.id,
									'name': 'Claim Amount',
									'credit': 0,
									'debit': self.claim_id.amount_paid - self.released_claim_amount,
									'move_id': move_id.id,
									})
		move_id.button_validate()


class EmployeeInsurancePaymentWizard(models.Model):
	_name = 'policy.payment.wizard'

	date = fields.Date('Date',default=fields.Date.today)
	payment_id = fields.Many2one('insurance.policy.payment')
	payment_mode = fields.Many2one('account.journal', string="Mode of Payment", domain=[('type','in',['cash','bank'])])
	payment_amount = fields.Float('Payment Amount')


	@api.multi
	def button_payment(self):
		self.payment_id.state = 'paid'
		move = self.env['account.move']
		move_line = self.env['account.move.line']
		
		move_id = move.create({
							'journal_id': self.payment_mode.id,
							'date': datetime.now(),
							})
		print 'account---------------------', self.payment_mode.default_credit_account_id.id, self.payment_id.policy_id.account_id.id
		
		line_id = move_line.create({
								'account_id': self.payment_mode.default_credit_account_id.id,
								'name': 'Insurance Amount',
								'credit': self.payment_amount,
								'debit': 0,
								'move_id': move_id.id,
								})
			
		line_id = move_line.create({
								'account_id': self.payment_id.policy_id.account_id.id,
								'name': 'Insurance Amount',
								'credit': 0,
								'debit': self.payment_amount,
								'move_id': move_id.id,
								})
		move_id.button_validate()

		for record in self.payment_id.payment_ids:
			if record.emp_policy_id.renew_date:


				record.emp_policy_id.write({'state':'paid'})











class ManagementPolicy(models.Model):
	_name = 'management.policy'
	
	
	@api.onchange('remittance_date')
	def onchange_remittance_date(self):
		for rec in self:
			if rec.remittance_date:
				rec.maturity_date = datetime.strptime(rec.remittance_date,"%Y-%m-%d") - timedelta(days=30)

	@api.constrains('maturity_date')
	def check_maturity_date(self):
		for rec in self:
			if rec.commencement_date > rec.maturity_date:
				raise exceptions.ValidationError('Maturity Date should be grater than or equal to Commencement Date')

	@api.constrains('remittance_date')
	def check_remittance_date(self):
		for rec in self:
			if rec.commencement_date > rec.remittance_date:
				raise exceptions.ValidationError('Last Remittance Date should be grater than or equal to Commencement Date')

	# name = fields.Char('Policy')
	name = fields.Char('Name', compute="_get_name")
	res_company_id = fields.Many2one('res.partner', string='Policy Holder',domain="[('company_contractor','=',True)]")
	policy_type_id = fields.Many2one('management.policy.type', 'Policy Type')
	is_money_back_policy = fields.Boolean(related="policy_type_id.is_money_back_policy", string='Is a money back policy?')
	# insurance_company_id = fields.Many2one('insurance.company', 'Company Name')
	account_id = fields.Many2one('account.account', string="Account")
	policy_no = fields.Char('Policy No')
	commencement_date = fields.Date('Commencement Date')
	remittance_date = fields.Date('Last Remittance Date')
	maturity_date = fields.Date('Maturity Date')
	payment_mode = fields.Selection([('mly','Monthly'),
									('qly','Quarterly'),
									('hly','Half Yearly'),
									('yly','Yearly'),
									],'Payment Mode')
	sum_assured = fields.Float('Sum Assured')
	premium_amount = fields.Float('Premium Amount')
	remarks = fields.Text('Remarks')
	payment_ids = fields.One2many('management.policy.line','line_id')
	state = fields.Selection([('draft','Draft'),
							('active','Active'),
							('surrender','Surrender'),
							('matured','Matured'),
							('release','Released'),
							], default='draft',string="Status")
	released_sum_assured = fields.Float("Released Sum Assurance")
	released_survival_benefit = fields.Float('Survival Benefit')
	released_amount = fields.Float('Total Released Amount')
	released_payment_mode = fields.Many2one('account.journal', string="Mode of Payment", domain=[('type','in',['cash','bank'])])
	survival_benefit_account_id = fields.Many2one('account.account', string="Survival Benefit Account")

	mn_ids = fields.One2many('management.policy.money_back','payment_id', domain=[('state','=','released')])

	@api.multi
	def _get_name(self):
		for record in self:
			if record.policy_type_id.name and record.policy_no:
				record.name = record.policy_type_id.name + '-' + record.policy_no


	@api.model
	def _cron_manag_policy_maturity_entries(self):
		print 'f3333333333333333333333ggggggggggggggggggggggggggggggggggggg', fields.Date.today()
		date_today = fields.Date.today()
		for day in self.env['management.policy'].search([('maturity_date','=',date_today)]):
			print 'day1------------------', day, day.state
			day.write({'state':'matured'})
			print 'day2------------------', day, day.state
	
	
					
	@api.multi
	def button_active(self):
		for rec in self:
			rec.state = 'active'
			date_diff = datetime.strptime(rec.remittance_date,"%Y-%m-%d") - datetime.strptime(rec.commencement_date,"%Y-%m-%d")
			year1 = datetime.strptime(rec.remittance_date,"%Y-%m-%d").year
			year2 = datetime.strptime(rec.commencement_date,"%Y-%m-%d").year
			diff_year = year1 - year2
			month1 = datetime.strptime(rec.remittance_date,"%Y-%m-%d").month
			month2 = datetime.strptime(rec.commencement_date,"%Y-%m-%d").month
			diff_month = month1 - month2
			months = diff_month +  (diff_year*12)
			payment_date = datetime.strptime(rec.commencement_date, "%Y-%m-%d")
			if rec.payment_mode == 'mly':
				for mon in range(months+1):

					days_in_month = calendar.monthrange(payment_date.year, payment_date.month)[1]

					self.env['management.policy.line'].create({'line_id':rec.id,
															   'date':payment_date,
															   'res_company_id':rec.res_company_id.id,
															   'premium_amount':rec.premium_amount,
															   })

					payment_date = payment_date + timedelta(days=days_in_month)
			elif rec.payment_mode == 'qly':
				months = months/3
				for mon in range(months):


					self.env['management.policy.line'].create({'line_id':rec.id,
															   'date':datetime.strptime(rec.commencement_date,"%Y-%m-%d") + timedelta(days=90),
															   'res_company_id':rec.res_company_id.id,
															   'premium_amount': rec.premium_amount,
															   })
			elif rec.payment_mode == 'hly':
				months = months/6
				for mon in range(months):


					self.env['management.policy.line'].create({'line_id':rec.id,
															   'date':datetime.strptime(rec.commencement_date,"%Y-%m-%d") + timedelta(days=180),
															   'res_company_id':rec.res_company_id.id,
															   'premium_amount': rec.premium_amount,
															   })
			else:
				months = months/12
				for mon in range(months):


					self.env['management.policy.line'].create({'line_id':rec.id,
															   'date':datetime.strptime(rec.commencement_date,"%Y-%m-%d") + timedelta(days=365),
															   'res_company_id':rec.res_company_id.id,
															   'premium_amount': rec.premium_amount,
															   })



			# if rec.payment_mode == 'mly':
			#
			# self.env['']

	@api.multi
	def view_action_payment(self):
		# 

		res = {
			'name': 'Management Policy Release',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'management.policy.release.wizard',
			# 'domain': [('line_id', '=', self.id),('date','=',self.date)],
			# 'res_id': res_id,
			'target': 'new',
			'type': 'ir.actions.act_window',
			'context': {'default_payment_id': self.id, 'default_sum_assured': self.sum_assured},

		}

		return res

	@api.multi
	def view_action_surrender(self):
		# 

		res = {
			'name': 'Management Policy Surrender',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'management.policy.release.wizard',
			# 'domain': [('line_id', '=', self.id),('date','=',self.date)],
			# 'res_id': res_id,
			'target': 'new',
			'type': 'ir.actions.act_window',
			'context': {'default_payment_id': self.id},

		}

		return res

	@api.multi
	def view_action_mn(self):
		# 

		res = {
			'name': 'Management Policy Surrender',
			'view_type': 'form',
			'view_mode': 'form',
			'res_model': 'management.policy.money_back',
			# 'domain': [('line_id', '=', self.id),('date','=',self.date)],
			# 'res_id': res_id,
			'target': 'new',
			'type': 'ir.actions.act_window',
			'context': {'default_payment_id': self.id},

		}

		return res




class ManagementPolicyMnWizard(models.Model):
	_name = 'management.policy.money_back'

	payment_id = fields.Many2one('management.policy')
	date = fields.Date('Date',default=fields.Date.today)
	payment_mode = fields.Many2one('account.journal', string="Mode of Payment", domain=[('type','in',['cash','bank'])])
	payment_amount = fields.Float('Released Amount')
	state = fields.Selection([('draft','Draft'),('released','Released')], default="draft")
	# survival_benefit_account_id = fields.Many2one('account.account', string="Survival Benefit Account")

	


	@api.multi
	def button_policy_money_back(self):
		self.state = 'released'
		move = self.env['account.move']
		move_line = self.env['account.move.line']
		
		move_id = move.create({
							'journal_id': self.payment_mode.id,
							'date': datetime.now(),
							})
		# print 'account---------------------', self.payment_mode.default_credit_account_id.id, self.payment_id.policy_type_id.account_id.id
		
		line_id = move_line.create({
								'account_id': self.payment_mode.default_credit_account_id.id,
								'name': 'Insurance Amount',
								'debit': self.payment_amount,
								'credit': 0,
								'move_id': move_id.id,
								})
			
		line_id = move_line.create({
								'account_id': self.payment_id.account_id.id,
								'name': 'Sum Assured',
								'debit': 0,
								'credit': self.payment_amount,
								'move_id': move_id.id,
								})
		
		move_id.button_validate()




class ManagementPolicyReleaseWizard(models.Model):
	_name = 'management.policy.release.wizard'

	date = fields.Date('Date',default=fields.Date.today)
	payment_amount = fields.Float('Released Amount')
	payment_id = fields.Many2one('management.policy')
	sum_assured = fields.Float('Sum Assured')
	survival_benefit = fields.Float('Survival Benefit')
	payment_mode = fields.Many2one('account.journal', string="Mode of Payment", domain=[('type','in',['cash','bank'])])
	survival_benefit_account_id = fields.Many2one('account.account', string="Survival Benefit Account")

	@api.onchange('payment_amount')
	def onchange_amount(self):
		amount = 0
		money_back_amt = 0
		for rec in self.payment_id.payment_ids:
			if rec.state == 'paid':
				amount += rec.premium_amount
		self.sum_assured = amount
		self.survival_benefit = self.payment_amount - amount

		# if self.payment_id.is_money_back_policy == True:
		# 	for vals in self.payment_id.mn_ids:
		# 		money_back_amt += vals.payment_amount
		# 	self.sum_assured = amount
		# 	self.survival_benefit = self.payment_amount - (amount - money_back_amt)
		# else:
		# 	self.sum_assured = amount
		# 	self.survival_benefit = self.payment_amount - amount


	@api.multi
	def button_policy_release(self):
		if self.payment_id.state == 'active':
			self.payment_id.state = 'surrender'
		if self.payment_id.state == 'matured':
			self.payment_id.state = 'release'
		self.payment_id.released_sum_assured = self.sum_assured
		self.payment_id.released_survival_benefit = self.survival_benefit
		self.payment_id.released_amount = self.payment_amount
		self.payment_id.released_payment_mode = self.payment_mode
		self.payment_id.survival_benefit_account_id = self.survival_benefit_account_id
		move = self.env['account.move']
		move_line = self.env['account.move.line']
		
		move_id = move.create({
							'journal_id': self.payment_mode.id,
							'date': datetime.now(),
							})
		# print 'account---------------------', self.payment_mode.default_credit_account_id.id, self.payment_id.policy_type_id.account_id.id
		
		line_id = move_line.create({
								'account_id': self.payment_mode.default_credit_account_id.id,
								'name': 'Insurance Amount',
								'debit': self.payment_amount,
								'credit': 0,
								'move_id': move_id.id,
								})
			
		line_id = move_line.create({
								'account_id': self.payment_id.account_id.id,
								'name': 'Sum Assured',
								'debit': 0,
								'credit': self.sum_assured,
								'move_id': move_id.id,
								})
		if self.survival_benefit != False:
			line_id = move_line.create({
									'account_id': self.survival_benefit_account_id.id,
									'name': 'Survival Benefit',
									'debit': 0,
									'credit': self.survival_benefit,
									'move_id': move_id.id,
								})
		move_id.button_validate()

	


		

class ManagementPolicyLine(models.Model):
	_name = 'management.policy.line'

	line_id = fields.Many2one('management.policy', string="Policy No.")
	date = fields.Date('Payment Date')
	premium_amount = fields.Float('Premium Amount')
	payment_mode = fields.Many2one('account.journal', string="Mode of Payment", domain=[('type','in',['cash','bank'])])
	state = fields.Selection([('draft','draft'),
							('paid','Paid')
							], default='draft')	
	account_id = fields.Many2one('account.account', related="line_id.account_id", string="Account")
	res_company_id = fields.Many2one('res.partner',domain="[('contractor', '=', True)]", related="line_id.res_company_id", string='Policy Holder')
	policy_type_id = fields.Many2one('management.policy.type', related="line_id.policy_type_id", string= 'Policy Type')
	policy_no = fields.Char( related="line_id.policy_no", string='Policy No')
	commencement_date = fields.Date( related="line_id.commencement_date", string='Commencement Date')
	remittance_date = fields.Date( related="line_id.remittance_date", string='Last Remittance Date')
	maturity_date = fields.Date( related="line_id.maturity_date", string='Maturity Date')
	payment_duration = fields.Selection([('mly','Monthly'),
									('qly','Quarterly'),
									('hly','Half Yearly'),
									('yly','Yearly'),
									], related="line_id.payment_mode", string='Payment Mode')
	sum_assured = fields.Float( related="line_id.sum_assured", string='Sum Assured')


	@api.multi
	def button_payment(self):
		self.state = 'paid'
		move = self.env['account.move']
		move_line = self.env['account.move.line']
		
		move_id = move.create({
							'journal_id': self.payment_mode.id,
							'date': datetime.now(),
							})
		line_id = move_line.create({
								'account_id': self.payment_mode.default_credit_account_id.id,
								'name': 'Insurance Amount',
								'credit': self.premium_amount,
								'debit': 0,
								'move_id': move_id.id,
								})
			
		line_id = move_line.create({
								'account_id': self.account_id.id,
								'name': 'Insurance Amount',
								'credit': 0,
								'debit': self.premium_amount,
								'move_id': move_id.id,
								})
		move_id.button_validate()





	@api.model
	def _cron_monthly_manag_policy_entries(self):
		print 'f11111111111111111111111gggggggggggggggggggggggg'
		for day in self.env['management.policy'].search([('payment_mode','=','mly'),('state','=','active')]):
			lines = self.env['management.policy.line'].search([('line_id','=', day.id)])
			if lines:
				date = self.env['management.policy.line'].search([('line_id','=', day.id)])[-1].date
			else:
				date = day.commencement_date

			day3 = time.strftime("%A", time.strptime(date, "%Y-%m-%d"))
			month =  datetime.strptime(date, "%Y-%m-%d").month

			date_start_dt = fields.Datetime.from_string(date)
			dt = date_start_dt + relativedelta(months=1)
			new_date = fields.Datetime.to_string(dt)
			
			print 'newdate11111111111111111111============================', new_date
			 
			self.env['management.policy.line'].create({'line_id':day.id,'date':new_date, 'premium_amount':day.premium_amount,'state':'draft'})


			
	@api.model
	def _cron_quarterly_manag_policy_entries(self):
		print 'f222222222222222222gggggggggggggggggggggggggggggggg'
		for day in self.env['management.policy'].search([('payment_mode','=','qly'),('state','=','active')]):
			lines = self.env['management.policy.line'].search([('line_id','=', day.id)])
			if lines:
				date = self.env['management.policy.line'].search([('line_id','=', day.id)])[-1].date
			else:
				date = day.commencement_date

			day3 = time.strftime("%A", time.strptime(date, "%Y-%m-%d"))
			month =  datetime.strptime(date, "%Y-%m-%d").month

			date_start_dt = fields.Datetime.from_string(date)
			dt = date_start_dt + relativedelta(months=3)
			new_date = fields.Datetime.to_string(dt)
			
			print 'newdate222222222222222222===============================', new_date

			 
			self.env['management.policy.line'].create({'line_id':day.id,'date':new_date, 'premium_amount':day.premium_amount,'state':'draft'})




	@api.model
	def _cron_half_yearly_manag_policy_entries(self):
		print 'f3333333333333333333333ggggggggggggggggggggggggggggggggggggg'
		for day in self.env['management.policy'].search([('payment_mode','=','hly'),('state','=','active')]):
			lines = self.env['management.policy.line'].search([('line_id','=', day.id)])
			if lines:
				date = self.env['management.policy.line'].search([('line_id','=', day.id)])[-1].date
			else:
				date = day.commencement_date

			day3 = time.strftime("%A", time.strptime(date, "%Y-%m-%d"))
			month =  datetime.strptime(date, "%Y-%m-%d").month

			date_start_dt = fields.Datetime.from_string(date)
			dt = date_start_dt + relativedelta(months=6)
			new_date = fields.Datetime.to_string(dt)
			
			print 'newdate333333333333333333333=====================', new_date


			self.env['management.policy.line'].create({'line_id':day.id,'date':new_date, 'premium_amount':day.premium_amount,'state':'draft'})



	@api.model
	def _cron_yearly_manag_policy_entries(self):
		print 'f44444444444444444444444yyyyyyyyyyyyyyyyyyyy'
		for day in self.env['management.policy'].search([('payment_mode','=','yly'),('state','=','active')]):
			lines = self.env['management.policy.line'].search([('line_id','=', day.id)])
			if lines:
				date = self.env['management.policy.line'].search([('line_id','=', day.id)])[-1].date
			else:
				date = day.commencement_date

			day3 = time.strftime("%A", time.strptime(date, "%Y-%m-%d"))
			month =  datetime.strptime(date, "%Y-%m-%d").month

			date_start_dt = fields.Datetime.from_string(date)
			dt = date_start_dt + relativedelta(months=12)
			new_date = fields.Datetime.to_string(dt)
			
			print 'newdate444444444444444444444[[[]]]]]]]]]]]', new_date
			 
			self.env['management.policy.line'].create({'line_id':day.id,'date':new_date, 'premium_amount':day.premium_amount,'state':'draft'})





class ManagementPolicyClaim(models.Model):
	_name = 'management.policy.claim'

	date = fields.Date("Claim Submission Date")
	management_policy_id = fields.Many2one('management.policy',"Management Policy")
	policy_holder_id = fields.Many2one('res.partner',"Policy Holder",related='management_policy_id.res_company_id')
	commit_date = fields.Date(string="Commencement Date",related='management_policy_id.commencement_date')
	remittance_date = fields.Date(string="Remittance Date",related='management_policy_id.remittance_date')
	maturity_date = fields.Date(string="Maturity Date",related='management_policy_id.maturity_date')
	claim_amount = fields.Float(string="Claim Amount")
	state = fields.Selection([('draft','Draft'),
							  ('pending','Pending'),
							  ('closed','Closed')],string="Status",default='draft')
	claim_received_date = fields.Date("Claim Received Date")
	claim_received_amt = fields.Float("Claim Received Amount")


	@api.multi
	def action_claim_request(self):
		for rec in self:
			rec.state = 'pending'
		return True

	@api.multi
	def action_claim_receive(self):
		for rec in self:
			rec.claim_received_date = fields.datetime.now()
			rec.state = 'closed'
		return True

class ManagementPolicyType(models.Model):
	_name = 'management.policy.type'

	name = fields.Char('Insurance Company')
	is_money_back_policy = fields.Boolean('Is a money back policy?', default=False)
