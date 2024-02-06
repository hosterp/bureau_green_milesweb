from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta

class ProfessionalTax(models.Model):
    _name = 'professional.tax'

    @api.onchange('month')
    def onchange_pf(self):
        list = []



        if self.month:
            date = '1 ' + self.month + ' ' + str(datetime.now().year)

            date_from = datetime.strptime(date, '%d %B %Y')
            date_to = date_from + relativedelta(day=31)
            date_from = date_from.date()
            date_to = date_to.date()
            wages_due =0
            for record in self.env['hr.employee'].search([('pt_check', '=', True),('company_contractor_id', '=', self.company_contractor_id.id)]):

                employee_payroll_info = self.env['employee.payroll.info.line'].search(
                    [('employee_id', '=', record.id), ('date_from', '>=', date_from), ('date_to', '<=', date_to)])
                if employee_payroll_info:
                    rule = self.env['hr.salary.rule'].search([('related_type', '=', 'pt')], limit=1)
                    current_month = date_from.month

                    professional_payment = self.env['professional.tax.payment'].search(
                        [('payment_month', '=', current_month), ('hr_salary_rule_id', '=', rule.id)], limit=1)


                    wages_due = 0
                    for line in self.env['employee.payroll.info.line'].search([('employee_id', '=', record.id),
                                                                               ('date_from', '>=',
                                                                                professional_payment.date_from), (
                                                                               'date_to', '<=',
                                                                               professional_payment.date_to)]):
                        wages_due += line.wages_due
                    professional_tax = self.env['hr.salary.rule'].search([('related_type','=','pt')],order='id desc',limit=1)
                    amount = 0


                    profess_tax_line_config = self.env['professional.tax.line'].search([('rule_id','=',professional_tax.id),('range_from','>=',wages_due),('range_to','<=',wages_due)],limit=1)
                    amount = profess_tax_line_config.tax_amount
                    print "hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh",wages_due
                    if amount != 0:
                        values = {
                            'employee_id': record.id,

                            'wages_due': wages_due,
                            'amount': amount,


                        }
                        list.append((0, 0, values))


        self.professional_tax_line_ids = list


    @api.depends('professional_tax_line_ids')
    def compute_total_amount(self):
        for rec in self:
            amount = 0
            for pt_line in rec.professional_tax_line_ids:
                amount += pt_line.amount
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
    year = fields.Selection([(num, str(num)) for num in range(1960,5080)], 'Year', default=(datetime.now().year))
    professional_tax_line_ids = fields.One2many('professional.taxes.line','line_id',string="Professional Tax Lines")
    company_contractor_id = fields.Many2one('res.partner', "Contract Company",
                                            domain="[('company_contractor','=',True)]")
    paid_amount = fields.Float("Paid Amount")
    total_amount = fields.Float("Total Amount",compute='compute_total_amount',store=True)
    balance = fields.Float("Balance",compute='compute_balance',store=True)



    @api.multi
    def button_action_paid(self):
        for rec in self:
            professional_tax = self.env['hr.salary.rule'].search([('related_type', '=', 'pt')], order='id desc',
                                                                 limit=1)
            total = 0
            for line in rec.professional_tax_line_ids:
                total += line.amount
            move = self.env['account.move']
            move_line = self.env['account.move.line']

            move_id = move.create({
                'journal_id': rec.journal_id.id,
                'date': rec.date,
            })


            line_id = move_line.create({
                'account_id': rec.journal_id.default_credit_account_id.id,
                'name': 'Professional Tax Amount',
                'credit': total,
                'debit': 0,
                'move_id': move_id.id,
            })

            line_id = move_line.create({
                'account_id': professional_tax.common_account_id.id,
                'name': 'Professional Tax Amount',
                'credit': 0,
                'debit': total,
                'move_id': move_id.id,
            })
            move_id.button_validate()

class ProfessionalTaxLine(models.Model):
    _name = 'professional.taxes.line'

    line_id = fields.Many2one('professional.tax',"Professional Tax")
    employee_id = fields.Many2one('hr.employee', 'Employee Name')
    wages_due = fields.Float('Wages Due')
    amount = fields.Float("Half Yearly Professional Tax")
