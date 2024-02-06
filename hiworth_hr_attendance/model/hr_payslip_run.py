from openerp import models, fields, api, _
from datetime import datetime , timedelta
from openerp.osv import osv
from openerp import tools


class Number2Words(object):


        def __init__(self):
            '''Initialise the class with useful data'''

            self.wordsDict = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
                              8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen',
                              14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen',
                              18: 'eighteen', 19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty',
                              50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninty' }

            self.powerNameList = ['thousand', 'lac', 'crore']


        def convertNumberToWords(self, number):

            # Check if there is decimal in the number. If Yes process them as paisa part.
            formString = str(number)
            if formString.find('.') != -1:
                withoutDecimal, decimalPart = formString.split('.')

                paisaPart =  str(round(float(formString), 2)).split('.')[1]
                inPaisa = self._formulateDoubleDigitWords(paisaPart)

                formString, formNumber = str(withoutDecimal), int(withoutDecimal)
            else:
                # Process the number part without decimal separately
                formNumber = int(number)
                inPaisa = None

            if not formNumber:
                return 'zero'

            self._validateNumber(formString, formNumber)

            inRupees = self._convertNumberToWords(formString)

            if inPaisa:
                return '%s and %s paisa' % (inRupees.title(), inPaisa.title())
            else:
                return '%s' % inRupees.title()


        def _validateNumber(self, formString, formNumber):

            assert formString.isdigit()

            # Developed to provide words upto 999999999
            if formNumber > 999999999 or formNumber < 0:
                raise AssertionError('Out Of range')


        def _convertNumberToWords(self, formString):

            MSBs, hundredthPlace, teens = self._getGroupOfNumbers(formString)

            wordsList = self._convertGroupsToWords(MSBs, hundredthPlace, teens)

            return ' '.join(wordsList)


        def _getGroupOfNumbers(self, formString):

            hundredthPlace, teens = formString[-3:-2], formString[-2:]

            msbUnformattedList = list(formString[:-3])

            #---------------------------------------------------------------------#

            MSBs = []
            tempstr = ''
            for num in msbUnformattedList[::-1]:
                tempstr = '%s%s' % (num, tempstr)
                if len(tempstr) == 2:
                    MSBs.insert(0, tempstr)
                    tempstr = ''
            if tempstr:
                MSBs.insert(0, tempstr)

            #---------------------------------------------------------------------#

            return MSBs, hundredthPlace, teens


        def _convertGroupsToWords(self, MSBs, hundredthPlace, teens):

            wordList = []

            #---------------------------------------------------------------------#
            if teens:
                teens = int(teens)
                tensUnitsInWords = self._formulateDoubleDigitWords(teens)
                if tensUnitsInWords:
                    wordList.insert(0, tensUnitsInWords)

            #---------------------------------------------------------------------#
            if hundredthPlace:
                hundredthPlace = int(hundredthPlace)
                if not hundredthPlace:
                    # Might be zero. Ignore.
                    pass
                else:
                    hundredsInWords = '%s hundred' % self.wordsDict[hundredthPlace]
                    wordList.insert(0, hundredsInWords)

            #---------------------------------------------------------------------#
            if MSBs:
                MSBs.reverse()

                for idx, item in enumerate(MSBs):
                    inWords = self._formulateDoubleDigitWords(int(item))
                    if inWords:
                        inWordsWithDenomination = '%s %s' % (inWords, self.powerNameList[idx])
                        wordList.insert(0, inWordsWithDenomination)

            #---------------------------------------------------------------------#
            return wordList


        def _formulateDoubleDigitWords(self, doubleDigit):

            if not int(doubleDigit):
                # Might be zero. Ignore.
                return None
            elif self.wordsDict.has_key(int(doubleDigit)):
                # Global dict has the key for this number
                tensInWords = self.wordsDict[int(doubleDigit)]
                return tensInWords
            else:
                doubleDigitStr = str(doubleDigit)
                tens, units = int(doubleDigitStr[0])*10, int(doubleDigitStr[1])
                tensUnitsInWords = '%s %s' % (self.wordsDict[tens], self.wordsDict[units])
                return tensUnitsInWords

