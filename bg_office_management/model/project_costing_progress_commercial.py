from openerp import models, fields, api, _


class ProjectCostingProgressCommercial(models.Model):
    _name = 'costprogress.commercial'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', 'Project Name')
    project_value = fields.Float('Project Value')
    project_duration_months = fields.Float('Project Duration In Months')
    project_estimated_man_hours = fields.Float('Project estimated Man hours')
    actual_man_hours = fields.Float('Actual Man Hours')
    estimated_material_cost = fields.Float('Estimated material Cost')
    purchase_material_cost = fields.Float('Purchased Material Cost')
    date = fields.Date('Date')
