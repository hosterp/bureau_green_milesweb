from openerp import models, fields, api, _


class OverheadCategory(models.Model):
    _name = 'overhead.category'

    name = fields.Char('Category Name')


class OverheadSubCategory(models.Model):
    _name = 'overhead.subcategory'

    name = fields.Char('Sub Category Name')


class OverheadCostingCommercial(models.Model):
    _name = 'overheadcost.commercial'
    _rec_name = 'overhead_category'

    overhead_category = fields.Many2one('overhead.category', 'Category')
    overhead_sub_category = fields.Many2one('overhead.subcategory', 'Sub Category')
    estimated_total_amount = fields.Float('Estimated Total Amount')
    estimated_total_amount_month = fields.Float('Estimated Total Amount per Month')
    month_select = fields.Selection(
        [('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'),
         ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'),
         ('november', 'November'), ('december', 'December')], string="Month")
    actual_value = fields.Float()
    date = fields.Date(default=fields.date.today())
