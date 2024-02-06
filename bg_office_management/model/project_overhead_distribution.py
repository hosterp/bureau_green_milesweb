from openerp import models, fields, api, _

class ProjectOverheadDistribution(models.Model):
    _name = 'projectoverhead.distribution'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project','Project Name')
    project_value = fields.Float('Project Value')
    month_select = fields.Selection(
        [('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'),
         ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'),
         ('november', 'November'), ('december', 'December')],string="Month")
    actual_value = fields.Float()
    date = fields.Date(default=fields.date.today())
