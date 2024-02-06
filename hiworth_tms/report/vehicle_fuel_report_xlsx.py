from openerp import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.addons.report_xlsx.report.report_xlsx import ReportXlsx


class ReportDailyProgressReport(models.TransientModel):
    _name = 'report.vehicle.fuel.report'

    @api.multi
    def generate_xls_report(self):

        return self.env["report"].get_action(self, report_name='custom.vehicle_fuel_report.xlsx')

class BillReportXlsx(ReportXlsx):
    def generate_xlsx_report(self, workbook, data, invoices):
        vehicle_obj = self.env['diesel.pump.line'].search([])
        vehicle_det =[]
        vehicle_lst = []
        for vehicles in vehicle_obj:
            print("vehicles are.......",vehicles.vehicle_id)
            item = vehicles.vehicle_id

            if item not in vehicle_lst:
                if item:
                    vehicle_vals = ({
                        'vehicle_id': vehicles.vehicle_id.name,
                        'diesel_ltr': vehicles.litre,
                        'diesel_price': vehicles.total_litre_amount,
                        'total_km': vehicles.total_odometer,
                    })
                    vehicle_det.append(vehicle_vals)
                    vehicle_lst.append(vehicles.vehicle_id)
            else :
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
        print("here we are....",vehicle_det)
        worksheet = workbook.add_worksheet("Site")
        # raise UserError(str(invoices.invoice_no.id))

        boldc = workbook.add_format(
            {'bold': True, 'align': 'center', 'bg_color': '#D3D3D3', 'font': 'height 10', 'border': 1})
        boldlwb = workbook.add_format(
            {'bold': True, 'align': 'left', 'valign': 'top', 'bg_color': '#ffffff ', 'font': 'height 20', 'right': 1})
        boldlbborder = workbook.add_format(
            {'bold': True, 'align': 'left', 'valign': 'top', 'bg_color': '#ffffff ', 'font': 'height 10', 'bottom': 1,
             'right': 1})
        boldl = workbook.add_format(
            {'bold': True, 'align': 'left', 'valign': 'top', 'bg_color': '#ffffff ', 'font': 'height 10', 'border': 1})
        boldm = workbook.add_format(
            {'bold': True, 'align': 'left', 'valign': 'vcenter', 'bg_color': '#ffffff ', 'font': 'height 10'})
        boldb = workbook.add_format(
            {'bold': True, 'align': 'left', 'valign': 'bottom', 'bg_color': '#ffffff ', 'font': 'height 10',
             'border': 1})
        heading_format = workbook.add_format({'bold': True, 'align': 'left', 'size': 20})
        bold = workbook.add_format({'bold': True, 'align': 'center', 'size': 8, 'text_wrap': True, })
        rightb = workbook.add_format({'align': 'right', 'bold': True})
        right = workbook.add_format({'align': 'right'})
        regular = workbook.add_format({'align': 'center', 'bold': False, 'size': 8})
        merge_format = workbook.add_format({
            'bold': 1,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D3D3D3',
            'font_color': '#000000',
        })
        format_hidden = workbook.add_format({
            'hidden': True
        })
        align_format = workbook.add_format({
            'align': 'right',
        }
        )
        # worksheet.write(5, 0, ('Vehicle Number'), boldc)
        worksheet.merge_range('A1:F2', "TTK CONSTRUCTION",heading_format )
        worksheet.set_column(5 , 0, 30)
        worksheet.write(5, 0, ('Vehicle Number'), boldc)
        worksheet.write(5, 1,('Total Fuel'), boldc)
        worksheet.write(5, 2, ('Total Amount'), boldc)
        # worksheet.write(5, 3, ('Total KM'), boldc)

        row = 6
        for dicts in vehicle_det:
            v_id = dicts['vehicle_id']
            v_ltr = dicts['diesel_ltr']
            v_price = dicts['diesel_price']
            v_km = dicts['total_km']
            print("PYTHON",v_id)
            print("PYTHON",v_ltr)
            print("PYTHON",v_price)
            print("PYTHON",v_km)
            worksheet.write(row, 0, v_id, boldc)
            worksheet.write(row, 1, v_ltr, boldc)
            worksheet.write(row, 2, v_price, boldc)
            # worksheet.write(row, 3, 1, boldc)
            row += 1


BillReportXlsx('report.custom.vehicle_fuel_report.xlsx', 'report.vehicle.fuel.report')