class HRPayslipBatches(models.Model):
	_name = 'hr.payslip.batches'

	@api.onchange('contract_company_id')
	def onchange_contract_company_id(self):
		for rec in self:
			basic_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'basic')], limit=1)
			attend_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'attendance')], limit=1)
			pf_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pf')], limit=1)
			employee_list = self.env['hr.employee'].search([('company_contractor_id','=',rec.contract_company_id.id)])
			value_list = []
			rule_list = []


	@api.multi
	def unlink(self):
		# for rec in self:
			# if rec.state in ['verify','approve','payment','paid']:
			# 	raise osv.except_osv(_('Warning!'),
			# 						 _("Payslip Record Can'tbe deleted from an approval stage") % (lines.employee_id.name,))
			#
		return super(HRPayslipBatches, self).unlink()

	contract_company_id = fields.Many2one('res.partner',domain="[('company_contractor','=',True)]",string="Contract Company")
	date_from = fields.Date("Period From")
	date_to = fields.Date("To")
	payslip_batches_line_ids = fields.One2many('hr.payslip.batches.line','payslip_batches_id',"Batches Line")

	employee_payroll_info_line_ids = fields.One2many('employee.payroll.info.line','hr_payslip_batches_id',"Payslip Lines")
	state = fields.Selection([('draft','Draft'),
							  ('verify','Verify'),
							  ('approve','Approve'),
							  ('payment',"Under Payment"),
							  ('paid',"Paid"),
							  ('cancel',"Cancel")],default='draft',string="Status")

	employee_hr_payslip_ids = fields.One2many('hr.payslip', 'employee_payslip_batches_id')

	@api.multi
	def action_verify(self):
		for rec in self:
			for payslip in rec.employee_hr_payslip_ids:
				payslip.compute_sheet()
				payslip.state = 'verify'

			# for emp in rec.employee_payroll_info_line_ids:
			# 	month = datetime.strptime(rec.date_from, "%Y-%m-%d").month
			# 	leave_type = self.env['hr.holidays.status'].search([('limit', '=', False)], limit=1, order='id asc')
			#
			# 	self.env['month.leave.status'].create({'status_id': emp.employee_id.id,
			# 										   'month_id': month + 1,
			# 										   'leave_id': leave_type.id,
			# 										   'available': emp.leave_cf})

		rec.state = 'verify'

	@api.multi
	def action_paid(self):
		for rec in self:
			rec.state = 'paid'
			for lines in rec.employee_hr_payslip_ids:
				lines.state = 'paid'

	@api.multi
	def action_approve(self):
		for rec in self:
			current_month = datetime.strptime(rec.date_to, "%Y-%m-%d").month
			current_year = datetime.strptime(rec.date_to, "%Y-%m-%d").year
			rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pt')], limit=1)

			professional_payment = self.env['professional.tax.payment'].search(
				[('payment_month', '=', current_month), ('hr_salary_rule_id', '=', rule.id)], limit=1)
			if professional_payment:
				update_date1 = datetime.strptime(professional_payment.date_from,"%Y-%m-%d")
				update_date2 = datetime.strptime(professional_payment.date_to,"%Y-%m-%d")
				days = 365
				if current_year %4 ==0:
					if current_year %100 ==0:
						if current_year %400 ==0:
							days = 366
						else:
							days=365
					else:
						days=366
				else:
					days = 365
				new_date_from = update_date1 + timedelta(days=days)
				new_date_to = update_date2 + timedelta(days=days-1)
				professional_payment.write({'date_from':new_date_from,
											'date_to':new_date_to})
			rec.state = 'approve'
	
	@api.multi
	def get_records(self):
		for rec in self:
			list = []
			for lin in rec.employee_payroll_info_line_ids:
				list.append(lin)
			return list


	@api.multi
	def convert_to_words(self,num):
		wGenerator = Number2Words()
		amt_in_words = ''
		if num >= 0.0:

			amt_in_words = wGenerator.convertNumberToWords(num)
		return amt_in_words



	@api.multi
	def action_view_individual(self):
		for rec in self:
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'hiworth_hr_attendance.report_employee_payslip_individual_template',
				'report_type': 'qweb-html'
			}


	@api.multi
	def action_payment(self):
		for rec in self:
			rec.state = 'payment'

	@api.multi
	def action_cancel(self):
		for rec in self:
			rec.state = 'cancel'


	@api.multi
	def action_view_payroll_report(self):
		for rec in self:
			return {
				'type': 'ir.actions.report.xml',
				'report_name': 'hiworth_hr_attendance.report_employee_payslip_batches_template',
				'report_type': 'qweb-html'
			}

	@api.multi
	def action_generate_payslip(self):
		line_ids = []
		for rec in self:
			if rec.employee_hr_payslip_ids:
				rec.employee_hr_payslip_ids.unlink()
			for emp in self.env['hr.employee'].search([('company_contractor_id', '=', rec.contract_company_id.id)]):
				ttyme = datetime.strptime(rec.date_to, "%Y-%m-%d")
				values = {
					'employee_id': emp.id,
					'date_from': rec.date_from,
					'date_to': rec.date_to,
					'contract_id': self.env['hr.contract'].search(['&',('employee_id', '=', emp.id),('state', '=', 'active')]).id,
					'month': ttyme.strftime('%B'),
					'name': _('Salary Slip of %s for %s') % (emp.name, tools.ustr(ttyme.strftime('%B-%Y'))),
				}
				line_ids.append((0, 0, values))
				rec.employee_hr_payslip_ids = line_ids

			# if rec.employee_payroll_info_line_ids:
			# 	rec.employee_payroll_info_line_ids.unlink()
			# for emp in self.env['hr.employee'].search([('company_contractor_id','=',rec.contract_company_id.id)]):
			# 	employee_payroll_infos = self.env['employee.payroll.info'].search([('date_from','=',rec.date_from),('date_to','=',rec.date_to),('employee_id','=',emp.id)])
			# 	if employee_payroll_infos:
			# 		for employee_payroll_info in employee_payroll_infos:
			# 			values = {'employee_id':emp.id,
			# 					  'leave_cf':employee_payroll_info.leave_cf,
			# 					  'basic':employee_payroll_info.basic,
			# 					  'wages_due':employee_payroll_info.wages_due,
			# 					  'pf_wages':employee_payroll_info.pf_wages,
			# 					  'pf':employee_payroll_info.pf,
			# 					  'esi':employee_payroll_info.esi,
			# 					  'professional_tax':employee_payroll_info.professional_tax,
			# 					  'labour_welfare_fund':employee_payroll_info.labour_welfare_fund,
			# 					  'advance':employee_payroll_info.advance,
			# 					  'canteen':employee_payroll_info.canteen,
			# 					  'welfare_society':employee_payroll_info.welfare_society,
			# 					  'mediclaim_insurance':employee_payroll_info.mediclaim_insurance,
			# 					  'lic_premium':employee_payroll_info.lic_premium,
			# 					  'staff_donation':employee_payroll_info.staff_donation,
			# 					  'chitty':employee_payroll_info.chitty,
			# 					  'mobile_over':employee_payroll_info.mobile_over,
			# 					  'fine':employee_payroll_info.fine,
			# 					  'tds':employee_payroll_info.tds,
			# 					  'total_deduction':employee_payroll_info.total_deduction,
			# 					  'reimbursement':employee_payroll_info.reimbursement,
			# 					  'net_salary':employee_payroll_info.net_salary,
			# 					  'hr_payslip_batches_id':rec.id}
			# 		self.env['employee.payroll.info.line'].create(values)

