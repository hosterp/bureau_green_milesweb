from openerp import models, fields, api, _


class BgMachines(models.Model):
    _name = 'bg.machines'

    name = fields.Char('Machinery')


class BgWorkPlans(models.Model):
    _name = 'work.sub.plans'

    plan_id = fields.Many2one('work.submission.plan', string='Works')
    nature = fields.Selection(
        [('mech', 'Mechanical'), ('elect', 'Electrical'), ('plum', 'Plumbing')], string="Nature Of Work")
    work_description = fields.Char("Work Description")
    sqft = fields.Float('Square Feet')
    # machines = fields.Many2many('bg.machines', "Machines")
    machines = fields.Many2one('bg.machines', "Machines")
    materials = fields.Many2one('product.product', "Materials")
    sub_contractor = fields.Many2one('res.partner', 'Sub Contractor')
    remarks = fields.Char('Remarks')
    start_date = fields.Date('Start Date')
    appro_finish_date = fields.Date('Approximate Finish Date')
    duration = fields.Integer('Duration Days')
    site_engineer = fields.Many2one('hr.employee', 'Site Engineer')
    file_loc = fields.Char('File Location')


class BgWorkSubPlan(models.Model):
    _name = 'work.submission.plan'
    _rec_name = 'project'

    project = fields.Char('Project')
    # project = fields.Many2one('project.project', 'Project')
    location = fields.Char('Place/Location')
    sqft = fields.Float('Square Feet')
    no_floors = fields.Integer('No floors')
    work_start_date = fields.Date('Work Start Date')
    work_completeion_date = fields.Date('Work Submission Date')
    work_agreement_date = fields.Date('Work Agreement Date')
    work_target_date = fields.Date('Work Target Date')
    work_plan_ids = fields.One2many(
        comodel_name='work.sub.plans',
        inverse_name='plan_id',
        string='Work Submission Plans',
        store=True,
    )
