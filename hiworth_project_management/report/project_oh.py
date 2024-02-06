from dateutil.relativedelta import *
from openerp import models, fields, api, _
from openerp import tools, _
from datetime import datetime, date, timedelta


class OverheadProjectReport(models.TransientModel):
    _name = 'overhead.project'

    project_id = fields.Many2one('project.project', 'Project Name')
    month_select = fields.Selection(
        [('january', 'January'), ('february', 'February'), ('march', 'March'), ('april', 'April'), ('may', 'May'),
         ('june', 'June'), ('july', 'July'), ('august', 'August'), ('september', 'September'), ('october', 'October'),
         ('november', 'November'), ('december', 'December')], string="Month")
    date_from = fields.Date()
    date_to = fields.Date()

    @api.multi
    def action_overhead_project(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }

        return {
            'name': 'Project Overhead Distribution Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_project_management.report_overhead_project_template',
            'datas': datas,
            'report_type': 'qweb-pdf'
        }

    @api.multi
    def action_overhead_project_view(self):
        datas = {
            'ids': self._ids,
            'model': self._name,
            'form': self.read(),
            'context': self._context,
        }
        return {
            'name': 'Project Overhead Distribution Report',
            'type': 'ir.actions.report.xml',
            'report_name': 'hiworth_project_management.report_overhead_project_template',
            'datas': datas,
            'report_type': 'qweb-html',
        }

    @api.multi
    def get_details(self):
        lst = []
        # lst_dict = []
        date_from = datetime.strptime(self.date_from, "%Y-%m-%d")
        date_to = datetime.strptime(self.date_from, "%Y-%m-%d")

        domain = [('state','not in',['cancelled','close'])]
        if self.date_from:
            domain += [('date', '>=', self.date_from)]
        if self.date_to:
            domain += [('date', '<=', self.date_to)]

        # records = over_head_distribution_obj.search(domain)
        project_domain = [('state','not in',['cancelled','close'])]
        # month_domain = []
        # # if self.month_select:
        # #     month_domain += [('month_select', '=', self.month_select)]
        # overheadcost_ids = overhead_obj.search(month_domain)
        project_obj = self.env['project.project']
        overhead_obj = self.env['overheadcost.commercial']
        over_head_distribution_obj = self.env['projectoverhead.distribution']
        if self.project_id:
            project_domain += [('project_id', '=', self.project_id.id)]
        project_ids = project_obj.search(project_domain, order='id desc')

        jan_overheadcost_ids = overhead_obj.search([('month_select', '=', 'january'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        feb_overheadcost_ids = overhead_obj.search([('month_select', '=', 'february'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        mar_overheadcost_ids = overhead_obj.search([('month_select', '=', 'march'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        apr_overheadcost_ids = overhead_obj.search([('month_select', '=', 'april'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        may_overheadcost_ids = overhead_obj.search([('month_select', '=', 'may'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        jun_overheadcost_ids = overhead_obj.search([('month_select', '=', 'june'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        jul_overheadcost_ids = overhead_obj.search([('month_select', '=', 'july'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        aug_overheadcost_ids = overhead_obj.search([('month_select', '=', 'august'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        sep_overheadcost_ids = overhead_obj.search([('month_select', '=', 'september'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        oct_overheadcost_ids = overhead_obj.search([('month_select', '=', 'october'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        nov_overheadcost_ids = overhead_obj.search([('month_select', '=', 'november'), ('date','>=',self.date_from), ('date','<=',self.date_to)])
        dec_overheadcost_ids = overhead_obj.search([('month_select', '=', 'december'), ('date','>=',self.date_from), ('date','<=',self.date_to)])

        jan_monthly_overhead_sum = sum(jan_overheadcost_ids.mapped('actual_value'))
        feb_monthly_overhead_sum = sum(feb_overheadcost_ids.mapped('actual_value'))
        mar_monthly_overhead_sum = sum(mar_overheadcost_ids.mapped('actual_value'))
        apr_monthly_overhead_sum = sum(apr_overheadcost_ids.mapped('actual_value'))
        may_monthly_overhead_sum = sum(may_overheadcost_ids.mapped('actual_value'))
        jun_monthly_overhead_sum = sum(jun_overheadcost_ids.mapped('actual_value'))
        jul_monthly_overhead_sum = sum(jul_overheadcost_ids.mapped('actual_value'))
        aug_monthly_overhead_sum = sum(aug_overheadcost_ids.mapped('actual_value'))
        sep_monthly_overhead_sum = sum(sep_overheadcost_ids.mapped('actual_value'))
        oct_monthly_overhead_sum = sum(oct_overheadcost_ids.mapped('actual_value'))
        nov_monthly_overhead_sum = sum(nov_overheadcost_ids.mapped('actual_value'))
        dec_monthly_overhead_sum = sum(dec_overheadcost_ids.mapped('actual_value'))

        # jan_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<=',date_from+timedelta(month=1))])
        jan_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+1))])
        feb_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+2))])
        mar_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+3))])
        apr_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+4))])
        may_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+5))])
        jun_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+6))])
        jul_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+7))])
        aug_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+8))])
        sep_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+9))])
        oct_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+10))])
        nov_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<',date_from+relativedelta(months=+11))])
        dec_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<=',date_from+relativedelta(months=+11)+timedelta(days=30))])
        # dec_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close']),('start_date','<=',date_from+relativedelta(months=+11))])

        # jan_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'January' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # feb_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'February' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # mar_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'March' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # apr_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'April' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # may_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'May' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # jun_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'June' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # jul_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'July' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # aug_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'August' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # sep_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'September' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # oct_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'October' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # nov_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'November' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)
        # dec_project_ids = project_obj.search([('state', 'not in', ['cancelled', 'close'])]).filtered(
        #     lambda l: datetime.strptime(l.start_date, "%Y-%m-%d").strftime('%B') == 'December' and datetime.strptime(
        #         l.start_date, "%Y-%m-%d").year <= date_from.year)

        jan_project_cost_sum = sum(jan_project_ids.mapped('project_value'))
        feb_project_cost_sum = sum(feb_project_ids.mapped('project_value'))
        mar_project_cost_sum = sum(mar_project_ids.mapped('project_value'))
        apr_project_cost_sum = sum(apr_project_ids.mapped('project_value'))
        may_project_cost_sum = sum(may_project_ids.mapped('project_value'))
        jun_project_cost_sum = sum(jun_project_ids.mapped('project_value'))
        jul_project_cost_sum = sum(jul_project_ids.mapped('project_value'))
        aug_project_cost_sum = sum(aug_project_ids.mapped('project_value'))
        sep_project_cost_sum = sum(sep_project_ids.mapped('project_value'))
        oct_project_cost_sum = sum(oct_project_ids.mapped('project_value'))
        nov_project_cost_sum = sum(nov_project_ids.mapped('project_value'))
        dec_project_cost_sum = sum(dec_project_ids.mapped('project_value'))
        
        for project in project_ids:

            project_cost = project.project_value
            
            jan_weightage = 0
            feb_weightage = 0
            mar_weightage = 0
            apr_weightage = 0
            may_weightage = 0
            jun_weightage = 0
            jul_weightage = 0
            aug_weightage = 0
            sep_weightage = 0
            oct_weightage = 0
            nov_weightage = 0
            dec_weightage = 0
            if project in jan_project_ids:
                jan_weightage = (project_cost * 100)/jan_project_cost_sum
            if project in feb_project_ids:
                feb_weightage = (project_cost * 100)/feb_project_cost_sum
            if project in mar_project_ids:
                mar_weightage = (project_cost * 100)/mar_project_cost_sum
            if project in apr_project_ids:
                apr_weightage = (project_cost * 100)/apr_project_cost_sum
            if project in may_project_ids:
                may_weightage = (project_cost * 100)/may_project_cost_sum
            if project in jun_project_ids:
                jun_weightage = (project_cost * 100)/jun_project_cost_sum
            if project in jul_project_ids:
                jul_weightage = (project_cost * 100)/jul_project_cost_sum
            if project in aug_project_ids:
                aug_weightage = (project_cost * 100)/aug_project_cost_sum
            if project in sep_project_ids:
                sep_weightage = (project_cost * 100)/sep_project_cost_sum
            if project in oct_project_ids:
                oct_weightage = (project_cost * 100)/oct_project_cost_sum
            if project in nov_project_ids:
                nov_weightage = (project_cost * 100)/nov_project_cost_sum
            if project in dec_project_ids:
                dec_weightage = (project_cost * 100)/dec_project_cost_sum


            jan_over_head_distribution_sum = 0
            feb_over_head_distribution_sum = 0
            mar_over_head_distribution_sum = 0
            apr_over_head_distribution_sum = 0
            may_over_head_distribution_sum = 0
            jun_over_head_distribution_sum = 0
            jul_over_head_distribution_sum = 0
            aug_over_head_distribution_sum = 0
            sep_over_head_distribution_sum = 0
            oct_over_head_distribution_sum = 0
            nov_over_head_distribution_sum = 0
            dec_over_head_distribution_sum = 0

            if jan_weightage > 0:
                jan_over_head_distribution_sum = jan_monthly_overhead_sum * jan_weightage/100
            if feb_weightage > 0:
                feb_over_head_distribution_sum = feb_monthly_overhead_sum * feb_weightage/100
            if mar_weightage > 0:
                mar_over_head_distribution_sum = mar_monthly_overhead_sum * mar_weightage/100
            if apr_weightage > 0:
                apr_over_head_distribution_sum = apr_monthly_overhead_sum * apr_weightage/100
            if may_weightage > 0:
                may_over_head_distribution_sum = may_monthly_overhead_sum * may_weightage/100
            if jun_weightage > 0:
                jun_over_head_distribution_sum = jun_monthly_overhead_sum * jun_weightage/100
            if jul_weightage > 0:
                jul_over_head_distribution_sum = jul_monthly_overhead_sum * jul_weightage/100
            if aug_weightage > 0:
                aug_over_head_distribution_sum = aug_monthly_overhead_sum * aug_weightage/100
            if sep_weightage > 0:
                sep_over_head_distribution_sum = sep_monthly_overhead_sum * sep_weightage/100
            if oct_weightage > 0:
                oct_over_head_distribution_sum = oct_monthly_overhead_sum * oct_weightage/100
            if nov_weightage > 0:
                nov_over_head_distribution_sum = nov_monthly_overhead_sum * nov_weightage/100
            if dec_weightage > 0:
                dec_over_head_distribution_sum = dec_monthly_overhead_sum * dec_weightage/100


            # jan_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'january'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # feb_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'february'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # mar_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'march'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # apr_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'april'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # may_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'may'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # jun_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'june'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # jul_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'july'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # aug_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'august'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # sep_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'september'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # oct_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'october'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # nov_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'november'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))
            # dec_over_head_distribution_sum = sum(over_head_distribution_obj.search([('project_id', '=', project.id),('month_select', '=', 'december'), ('date','>=',self.date_from), ('date','<=',self.date_to)]).mapped('actual_value'))

            weightage = 0

            # jan_weightage = (jan_over_head_distribution_sum*100)/jan_monthly_overhead_sum
            # feb_weightage = (feb_over_head_distribution_sum*100)/feb_monthly_overhead_sum
            # mar_weightage = (mar_over_head_distribution_sum*100)/mar_monthly_overhead_sum
            # apr_weightage = (apr_over_head_distribution_sum*100)/apr_monthly_overhead_sum
            # may_weightage = (may_over_head_distribution_sum*100)/may_monthly_overhead_sum
            # jun_weightage = (jun_over_head_distribution_sum*100)/jun_monthly_overhead_sum
            # jul_weightage = (jul_over_head_distribution_sum*100)/jul_monthly_overhead_sum
            # aug_weightage = (aug_over_head_distribution_sum*100)/aug_monthly_overhead_sum
            # sep_weightage = (sep_over_head_distribution_sum*100)/sep_monthly_overhead_sum
            # oct_weightage = (oct_over_head_distribution_sum*100)/oct_monthly_overhead_sum
            # nov_weightage = (nov_over_head_distribution_sum*100)/nov_monthly_overhead_sum
            # dec_weightage = (dec_over_head_distribution_sum*100)/dec_monthly_overhead_sum

            if dec_weightage > 0:
                weightage = dec_weightage
            elif nov_weightage > 0:
                weightage = nov_weightage
            elif oct_weightage > 0:
                weightage = oct_weightage
            elif sep_weightage > 0:
                weightage = sep_weightage
            elif aug_weightage > 0:
                weightage = aug_weightage
            elif jul_weightage > 0:
                weightage = jul_weightage
            elif jun_weightage > 0:
                weightage = jun_weightage
            elif may_weightage > 0:
                weightage = may_weightage
            elif apr_weightage > 0:
                weightage = apr_weightage
            elif mar_weightage > 0:
                weightage = mar_weightage
            elif feb_weightage > 0:
                weightage = feb_weightage
            elif jan_weightage > 0:
                weightage = jan_weightage

            dict = {
                'project': project.name,
                'project_cost':project_cost,
                'weightage': round(weightage,2),
                'jan_weightage': round(jan_weightage,2),
                'feb_weightage': round(feb_weightage,2),
                'mar_weightage': round(mar_weightage,2),
                'apr_weightage': round(apr_weightage,2),
                'may_weightage': round(may_weightage,2),
                'jun_weightage': round(jun_weightage,2),
                'jul_weightage': round(jul_weightage,2),
                'aug_weightage': round(aug_weightage,2),
                'sep_weightage': round(sep_weightage,2),
                'oct_weightage': round(oct_weightage,2),
                'nov_weightage': round(nov_weightage,2),
                'dec_weightage': round(dec_weightage,2),
                'jan':round(jan_over_head_distribution_sum,2),
                'feb':round(feb_over_head_distribution_sum,2),
                'mar':round(mar_over_head_distribution_sum,2),
                'apr':round(apr_over_head_distribution_sum,2),
                'may':round(may_over_head_distribution_sum,2),
                'jun':round(jun_over_head_distribution_sum,2),
                'jul':round(jul_over_head_distribution_sum,2),
                'aug':round(aug_over_head_distribution_sum,2),
                'sep':round(sep_over_head_distribution_sum,2),
                'oct':round(oct_over_head_distribution_sum,2),
                'nov':round(nov_over_head_distribution_sum,2),
                'dec':round(dec_over_head_distribution_sum,2),
                'total':round((jan_over_head_distribution_sum+feb_over_head_distribution_sum+
                         mar_over_head_distribution_sum+mar_over_head_distribution_sum+
                         may_over_head_distribution_sum+jun_over_head_distribution_sum+
                         jul_over_head_distribution_sum+aug_over_head_distribution_sum+
                         sep_over_head_distribution_sum+oct_over_head_distribution_sum+
                         nov_over_head_distribution_sum+dec_over_head_distribution_sum),2)
            }

            lst.append(dict)
        # lst.append({
        #             'jan_monthly_overhead_sum':jan_monthly_overhead_sum,
        #             'feb_monthly_overhead_sum':feb_monthly_overhead_sum,
        #             'mar_monthly_overhead_sum':mar_monthly_overhead_sum,
        #             'apr_monthly_overhead_sum':apr_monthly_overhead_sum,
        #             'may_monthly_overhead_sum':may_monthly_overhead_sum,
        #             'jun_monthly_overhead_sum':jun_monthly_overhead_sum,
        #             'jul_monthly_overhead_sum':jul_monthly_overhead_sum,
        #             'aug_monthly_overhead_sum':aug_monthly_overhead_sum,
        #             'sep_monthly_overhead_sum':sep_monthly_overhead_sum,
        #             'oct_monthly_overhead_sum':oct_monthly_overhead_sum,
        #             'nov_monthly_overhead_sum':nov_monthly_overhead_sum,
        #             'dec_monthly_overhead_sum':dec_monthly_overhead_sum,})
        return lst



        # # jan_project_ids = project_obj.search([('state','not in',['cancelled','close']), ('start_date','')])
        # # feb_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # mar_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # apr_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # may_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # jun_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # jul_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # aug_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # sep_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # oct_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # nov_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        # # dec_project_ids = project_obj.search([('state','not in',['cancelled','close'])])
        #
        #
        #
        # # jan_flag = False
        # jan_project_cost = 0
        # for record in jan_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     jan_project_cost += project_cost
        #     if record == project:
        #         jan_flag = True
        # # if jan_flag:
        # #     jan_weightage =0
        #
        # feb_project_cost = 0
        # for record in feb_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     feb_project_cost += project_cost
        #
        # mar_project_cost = 0
        # for record in mar_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     mar_project_cost += project_cost
        #
        # apr_project_cost = 0
        # for record in apr_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     apr_project_cost += project_cost
        #
        # may_project_cost = 0
        # for record in may_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     may_project_cost += project_cost
        #
        # jun_project_cost = 0
        # for record in jun_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     jun_project_cost += project_cost
        #
        # jul_project_cost = 0
        # for record in jul_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     jul_project_cost += project_cost
        #
        # aug_project_cost = 0
        # for record in aug_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     aug_project_cost += project_cost
        #
        # sep_project_cost = 0
        # for record in sep_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     sep_project_cost += project_cost
        #
        # oct_project_cost = 0
        # for record in oct_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     oct_project_cost += project_cost
        #
        # nov_project_cost = 0
        # for record in nov_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     nov_project_cost += project_cost
        #
        # dec_project_cost = 0
        # for record in dec_project_ids:
        #     project_cost = over_head_distribution_obj.search([('project_id', '=', record.id)], limit=1,
        #                                                      order='id desc').project_value
        #     dec_project_cost += project_cost



        #
        # for rec in records:
        #     jan, feb, mar, apr, may, june, july, aug, sep, oct, nov, dec = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        # jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        #     vals_sample = {
        #         'project_id': rec.project_id.id,
        #     }
        #     if vals_sample not in lst_dict:
        #         # print("you there??")
        #         if rec.month_select == 'january':
        #             jan = rec.actual_value
        #         if rec.month_select == 'february':
        #             feb = rec.actual_value
        #         if rec.month_select == 'march':
        #             mar = rec.actual_value
        #         if rec.month_select == 'april':
        #             apr = rec.actual_value
        #         if rec.month_select == 'may':
        #             may = rec.actual_value
        #         if rec.month_select == 'june':
        #             june = rec.actual_value
        #         if rec.month_select == 'july':
        #             july = rec.actual_value
        #         if rec.month_select == 'august':
        #             aug = rec.actual_value
        #         if rec.month_select == 'september':
        #             sep = rec.actual_value
        #         if rec.month_select == 'october':
        #             oct = rec.actual_value
        #         if rec.month_select == 'november':
        #             nov = rec.actual_value
        #         if rec.month_select == 'december':
        #             dec = rec.actual_value
        #
        #         vals = {
        #             'pid': rec.project_id.id,
        #             'project_id': rec.project_id.name,
        #             'project_value': rec.project_value,
        #             'row_percentage': 0,
        #             'jan': jan,
        #             'feb': feb,
        #             'mar': mar,
        #             'apr': apr,
        #             'may': may,
        #             'june': june,
        #             'july': july,
        #             'aug': aug,
        #             'sep': sep,
        #             'oct': oct,
        #             'nov': nov,
        #             'dec': dec,
        #             'total': 0,
        #             'e_total_project_val': 0,
        #             'per_total': 0,
        #             'jan_total': 0,
        #             'feb_total': 0,
        #             'mar_total': 0,
        #             'may_total': 0,
        #             'june_total': 0,
        #             'july_total': 0,
        #             'aug_total': 0,
        #             'sep_total': 0,
        #             'oct_total': 0,
        #             'nov_total': 0,
        #             'dec_total': 0,
        #             'grand_total': 0,
        #
        #         }
        #         lst.append(vals)
        #         lst_dict.append(vals_sample)
        #     else:
        #         for dict in lst:
        #             if dict['pid'] == rec.project_id.id:
        #                 if rec.month_select == 'january':
        #                     dict['jan'] = rec.actual_value
        #                 if rec.month_select == 'february':
        #                     dict['feb'] = rec.actual_value
        #                 if rec.month_select == 'march':
        #                     dict['mar'] = rec.actual_value
        #                 if rec.month_select == 'april':
        #                     dict['apr'] = rec.actual_value
        #                 if rec.month_select == 'may':
        #                     dict['may'] = rec.actual_value
        #                 if rec.month_select == 'june':
        #                     dict['june'] = rec.actual_value
        #                 if rec.month_select == 'july':
        #                     dict['july'] = rec.actual_value
        #                 if rec.month_select == 'august':
        #                     dict['aug'] = rec.actual_value
        #                 if rec.month_select == 'september':
        #                     dict['sep'] = rec.actual_value
        #                 if rec.month_select == 'october':
        #                     dict['oct'] = rec.actual_value
        #                 if rec.month_select == 'november':
        #                     dict['nov'] = rec.actual_value
        #                 if rec.month_select == 'december':
        #                     dict['dec'] = rec.actual_value
        #                 dict['total'] = jan + feb + mar + apr + may + june + july + aug + sep + oct + nov + dec
        # sum1, row_percentage, jan_total, feb_total, mar_total, apr_total, may_total, june_total, july_total, aug_total, sep_total, oct_total, nove_total, dec_total, grand_total = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        # for dict in lst:
        #     dict['total'] = dict['jan'] + dict['feb'] + dict['mar'] + dict['apr'] + dict['may'] + dict['june'] + dict[
        #         'july'] + dict['aug'] + dict['sep'] + dict['oct'] + dict['nov'] + dict['dec']
        #     sum1 = sum1 + dict['project_value']
        #     dict['row_percentage'] = round(((dict['total']/dict['project_value'])*100),2)
        #     # sum2 = sum2 + dict['e_amount_month']
        #     jan_total = jan_total + dict['jan']
        #     feb_total = feb_total + dict['feb']
        #     mar_total = mar_total + dict['mar']
        #     apr_total = apr_total + dict['apr']
        #     may_total = may_total + dict['may']
        #     june_total = june_total + dict['june']
        #     july_total = july_total + dict['july']
        #     aug_total = aug_total + dict['aug']
        #     sep_total = sep_total + dict['sep']
        #     oct_total = oct_total + dict['oct']
        #     nove_total = nove_total + dict['nov']
        #     dec_total = dec_total + dict['dec']
        #     grand_total = grand_total + dict['total']
        #
        # for dict in lst:
        #     dict['e_totalproject_value'] = sum1
        #     dict['jan_total'] = jan_total
        #     dict['feb_total'] = feb_total
        #     dict['mar_total'] = mar_total
        #     dict['apr_total'] = apr_total
        #     dict['may_total'] = may_total
        #     dict['june_total'] = june_total
        #     dict['july_total'] = july_total
        #     dict['aug_total'] = aug_total
        #     dict['sep_total'] = sep_total
        #     dict['oct_total'] = oct_total
        #     dict['nove_total'] = nove_total
        #     dict['dec_total'] = dec_total
        #     dict['grand_total'] = grand_total
        #     dict['per_total'] = round((dict['grand_total']/dict['e_totalproject_value'])*100,2)
        #     # print("wewrtewrew", dict['e_amount_month_total'])
        #     # print("qqqqqqqqqqqqqqq", dict['grand_total'])
        # return lst