class HRPayslipBatchesLine(models.Model):
	_name = 'hr.payslip.batches.line'

	employee_id = fields.Many2one('hr.employee',"Employee")
	payslip_batches_salary_ids = fields.One2many('hr.payslip.batches.salary','payslip_batches_line_id',"Payslip Batches")
	payslip_batches_id = fields.Many2one('hr.payslip.batches',"Payslip Batches")

	@api.multi
	def view_deduction_summary(self):
		for rec in self:
			view_id = self.env.ref('hiworth_hr_attendance.hr_payslip_batches_form_salary_employee').id
			return {
				'name': 'Payroll',
				'view_type': 'form',
				'view_mode': 'form',
				'target': 'new',
				'res_model': 'hr.payslip.batches.line',
				 'views' : [(view_id,'form')],
				'type': 'ir.actions.act_window',

			}


class EmployeePayrollInfoLine(models.Model):
	_name = 'employee.payroll.info.line'

	@api.depends('staff_donation', 'mobile_over', 'fine', 'chitty', 'welfare_society','reimbursement','pf','esi','professional_tax','labour_welfare_fund','advance','canteen','welfare_society','mediclaim_insurance','lic_premium','tds')
	def compute_total_deduction(self):
		for rec in self:
			rec.total_deduction = rec.pf + rec.esi + rec.professional_tax + rec.labour_welfare_fund + rec.advance + rec.canteen + rec.welfare_society + rec.mediclaim_insurance + rec.lic_premium + rec.staff_donation + rec.chitty + rec.mobile_over + rec.fine + rec.tds
			rec.net_salary = rec.wages_due - rec.total_deduction + rec.reimbursement

	employee_id = fields.Many2one('hr.employee', "Employee")
	department = fields.Selection(related='employee_id.user_category')
	date_from = fields.Date("Date From",related='hr_payslip_batches_id.date_from')
	date_to = fields.Date("Date To",related='hr_payslip_batches_id.date_to')
	basic = fields.Float("Basic")
	attendance = fields.Float("Attendance")
	wages_due = fields.Float("Wages Due")
	advance = fields.Float("Salary Advance")
	staff_donation = fields.Float("Staff Donation")
	mobile_over = fields.Float("Mobile Over")
	pf = fields.Float("PF")
	esi = fields.Float("ESI")
	canteen = fields.Float("Canteen")
	professional_tax = fields.Float("P.T.")
	labour_welfare_fund = fields.Float("Labour Welfare Fund")
	fine = fields.Float("Fine")
	chitty = fields.Float("Chitty")
	welfare_society = fields.Float("Welfare Society Fund")
	leave_cf = fields.Float("Leave C/F")
	mediclaim_insurance = fields.Float("Mediclaim Inusurance")
	lic_premium = fields.Float("LIC Premium")
	pf_wages = fields.Float("PF Wages")
	esi_wages = fields.Float("ESI Wages")
	total_deduction = fields.Float("Total Deduction", compute='compute_total_deduction', store=True)
	reimbursement = fields.Float("Reimbursement")
	net_salary = fields.Float("Net Salary", compute='compute_total_deduction', store=True)
	pt_from_date = fields.Date("PT From")
	pt_to_date = fields.Date("PT To")
	pt_check = fields.Boolean("PT Applicable or Not", related='employee_id.pt_check')
	hr_payslip_batches_id = fields.Many2one('hr.payslip.batches', "Payslip Batches")
	tds= fields.Float("TDS")

class HRPayslipBatchesSalary(models.Model):
	_name = 'hr.payslip.batches.salary'

	@api.depends('amount', 'quantity')
	def compute_total(self):
		for rec in self:
			rec.total = rec.amount * rec.quantity

	name = fields.Char("Name")
	code = fields.Char("Code")
	category_id = fields.Many2one('hr.salary.rule.category', "Category")
	quantity = fields.Float("Quantity")
	amount = fields.Float("Amount")
	total = fields.Float("Total", compute='compute_total')
	payslip_batches_line_id = fields.Many2one('hr.payslip.batches.line',"Payslip")