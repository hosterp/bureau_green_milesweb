from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class VehicleSparePartsWizard(models.TransientModel):
    _name = 'vehicle.diesel.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.multi
    def action_vehicle_diesel_open_window(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'All Vehicle Diesel Infomation-Expense Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_tms.report_fleet_vehicle_diesel_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def get_details(self):
        vehicle_obj = self.env['diesel.pump.line'].search([])
        vehicle_det = []
        vehicle_lst = []
        for vehicles in vehicle_obj:
            print("vehicles are.......", vehicles.vehicle_id)
            item = vehicles.vehicle_id

            if item not in vehicle_lst:
                if item:
                    vehicle_vals = ({
                        # 'date': vehicles.date,
                        'vehicle_id': vehicles.vehicle_id.name,
                        'vehicle_model': vehicles.vehicle_id.model_id.name,
                        'diesel_ltr': vehicles.litre,
                        'diesel_price': vehicles.total_litre_amount,
                        'total_km': vehicles.total_odometer,
                    })
                    vehicle_det.append(vehicle_vals)
                    vehicle_lst.append(vehicles.vehicle_id)
            else:
                item_copy = vehicles.vehicle_id
                for dicts in vehicle_det:
                    if item_copy == dicts['vehicle_id']:
                        old_ltr = dicts['diesel_ltr']
                        new_ltr = old_ltr + vehicles.litre
                        dicts['diesel_ltr'] = new_ltr

                        old_price = dicts['diesel_price']
                        new_price = old_price + vehicles.total_litre_amount
                        dicts['diesel_ltr'] = new_price

                        old_km = dicts['total_km']
                        new_km = old_km + vehicles.total_odometer
                        dicts['total_km'] = new_km
        return vehicle_det