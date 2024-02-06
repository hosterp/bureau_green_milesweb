from openerp import models, fields, api

from datetime import datetime
from dateutil.relativedelta import relativedelta

class LabourWelfareFund(models.Model):
    _name = 'labour.welfare.fund'

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
            amount_emp = 0
            domain = []
            domain.append(('month','=',self.month))
            domain.append(('year','=',self.year))
            if self.company_contractor_id:
                domain.append(('company_contractor_id', '=', self.company_contractor_id.id))

            for record in self.env['hr.employee'].search([('labour_welfare_fund', '=', True),('company_contractor_id', '=', self.company_contractor_id.id)]):
                employee_payroll_info = self.env['employee.payroll.info.line'].search(
                    [('employee_id', '=', record.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to)])
                if employee_payroll_info:

                    professional_tax = self.env['hr.salary.rule'].search([('related_type', '=', 'labour_welfare')], order='id desc',
                                                                     limit=1)





                    if professional_tax.labour_welfare_type == 'lumpsum':
                        amount = professional_tax.labour_emp_contri
                        amount_emp = professional_tax.labour_employer_contri
                    else:
                        amount = employee_payroll_info.basic * (professional_tax.labour_emp_contri /100)
                        amount_emp = employee_payroll_info.basic * (professional_tax.labour_employer_contri/100)
                    if employee_payroll_info.basic !=0:
                        values = {
                            'employee_id': record.id,

                            'wages_due': employee_payroll_info.basic,
                            'amount':amount ,
                            'employer_contribution': amount_emp,

                        }
                        list.append((0, 0, values))
            self.labour_welfare_fund_line_ids = list

    @api.depends('labour_welfare_fund_line_ids')
    def compute_total_amount(self):
        for rec in self:
            amount = 0
            for pt_line in rec.labour_welfare_fund_line_ids:
                amount += pt_line.total_contri
            rec.total_amount = amount

    @api.depends('paid_amount')
    def compute_balance(self):
        for rec in self:
            balance = rec.total_amount - rec.paid_amount
            rec.balance = balance

    date = fields.Date("Date", default=fields.Date.today)
    user_id = fields.Many2one('res.users', 'User', default=lambda self: self.env.user)
    journal_id = fields.Many2one('account.journal', string='Mode of Payment', domain="[('type','in',['cash','bank'])]")
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
    year = fields.Selection([(num, str(num)) for num in range(1960, 5080)], 'Year', default=(datetime.now().year))
    labour_welfare_fund_line_ids = fields.One2many('labour.welfare.fund.line', 'line_id', string="Professional Tax Lines")
    company_contractor_id = fields.Many2one('res.partner', "Contract Company",
                                            domain="[('company_contractor','=',True)]")
    paid_amount = fields.Float("Paid Amount")
    total_amount = fields.Float("Total Amount", compute='compute_total_amount', store=True)
    balance = fields.Float("Balance", compute='compute_balance', store=True)


    @api.multi
    def button_action_paid(self):
        for rec in self:
            professional_tax = self.env['hr.salary.rule'].search([('related_type', '=', 'labour_welfare')], order='id desc',
                                                                 limit=1)
            total = 0
            for line in rec.labour_welfare_fund_line_ids:
                total += line.amount
            move = self.env['account.move']
            move_line = self.env['account.move.line']

            move_id = move.create({
                'journal_id': rec.journal_id.id,
                'date': rec.date,
            })

            line_id = move_line.create({
                'account_id': rec.journal_id.default_credit_account_id.id,
                'name': 'Labour Welfare Amount',
                'credit': total,
                'debit': 0,
                'move_id': move_id.id,
            })

            line_id = move_line.create({
                'account_id': professional_tax.common_account_id.id,
                'name': 'Labour Welfare Amount',
                'credit': 0,
                'debit': total,
                'move_id': move_id.id,
            })
            move_id.button_validate()


class LabourWelfareFundLine(models.Model):
    _name = 'labour.welfare.fund.line'

    @api.depends('amount','employer_contribution')
    def compute_total_contri(self):
        for record in self:
            record.total_contri = record.amount + record.employer_contribution

    line_id = fields.Many2one('labour.welfare.fund', "Labour Welfare Fund")
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    wages_due = fields.Float('Wages Due')
    amount = fields.Float("Employee Contribution")
    employer_contribution = fields.Float("Employer Contribution")
    total_contri = fields.Float("Total Contribution",compute='compute_total_contri',store=True)
