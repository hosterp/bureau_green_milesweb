from openerp import models, fields, api, _


class SiteVisits(models.Model):
    _name = 'site.visit'

    @api.depends("compuute_no")
    def _get_row_no(self):
        if self.ids:
            count = 1
            for rec in self:
                weight_id = self.env['site.visit'].search([('id', '=', rec.id)])
                weight_id.write({'no': count})
                count += 1

    no = fields.Integer("Visit")
    date = fields.Date('Date Of Visit')
    meeting_person = fields.Many2one('res.partner', 'Meeting Person')
    place = fields.Char('Place')
    remarks = fields.Char('Remarks')
    nature_of_work = fields.Selection(
        [('mech', 'Mechanical'), ('elect', 'Electrical'), ('plum', 'Plumbing')], string="Nature Of Work")
    visit_id = fields.Many2one('site.visit.entry', string='Stock')
    compuute_no = fields.Integer("invisible field", compute="_get_row_no")


class BgMarketingSiteVisitEntry(models.Model):
    _name = 'site.visit.entry'
    _rec_name = 'project'

    # project = fields.Many2one('project.project', 'Project Name')
    project = fields.Char('Project')
    location = fields.Char('Location')
    creation_date = fields.Date('Creation Date')
    site_visit_ids = fields.One2many(
        comodel_name='site.visit',
        inverse_name='visit_id',
        string='Site Visits',
        store=True,
    )
