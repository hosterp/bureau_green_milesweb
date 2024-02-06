from openerp import models, fields, api

class QuantityStatus(models.Model):

    _name = 'quantity.status'

    @api.one
    def done(self):
        self.state = 'done'

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self:
            return {'domain':{
                'location_id':[('id','in',rec.project_id.project_location_ids.ids)]
            }}


    state = fields.Selection([('not', 'Not Done'), ('done', 'Done')], 'State', default='not')
    location_id = fields.Many2one('stock.location', 'Site')
    date = fields.Date('Create Date')
    status_line = fields.One2many('quantity.status.line', 'status_id', 'Status')
    final = fields.Boolean('Is Final')
    project_id = fields.Many2one('project.project',"Project")
    district = fields.Char("District",related='project_id.district')
    length = fields.Float("Length",related='project_id.length')
    work_status_line = fields.One2many('survey.work.status.line', 'quantity_status_id', 'Work Status')

class QuantityStatusLine(models.Model):

    _name = 'quantity.status.line'

    @api.one
    def get_diff(self):
        for l in self:
            l.difference = l.schedule - l.proposal

    status_id = fields.Many2one('quantity.status', 'Status')
    worklist_id = fields.Many2one('survey.worklist', 'Particulars')
    schedule = fields.Float('f')
    proposal = fields.Float('Proposal - Rs')
    difference = fields.Float('Difference', compute="get_diff")
    remark = fields.Char("Remarks")
    attachment = fields.Binary("Attachment")

class WorkStatusLine(models.Model):

    _name = 'survey.work.status.line'

    quantity_status_id = fields.Many2one('quantity.status', 'Status')
    worklist_id = fields.Many2one('survey.worklist', 'Particulars')
    no_binding = fields.Float(string="No of Binding")
    no_field_book = fields.Float(string="No of Field Book")
    date_submission = fields.Date("Date of Submission")
    submi_auth = fields.Char("Submission Authority")
    subm_by_id = fields.Many2one('hr.employee',domain="[('user_category','=','survey_team')]",string="Submitted By")
    reporting_status = fields.Char('Reporting Status')
    reporting_date = fields.Date('Reporting Date')
    approval_status = fields.Char('Approval Status')
    approval_date = fields.Date('Approval Date')
    remarks = fields.Char("Remarks")