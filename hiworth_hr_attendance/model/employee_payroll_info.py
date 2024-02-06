from openerp import models, fields, api, _
from datetime import datetime
import math

class EmployeePayrollInfo(models.Model):
    _name = 'employee.payroll.info'

    @api.model
    def create(self,vals):
        res = super(EmployeePayrollInfo, self).create(vals)
        basic_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'basic')], limit=1)
        attend_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'attendance')], limit=1)
        pf_rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pf')], limit=1)
        rule_list = []
        contract_emp = self.env['hr.contract'].search([('employee_id', '=', res.employee_id.id), ('state', '=', 'active')])
        res.basic = contract_emp.wage or 0.0
        res.attendance = self.env['hr.employee'].get_present_days(res.employee_id.id, res.date_from,
                                                              res.date_to)
        no_of_days = datetime.strptime(res.date_to,"%Y-%m-%d") - datetime.strptime(res.date_from,"%Y-%m-%d")
        # res.wages_due = ((contract_emp.wage)/no_of_days.days)*res.attendance
        rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pf')], limit=1)
        rule_contri = self.env['contribution.line'].search(
            [('rule_id', '=', rule.id)], order='witheffct_date desc', limit=1)

        if res.wages_due <= rule_contri.celing_limit:
            pf_wages = res.wages_due
        if res.wages_due > rule_contri.celing_limit:
            pf_wages = rule_contri.celing_limit
        res.pf_wages = pf_wages
        res.pf = round(pf_wages * (rule_contri.emloyee_ratio/100))
        rule = self.env['hr.salary.rule'].search([('related_type', '=', 'esi')], limit=1)
        rule_contri = self.env['esi.contribution.line'].search(
            [('rule_id', '=', rule.id)], order='witheffct_date desc', limit=1)
        esi_wages = 0
        if res.basic <= rule_contri.celing_limit:
            esi_wages = res.wages_due

        res.esi_wages = esi_wages
        employee_amount = esi_wages * (rule_contri.emloyee_ratio / 100)
        res.esi = math.ceil(employee_amount)

        rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pt')], limit=1)
        current_month = datetime.strptime(res.date_to,"%Y-%m-%d").month

        professional_payment = self.env['professional.tax.payment'].search([('payment_month','=',current_month),('hr_salary_rule_id','=',rule.id)],limit=1)

        pt_wages = 0
        if professional_payment:
            for line in self.env['employee.payroll.info.line'].search([('employee_id','=',res.employee_id.id),('date_from','>=',professional_payment.date_from),('date_to','<=',professional_payment.date_to)]):

                pt_wages  += line.wages_due

        print "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu",pt_wages
        profess_tax_line_config = self.env['professional.tax.line'].search(
            [('rule_id', '=', rule.id), ('range_from', '<=', pt_wages),
             ('range_to', '>=', pt_wages)], limit=1)
        amount = 0
        print "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",profess_tax_line_config
        if profess_tax_line_config:
            amount = profess_tax_line_config.tax_amount
        res.professional_tax = amount

        canteen_amt = 0
        canteen_daily = self.env['canteen.daily'].search([('date','>=',res.date_from),('date','<=',res.date_to)])
        for can in canteen_daily:
            canteen_amt += can.amount
        res.canteen = canteen_amt
        labour_welfare_fund = 0
        labour_welfare_fund_ids = self.env['hr.salary.rule'].search([('related_type', '=', 'labour_welfare')], order='id desc',
                                                             limit=1)
        if labour_welfare_fund_ids.labour_welfare_type == 'per':
            labour_welfare_fund = contract_emp.wage * (labour_welfare_fund_ids.labour_emp_contri /100)
        else:
            labour_welfare_fund = labour_welfare_fund_ids.labour_emp_contri
        res.labour_welfare_fund = labour_welfare_fund


        carry_forward = self.env['hr.employee'].get_lop(res.employee_id.id, res.date_from, res.date_to) + self.env['hr.employee'].get_exgratia_days(res.employee_id.id, res.date_from, res.date_to)
        carry_forward -= self.env['hr.employee'].get_absent_days(res.employee_id.id, res.date_from, res.date_to)
        print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",carry_forward

        if carry_forward < 0:
            carry_forward = 0
        carry_forward = self.env['month.leave.status'].search([('status_id','=',res.employee_id.id),('month_id','=',datetime.strptime(res.date_from,"%Y-%m-%d").month)])
        res.leave_cf = carry_forward.remaining
        return res


    @api.depends('staff_donation','mobile_over','fine','chitty','welfare_society','pf','esi','professional_tax','labour_welfare_fund','advance','canteen','welfare_society','mediclaim_insurance','lic_premium','tds')
    def compute_total_deduction(self):
        for rec in self:
            rec.total_deduction = rec.pf + rec.esi + rec.professional_tax + rec.labour_welfare_fund + rec.advance + rec.canteen + rec.welfare_society + rec.mediclaim_insurance + rec.lic_premium + rec.staff_donation + rec.chitty + rec.mobile_over + rec.fine + rec.tds
            rec.net_salary = rec.wages_due - rec.total_deduction + rec.reimbursement

    employee_id = fields.Many2one('hr.employee',"Employee")
    department = fields.Selection(related='employee_id.user_category')
    date_from = fields.Date("Date From")
    date_to = fields.Date("Date To")
    basic = fields.Float("Basic")
    attendance = fields.Float("Attendance")
    wages_due = fields.Float("Wages Due")
    advance = fields.Float("Salary Advance")
    staff_donation = fields.Float("Staff Donation")
    mobile_over= fields.Float("Mobile Over")
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
    total_deduction = fields.Float("Total Deduction",compute='compute_total_deduction',store=True)
    net_salary = fields.Float("Net Salary",compute='compute_total_deduction',store=True)
    pt_from_date = fields.Date("PT From")
    pt_to_date = fields.Date("PT To")
    pt_check = fields.Boolean("PT Applicable or Not",related='employee_id.pt_check')
    hr_payslip_batches_id = fields.Many2one('hr.payslip.batches',"Payslip Batches")
    reimbursement = fields.Float("Reimbursement")
    tds= fields.Float("TDS")