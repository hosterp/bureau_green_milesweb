from openerp import models, fields, api


class VehicleSparePartsWizard(models.TransientModel):
    _name = 'vehicle.costing.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.multi
    def action_vehicle_costing(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Costing Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_tms.report_fleet_vehicle_costing_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def get_details(self):
        list1 = []
        vehicles = self.env['fleet.vehicle'].search([])
        for vehicle in vehicles:
            maintenance = sum(self.env['vehicle.preventive.maintenance.line'].search(
               [('vehicle_id', '=', vehicle.id), ('date', '>=', self.date_from),
                ('date', '<=', self.date_to)]).mapped('cost'))

            spare = sum(self.env['fleet.vehicle.cost'].search(
                [('vehicle_id', '=', vehicle.id), ('date', '>=', self.date_from), ('date', '<=', self.date_to)]).mapped('total_amount'))

            retreading = sum(self.env['retreading.tyre.line'].search(
                [('vehicle_id', '=', vehicle.id), ('retreading_date', '=', self.date_from),
                 ('retreading_date', '<=', self.date_to)]).mapped('retrading_cost'))

            fuel_lines = sum(self.env['vehicle.fuel.voucher'].search(
                [('vehicle_id', '=', vehicle.id), ('date', '>=', self.date_from),
                 ('date', '<=', self.date_to)]).mapped('amount'))

            driver_statement = self.env['driver.daily.statement'].search(
                [('vehicle_no', '=', vehicle.id), ('date', '>=', self.date_from), ('date', '<=', self.date_to)])
            list_ids = []
            for stmt in driver_statement:
                list_ids += stmt.driver_stmt_line.ids
            expense_ids = []
            for stmt in driver_statement:
                expense_ids += stmt.stmt_line.ids
            driver_stmt_line = sum(self.env['driver.daily.statement.line'].search([('id', 'in', list_ids)]).mapped('driver_betha'))
            expense_line = sum(self.env['driver.daily.expense'].search([('id', 'in', expense_ids)]).mapped('payment'))

            owner = str(vehicle.vehicle_under.name) if vehicle.vehicle_under.name else "NA"
            model = str(vehicle.model_id.name) if vehicle.model_id.name else "NA"
            type_1 = str(vehicle.vehicle_categ_id.name) if vehicle.vehicle_categ_id.name else "NA"
            no = str(vehicle.name) if vehicle.name else "NA"

            vals = {
                'owner_name': owner,
                'model': model,
                'type': type_1,
                'no': no,
                'no_of_days': len(driver_statement),
                'maintenance_cost': maintenance+retreading+spare,
                'fuel_cost': fuel_lines,
                'driver_expense': driver_stmt_line,
                'other_expense': expense_line,
                'total_amt': maintenance+retreading+spare+fuel_lines+driver_stmt_line+expense_line,

            }
            list1.append(vals)

        return list1
