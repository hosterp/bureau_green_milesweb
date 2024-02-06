from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class CostingProgressReport(models.TransientModel):
    _name = 'work.hours.reports'

    project_id = fields.Many2one('project.project', 'Project Name')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.multi
    def action_work_hours(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Work Hours Planned Report By Qs',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_work_hrs_planned_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def action_work_hrs_view(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'name': 'Work Hours Planned Report By Qs',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_work_hrs_planned_template',
            'datas': datas,
            'report_type': 'qweb-html',
        }

    @api.multi
    def get_details(self):
        lst = []
        domain = []
        if self.project_id:
            domain += [('project_id', '=', self.project_id.id)]
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]
        records = self.env['work.hours.qs'].search(domain)
        print(records)
        for rec in records:

            d = float((rec.total_manhours_required)/float(rec.estimated_manhours_required)*100)

            vals = {
                'project_id': rec.project_id.name,
                'date_from': self.date_from,
                'date_to': self.date_to,
                'date': rec.date,
                'construction_activities': rec.construction_activities.name,
                'category': rec.overhead_category.name,
                'estimated_qty': rec.estimated_qty,
                'unit': rec.unit.name,
                'estimated_manhours_required': rec.estimated_manhours_required,
                'total_manhours_required': rec.total_manhours_required,
                'difference': (rec.estimated_manhours_required - rec.total_manhours_required),
                'per_used':round(d,2) ,

            }
            lst.append(vals)
        return lst
