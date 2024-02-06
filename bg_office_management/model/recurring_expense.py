from openerp import models, fields, api, _


class RecurringExpense(models.Model):
    _name = 'recurring.expense'
    _rec_name = 'overhead_category'

    overhead_category = fields.Many2one('overhead.category', 'Overhead Category')
    overhead_sub_category = fields.Many2one('overhead.subcategory', 'Overhead Sub Category')
    name = fields.Many2one('res.partner','Name')
    recurring_period =  fields.Selection(
        [('monthly', 'Monthly'), ('annually', 'Annually')],string="Recurring Period")
    date_of_recurring = fields.Date('Date of Recurring')
    amount_recurring = fields.Float('Amount Recurring')

