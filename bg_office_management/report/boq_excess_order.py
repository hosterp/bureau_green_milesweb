from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class BoqexcessOrder(models.TransientModel):
    _name = 'boq.excess.order.reports'

    project_id = fields.Many2one('project.project', 'Project Name')


    @api.multi
    def action_excess_order(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Boq Excess Order Report By Qs',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_boq_excess_order_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def action_boq_excess_view(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'name': 'Boq Excess Order Report By Qs',
            'type': 'ir.actions.report.xml',
            'report_name': 'bg_office_management.report_boq_excess_order_template',
            'datas': datas,
            'report_type': 'qweb-html',
        }

    @api.multi
    def get_details(self):
        lst = []
        domain = []
        if self.project_id:
            domain += [('project_id', '=', self.project_id.id)]

        records = self.env['boq.excessorder.qs'].search(domain)
        for rec in records:
            vals = {
                'project_id': rec.project_id.name,
                'category': rec.overhead_category.name,
                'sub_category': rec.overhead_sub_category.name,
                'material': rec.material.name,
                'description': rec.description,
                'quantity': rec.qty,
                'unit': rec.unit.name,
                'measure_len': rec.measure_length,
                'unit_cost': rec.unit_cost,
                'total_cost': (rec.unit_cost*rec.qty),
                'remark': rec.remarks,
            }
            lst.append(vals)
        return lst
