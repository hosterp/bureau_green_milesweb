from openerp import models, fields, api, _


class TenderAttachmentForm(models.Model):
    _name = 'tender.attachments.tender'

    tender_id = fields.Many2one('tender.tender', "Tender")
    date = fields.Date('Date', default=fields.Date.today)
    name = fields.Char('Name')
    binary_field = fields.Binary('File')
    filename = fields.Char('Filename')
    # project_id = fields.Many2one('project.project', "Project")


class TenderForm(models.Model):
    _name = 'tender.tender'
    _rec_name = 'tender_no'

    @api.multi
    def button_approve(self):
        self.state = 'approved'

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'

    @api.multi
    def button_reject(self):
        self.state = 'rejected'

    tender_no = fields.Char('Tender Number')
    name = fields.Char('Work Name')
    location = fields.Char('Location')
    contract_awarder = fields.Char('Contract Awarder')
    creation_date = fields.Date('Creation Date')
    tender_last_date = fields.Date('Last Date Of Tender')
    tender_postponed_date = fields.Date('Postponed Date Of Tender')
    tender_amount = fields.Float('Tender Amount')
    bond_amount = fields.Float('Bond Amount')
    attachment_ids = fields.One2many('tender.attachments.tender', 'tender_id')
    state = fields.Selection([('draft', 'Draft'),
                                      ('approved', 'Accepted'),
                                      ('rejected', 'Rejected'),
                                      ('cancel', 'Cancel'),],default="draft")
