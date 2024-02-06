from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class CostingProgressReport(models.TransientModel):
    _name = 'costing.progress.reports'

    project_id = fields.Many2one('project.project', 'Project Name')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.multi
    def action_costing_progress(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Costing and Progress Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_costing_progress_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def action_costing_progress_view(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'name': 'Costing and Progress Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_costing_progress_template',
            'datas': datas,
            'report_type': 'qweb-html',
        }

    @api.multi
    def get_details(self):
        lst = []
        domain = []
        projects = []
        if self.project_id:
            domain += [('project_id', '=', self.project_id.id)]
        records = self.env['costprogress.commercial'].search(domain)
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]
        for rec in records:
            pid = rec.project_id.id
            if pid not in projects:
                vals = {
                    'projects_id': rec.project_id.id,
                    'project_id': rec.project_id.name,
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'date':rec.date,
                    'project_value': rec.project_value,
                    'duration': rec.project_duration_months,
                    'e_man_hrs': rec.project_estimated_man_hours,
                    'a_man_hrs': rec.actual_man_hours,
                    'perce_man_hrs_consumed': 0,
                    'estimated_mate_cost': rec.estimated_material_cost,
                    'purchase_mat_cost': rec.purchase_material_cost,
                    'per_mat_purchased': 0,
                    'per_progress': 0,
                    'per_productivity': 0,
                }
                lst.append(vals)
                projects.append(rec.project_id.id)
            else:
                project = rec.project_id.id
                for dicts in lst:
                    if project == dicts['projects_id']:
                        old_man_hr = dicts['a_man_hrs']
                        new_man_hr = old_man_hr + rec.actual_man_hours
                        dicts['a_man_hrs'] = new_man_hr

                        old_purchase_cost = dicts['purchase_mat_cost']
                        new_purchase = old_purchase_cost + rec.purchase_material_cost
                        dicts['purchase_mat_cost'] = new_purchase
        for vals in lst:
            per_man_consumed = (vals['a_man_hrs'] / vals['e_man_hrs']) * 100
            vals['perce_man_hrs_consumed'] = per_man_consumed

            per_mat_consumed = (vals['purchase_mat_cost'] / vals['estimated_mate_cost']) * 100
            vals['per_mat_purchased'] = per_mat_consumed

        return lst
