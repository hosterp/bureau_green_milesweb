from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class ReportRecurringExpense(models.TransientModel):
    _name = 'recurring.expense.reports'

    overhead_category = fields.Many2one('overhead.category', 'Category')
    overhead_sub_category = fields.Many2one('overhead.subcategory', 'Sub Category')
    name = fields.Many2one('res.partner', 'Name')
    recurring_period = fields.Selection(
        [('monthly', 'Monthly'), ('annually', 'Annually')], string="Recurring Period")

    @api.multi
    def action_recurring_expense(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Recurring Expense Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_recurring_expense_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def action_recurring_expense_view(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'name': 'Recurring Expense Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_recurring_expense_template',
            'datas': datas,
            'report_type': 'qweb-html',
        }

    @api.multi
    def get_details(self):
        lst = []
        domain = []
        if self.overhead_category:
            domain += [('overhead_category', '=', self.overhead_category.id)]
        if self.overhead_sub_category:
            domain += [('overhead_sub_category', '=', self.overhead_sub_category.id)]
        if self.name:
            domain += [('name', '=', self.name.id)]
        if self.recurring_period:
            domain += [('recurring_period', '=', self.recurring_period)]
        records = self.env['recurring.expense'].search(domain)
        for rec in records:
            vals = {
                'overhead_category': rec.overhead_category.name,
                'overhead_sub_category': rec.overhead_sub_category.name,
                'name': rec.name.name,
                'recurring_period': rec.recurring_period,
                'date_of_recurring': rec.date_of_recurring,
                'amount_recurring': rec.amount_recurring,
            }
            lst.append(vals)
        return lst










