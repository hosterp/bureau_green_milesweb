from openerp import models, fields, api, _


class Activity(models.Model):
    _name = 'activity.activity.docs'

    name = fields.Char('Activity')


class BgMechDocs(models.Model):
    _name = 'mech.docs'

    mech_id = fields.Many2one('document.collection', string='Mechanical Documents')
    # floor = fields.Integer('Floor')
    work_description = fields.Char("Work Description")
    activity = fields.Many2one('activity.activity.docs', 'Activity')
    man_power = fields.Float("No of Labours")
    Duration = fields.Integer('Duration in Days')
    cost = fields.Integer('Cost')
    site_engineer = fields.Many2one('Site Engineer')


class BgElecDocs(models.Model):
    _name = 'elec.docs'

    elec_id = fields.Many2one('document.collection', string='Electrical Documents')
    work_description = fields.Char("Work Description")
    activity = fields.Many2one('activity.activity.docs', 'Activity')
    man_power = fields.Float("No of Labours")
    Duration = fields.Integer('Duration in Days')
    cost = fields.Integer('Cost')
    site_engineer = fields.Many2one('Site Engineer')


class BgPlumDocs(models.Model):
    _name = 'plum.docs'

    plum_id = fields.Many2one('document.collection', string='Plumbing Documents')
    work_description = fields.Char("Work Description")
    activity = fields.Many2one('activity.activity.docs', 'Activity')
    man_power = fields.Float("No of Labours")
    Duration = fields.Integer('Duration in Days')
    cost = fields.Integer('Cost')
    site_engineer = fields.Many2one('res.partner','Site Engineer')


class BgDocumentCollection(models.Model):
    _name = 'document.collection'

    name = fields.Char('Planning/Programme')
    project = fields.Many2one('project.project', 'Project')
    mech_docs_ids = fields.One2many(
        comodel_name='mech.docs',
        inverse_name='mech_id',
        string='Mechanical',
        store=True,
    )
    elect_docs_ids = fields.One2many(
        comodel_name='elec.docs',
        inverse_name='elec_id',
        string='Electrical',
        store=True,
    )
    plum_docs_ids = fields.One2many(
        comodel_name='plum.docs',
        inverse_name='plum_id',
        string='Plumbing',
        store=True,
    )
    mech = fields.Binary(string='Upload Mechanical Documents')
    plum = fields.Binary(string='Upload Plumbing Documents')
    elec = fields.Binary(string='Upload Electrical Documents')
