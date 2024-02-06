from openerp import models, fields, api, _


class ConstructionActivity(models.Model):
    _name = 'construction.activity'

    name = fields.Char('Construction Activity')


class WorkHoursPlannedByQs(models.Model):
    _name = 'work.hours.qs'
    _rec_name = 'construction_activities'

    project_id = fields.Many2one('project.project', 'Project Name')
    date = fields.Date('Date')
    construction_activities = fields.Many2one('construction.activity', 'Construction Activitiy')
    overhead_category = fields.Many2one('overhead.category', 'Category')
    estimated_qty = fields.Integer('Estimated Quantity')
    unit = fields.Many2one('product.uom', 'Units')
    estimated_manhours_required = fields.Integer('Estimated ManHours Required')

    total_manhours_required = fields.Integer('Total ManHours Used')
    difference = fields.Integer('Difference')
