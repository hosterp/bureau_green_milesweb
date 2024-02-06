from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class VehicleSparePartsWizard(models.TransientModel):
    _name = 'vehicle.spare.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.multi
    def action_vehicle_spare_open_window(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'All Vehicle Spare Parts Expense Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_tms.report_fleet_vehicle_spare_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def get_details(self):
        lst = []
        vehicles = self.env['fleet.vehicle.log.services'].search([])
        if vehicles:
            print("found........................................")
        else :
            print("not found..............................")
        for vid in vehicles:
            for lines in vid.cost_ids:
                print("date in record",lines.date1)
                print("date from",self.date_from)
                print("date to",self.date_to)
                if (lines.date1 >= self.date_from):
                    if(lines.date1 <= self.date_to):

                        vals = {
                            'date':lines.date1,
                            'vehicle_no':lines.vehicle_id.name,
                            'vehicle_model' :lines.vehicle_id.model_id.name,
                            'parts_change':lines.new_parts_name,
                            'total_amt':lines.amount,
                            'sub_total':0,

                        }
                        lst.append(vals)
                total = 0
                for vals in lst:
                    total = total + vals['total_amt']
                for vals in lst:
                    vals['sub_total'] = total

        return lst
