
from openerp import api, models


class VehicleDetailsReport(models.AbstractModel):
    _name = 'report.hiworth_tms.vehicle_details_custom_report'

    @api.multi
    def render_html(self, data):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('hiworth_tms.vehicle_details_custom_report')
        vehicle = self.env[report.model].browse(self.id)
        tyre_detials_ids = vehicle.tyre_detials_ids

        retreading_ids = None
        fuel_lines = None
        vehicle_gps_ids = None
        battery_details_ids = None
        maintenance_ids = None
        expense_line = None
        driver_stmt_line = None
        cost_ids = None
        expense = False
        date_from = False
        date_to = False

        if data:
            expense = True
            vehicle = self.env['fleet.vehicle'].browse(data['vehicle'])
            form = data['form']
            date_from = form['date_from']
            date_to = form['date_to']
            maintenance_ids = self.env['vehicle.preventive.maintenance.line'].search(
                [('vehicle_id', '=', vehicle.id), ('date', '>=', form['date_from']), ('date', '<=', form['date_to'])])
            cost_ids = self.env['fleet.vehicle.cost'].search(
                [('vehicle_id', '=', vehicle.id), ('date', '>=', form['date_from']), ('date', '<=', form['date_to'])])
            tyre_detials_ids = None
            retreading_ids = vehicle.retreading_ids.search(
                [('vehicle_id', '=', vehicle.id), ('retreading_date', '=', form['date_from']),
                 ('retreading_date', '<=', form['date_to'])])
            fuel_lines = vehicle.fuel_lines.search(
                [('vehicle_id', '=', vehicle.id), ('date', '>=', form['date_from']),
                 ('date', '<=', form['date_to'])])
            vehicle_gps_ids = vehicle.vehicle_gps_ids.search(
                [('vehicle_id', '=', vehicle.id), ('purchase_date', '>=', form['date_from']),
                 ('purchase_date', '<=', form['date_to'])])
            battery_details_ids = vehicle.battery_details_ids.search(
                [('vehicle_id', '=', vehicle.id), ('warranty_period_from', '>=', form['date_from']),
                 ('warranty_period_from', '<=', form['date_to'])])
            driver_statement = self.env['driver.daily.statement'].search(
                [('vehicle_no', '=', vehicle.id), ('date', '>=', form['date_from']), ('date', '<=', form['date_to'])])
            list_ids = []
            for stmt in driver_statement:
                list_ids += stmt.driver_stmt_line.ids
            expense_ids = []
            for stmt in driver_statement:
                expense_ids += stmt.stmt_line.ids
            driver_stmt_line = self.env['driver.daily.statement.line'].search([('id', 'in', list_ids)])
            expense_line = self.env['driver.daily.expense'].search([('id', 'in', expense_ids)])


        docargs = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'doc': vehicle,
            'tyre_detials_ids': tyre_detials_ids,
            'retreading_ids': retreading_ids,
            'fuel_lines': fuel_lines,
            'vehicle_gps_ids': vehicle_gps_ids,
            'battery_details_ids': battery_details_ids,
            'maintenance_ids': maintenance_ids,
            'driver_stmt_line': driver_stmt_line,
            'expense_line': expense_line,
            'cost_ids': cost_ids,
            'with_expense': expense,
            'date_from': date_from,
            'date_to': date_to,

        }

        return report_obj.render('hiworth_tms.vehicle_details_custom_report', docargs)
