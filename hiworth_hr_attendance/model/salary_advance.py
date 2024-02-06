from openerp import models, fields, api

class SalaryAdvance(models.Model):
    _name = "hr.salary.advance"
    _rec_name = "employee_id"

    employee_id = fields.Many2one('hr.employee','Employee')
    advance_amount = fields.Float()
    date = fields.Date()
    tenure = fields.Integer()
    emi_start_date = fields.Date()
    emi_end_date = fields.Date()
    emi_amount = fields.Float(compute='_compute_emi')
    balance_amount = fields.Float(compute='_compute_balance')
    paid_amount = fields.Float(compute='_compute_paid_amount')
    emi_lines = fields.One2many('hr.salary.advance.lines','salary_advance_id')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'),('closed', 'Closed')], default="draft")

    @api.depends('tenure','advance_amount')
    def _compute_emi(self):
        for rec in self:
            if rec.tenure>0:
                rec.emi_amount = rec.advance_amount / rec.tenure
    @api.depends('paid_amount','advance_amount')
    def _compute_balance(self):
        for rec in self:
            rec.balance_amount = rec.advance_amount - rec.paid_amount
    @api.depends('emi_lines','advance_amount')
    def _compute_paid_amount(self):
        for rec in self:
            if rec.emi_lines:
                rec.paid_amount = sum(rec.emi_lines.mapped('payment'))

    @api.multi
    def button_active(self):
        for rec in self:
            rec.state = 'active'



class SalaryAdvanceLines(models.Model):
    _name = "hr.salary.advance.lines"

    date = fields.Date()
    payment = fields.Float()
    balance_amount = fields.Float()
    salary_slip = fields.Many2one('hr.payslip')
    salary_advance_id = fields.Many2one('hr.salary.advance')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active'),('closed', 'Closed')], default="draft")

