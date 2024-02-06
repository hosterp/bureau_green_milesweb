from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class VehicleRentVehicleExpenseWizard(models.TransientModel):
    _name = 'vehicle.rent.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')

    @api.multi
    def action_vehicle_rent_open_window(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Vehicle Site Expense Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_tms.report_fleet_vehicle_rent_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def get_details(self):
        d1 = self.date_from
        d2 = self.date_to
        d1 = datetime.strptime(d1, "%Y-%m-%d")
        d2 = datetime.strptime(d2, "%Y-%m-%d")
        no_days1 = abs((d2 - d1).days)
        no_days = no_days1 + 1
        lst = []
        vehicle_lst = []
        driver_stmts = self.env['driver.daily.statement'].search(
            [('date', '>=', self.date_from), ('date', '<=', self.date_to)])
        if driver_stmts:
            print("foundddddddddddddddddddddddddddddddddddddddddddddd", no_days)

        else:
            print("not found....................")
        # main
        for rec in driver_stmts:
            veh = rec.vehicle_no.id
            if veh not in vehicle_lst:
                no_of_loads = 0
                t_rent = 0
                t_km = 0
                total_diesel = 0
                total_amt = 0
                total_sal_driver = 0
                total_fd_exp = 0
                worked_days = 0
                test_var=0
                test_var2 =0
                for items in rec.diesel_pump_line:
                    ltr = items.litre
                    total_diesel = total_diesel + ltr
                    total_amt = total_amt + items.total_litre_amount
                    per_day_rent = 0
                print("total diesel1", total_diesel)

                for lines in rec.driver_stmt_line:

                    test_var = lines.driver_betha
                    test_var2 = lines.item_expense2.name
                    no_of_loads = no_of_loads + 1
                    # rent = lines.rent
                    # t_rent = t_rent + lines.rent
                    t_km = t_km + lines.total_km
                    total_sal_driver = (total_sal_driver + lines.driver_betha)
                total_fd_exp = total_fd_exp + 150
                # per_day_rent = rent
                rent = rec.rent_amount
                t_rent = rent * (worked_days + 1)
                row_total =0
                vals = {
                    'reg_no': rec.vehicle_no.name,
                    'vehicle_no':rec.vehicle_no,
                    'veh_id': rec.vehicle_no.id,
                    'owner': rec.vehicle_no.vehicle_under.name,
                    'wheel': rec.vehicle_no.no_of_tyres,
                    'type': rec.vehicle_no.model_id.name,
                    # 'date':rec.date,
                    'no_days_worked': worked_days + 1,
                    'rent_per_day': rent,
                    'rent_total': t_rent,
                    'km': t_km,
                    'daily_sal_driver': test_var,
                    'total_sal_driver': total_sal_driver,
                    'material': test_var2,
                    'no_loads': no_of_loads,
                    'total_fd_exp': total_fd_exp,
                    'total_diesel': total_diesel,
                    'total_diesel_amt': total_amt,
                    'absent_days': no_days - 1,
                    'no_days': no_days,
                    'row_total': (total_amt+total_sal_driver+t_rent+total_fd_exp),
                    'sub_total': 0,
                    'sum1_profit': 0,
                    'loss': 0,
                    'net': 0,
                    'diesel_sum': 0,
                    'diesel_amt_sum': 0,
                    'km_sum': 0,
                    'rent_sum': 0,
                    'sal_sum': 0,
                    'food_sum': 0,
                    'mileage': 0,

                }
                lst.append(vals)
                vehicle_lst.append(rec.vehicle_no.id)

                print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq", vals['row_total'])

            else:
                no_of_loads = 0
                t_rent = 0
                t_km = 0
                total_diesel = 0
                total_amt = 0
                total_sal_driver = 0
                total_fd_exp = 0
                worked_days = 0
                row_total = 0
                for items in rec.diesel_pump_line:
                    total_diesel = total_diesel + items.litre
                    total_amt = total_amt + items.total_litre_amount
                print("total diesel2", total_diesel)

                for lines in rec.driver_stmt_line:
                    no_of_loads = no_of_loads + 1
                    # rent = lines.rent
                    # t_rent = t_rent + lines.rent
                    t_km = t_km + lines.total_km
                    total_sal_driver = (total_sal_driver + lines.driver_betha)
                total_fd_exp = total_fd_exp + 150
                # per_day_rent = rent
                rent = rec.rent_amount
                # t_rent = rent * worked_days+1
                # print("totalllllllllllllllllllllllllll rentttttttt",t_rent)
                item_copy = rec.vehicle_no.id
                for dicts in lst:
                    print("1111111111111111111111111111111111111111111111111111111111111111111111")
                    if item_copy == dicts['veh_id']:
                        if item_copy:
                            # old_rent_total = dicts['rent_total']
                            # new_rent_total = old_rent_total + t_rent
                            # dicts['rent_total'] = new_rent_total

                            row_total = (total_amt + total_sal_driver + t_rent + total_fd_exp)

                            old_driver_sal = dicts['total_sal_driver']
                            new_driver_sal = old_driver_sal + total_sal_driver
                            dicts['total_sal_driver'] = new_driver_sal

                            old_km = dicts['km']
                            new_km = old_km + t_km
                            dicts['km'] = new_km

                            old_loads = dicts['no_loads']
                            new_loads = old_loads + no_of_loads
                            dicts['no_loads'] = new_loads
                            total_fd_exp

                            old_f = dicts['total_fd_exp']
                            new_f = old_f + total_fd_exp
                            dicts['total_fd_exp'] = new_f

                            old_diesel = dicts['total_diesel']
                            new_d = old_diesel + total_diesel
                            dicts['total_diesel'] = new_d
                            print("new diesel total", new_d)

                            old_abs = dicts['absent_days']
                            old_w1days = dicts['no_days_worked']
                            new_abs = old_abs - 1
                            dicts['absent_days'] = new_abs

                            old_amt = dicts['total_diesel_amt']
                            new_amt = old_amt + total_amt
                            dicts['total_diesel_amt'] = new_amt

                            old_wdays = dicts['no_days_worked']
                            new_d = old_wdays + 1
                            dicts['no_days_worked'] = new_d
                            old_rent_total = dicts['rent_total']

                            new_rent_total = rent * new_d
                            dicts['rent_total'] = new_rent_total

                            row_t = new_rent_total+new_amt

                            old_row = dicts['row_total']
                            new_row = row_t +old_row+new_driver_sal+new_f
                            dicts['row_total'] = new_row
        subtotal=0
        sum=0
        profit_sum =0
        loss=0
        net_diff =0
        d_s =0
        d_m =0
        t_km =0
        r_s =0
        s_s =0
        f_s =0
        mileage =0

        for vals in lst:
            sum = (vals['rent_total']+vals['total_diesel_amt']+vals['total_fd_exp']+vals['total_sal_driver'])
            absent = vals['absent_days']
            loss = loss + (absent * vals['rent_per_day'])
            subtotal = subtotal + sum
            # net_diff = (vals['rent_total']-vals['total_diesel_amt']-vals['total_fd_exp'])
            net_diff = vals['rent_total']-(vals['rent_per_day']*vals['absent_days']+vals['total_sal_driver']+vals['total_fd_exp'])-(vals['total_fd_exp']+vals['total_sal_driver']+vals['rent_total']+vals['total_diesel_amt'])
            profit_sum = profit_sum + net_diff
            diesel_ltr = vals['total_diesel']
            d_s = d_s + diesel_ltr
            diesel_amt = vals['total_diesel_amt']
            d_m = d_m + diesel_amt
            tot_km = vals['km']
            t_km =t_km + tot_km
            re_total = vals['rent_total']
            r_s = r_s+ re_total
            salary_sum = vals['total_sal_driver']
            s_s = s_s + salary_sum
            fd_sum = vals['total_fd_exp']
            f_s =f_s+fd_sum



        for vals in lst:
            vals['sub_total'] = subtotal
            vals['sum1_profit'] = profit_sum
            vals['loss'] = loss
            vals['net'] = vals['sum1_profit']-vals['loss']
            vals['diesel_sum'] = d_s
            vals['diesel_amt_sum'] = d_m
            vals['km_sum'] = t_km
            vals['rent_sum'] = r_s
            vals['sal_sum'] = s_s
            vals['food_sum'] = f_s

            vehi_id = vals['vehicle_no']
            d1 = vals['total_diesel']
            k1 = vals['km']
            t = vehi_id.is_a_mach
            if (t == True):
                if (k1 != 0):
                    mileage = round((d1 / k1), 2)
                else:
                    mileage = 0
            else:
                if (d1 != 0):
                    mileage = round((k1 / d1), 2)
                else:
                    mileage = 0

            vals['mileage'] = mileage
        return lst
