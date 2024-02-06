from openerp import fields, models, api
from datetime import date
from datetime import  datetime,timedelta

class HRDashboard(models.Model):
    _name = 'hr.dashboard'

    def get_total_employee(self):
        total_employee = self.env['hr.employee'].search([])
        self.total_employee =len(total_employee)

    def get_total_supervisor(self):
        total_supervisor = self.env['hr.employee'].search([('user_category','in',['supervisor','super_trainee'])])
        self.total_supervisor = len(total_supervisor)

    def get_total_drivers(self):
        total_driver = self.env['hr.employee'].search([('user_category','in',['driver','eicher_driver','pickup_driver','lmv_driver'])])
        self.total_driver =len(total_driver)
    def get_attendance(self):
        attendance = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('attendance', 'in', ['half', 'full'])])
        
        self.attendance = len(attendance)

    def get_absent(self):
        absent = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('attendance', '=', 'absent')])
        self.absent = len(absent)

        
    def get_leaves_to_approve(self):
        leaves_to_approve = self.env['hr.holidays'].search([('state','=','confirm')])
        self.leaves_to_approve = len(leaves_to_approve)
        
    def get_daily_statements(self):
        daily_statement = self.env['partner.daily.statement'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.daily_statements_approve = len(daily_statement)

    def pending_daily_statements(self):
        self.pending_daily_statement =self.total_supervisor - self.daily_statements_approve   
        
    def get_driver_daily_statements(self):
        driver_daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.driver_daily_statements = len(driver_daily_statement)
    
    def get_pending_driver_statement(self):
        self.pending_driver_statement = self.total_driver - self.driver_daily_statements  

        
    def get_site_purchases(self):
        site_purchases = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', 'in', ['confirm'])])
        self.site_purchases = len(site_purchases)
    
    def get_site_purchase_yesterday(self):
        yesterday_date = date.today() - timedelta(days=1)
        #print 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy',yesterday_date.strftime("%Y-%m-%d %H:%M:%S")
        site_purchases_yesterday = self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', '=', 'confirm')])
        self.site_purchases_yesterday = len(site_purchases_yesterday)

    def get_total_site_purchase_today(self):
        total_purchase = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S"))])
        self.total_site_purchases_today = len(total_purchase)

    def get_total_site_purchase_yesterday(self):
        yesterday_date = date.today() - timedelta(days=1)
        total_purchase_yes = self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S"))])
        self.total_site_purchases_yesterday = len(total_purchase_yes)

    def get_approved_site_purchase_today(self):
        site_purchases_approved = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', 'in', ['approved1','approved2'])])
        self.total_site_purchase_approved_today = len(site_purchases_approved)
    
    def get_approved_site_purchase_yesterday(self):
        yesterday_date = date.today() - timedelta(days=1)
        site_purchases_approved_yes =  self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S")), ('state', 'in',['approved1','approved2'])])
        self.total_site_purchase_approved_yesterday = len(site_purchases_approved_yes)
    def get_events(self):
        task = self.env['event.event'].search([('date_begin', '<=', date.today().strftime("%Y-%m-%d")),
                                               ('date_end', '>=', date.today().strftime("%Y-%m-%d")),
                                               ('state', '=', 'initial')])
        self.events = len(task.ids)
        
    def get_tasks(self):
        task = self.env['project.task'].search([('date_start', '<=', date.today().strftime("%Y-%m-%d")),
                                               ('date_end', '>=', date.today().strftime("%Y-%m-%d")),
                                               ('state', 'in', ['approved','inprogress'])])
        self.tasks = len(task.ids)
        
    def get_next_day_settlement(self):
        next_day_settlement = self.env['nextday.settlement'].search([('date', '=', date.today().strftime("%Y-%m-%d"))])
        self.next_day_settlement = len(next_day_settlement)
        
    def get_prev_attendance(self):
        date_time = date.today() - timedelta(days=1)
        attendance = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('attendance', 'in', ['half', 'full'])])
        self.prev_attendance = len(attendance.ids)

    def get_prev_absent(self):
        date_time = date.today() - timedelta(days=1)
        prevabsent = self.env['hiworth.hr.attendance'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('attendance', '=', 'absent')])
        self.prev_absent = len(prevabsent)


        
    def get_daily_statements_prev(self):
        date_time = date.today() - timedelta(days=1)
        daily_statement = self.env['partner.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.daily_statements_approve_prev = len(daily_statement)

    def pending_yesterday_daily_statements(self):
        self.yes_pending_daily_statement = self.total_supervisor - self.daily_statements_approve_prev

    def pending_yesterday_driver_daily_statements(self):
        self.yes_pending_driver_daily_statement = self.total_driver - self.driver_daily_statements_prev
        
    def get_driver_daily_statements_prev(self):
        date_time = date.today() - timedelta(days=1)
        driver_daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        self.driver_daily_statements_prev = len(driver_daily_statement)
    
    def get_manufacuring_orders(self):
        manufacturing_orders = self.env['mrp.production'].search([('date_planned', '=', date.today().strftime("%Y-%m-%d"))])
        self.todays_manufacturing_orders = len(manufacturing_orders)

    def get_approved_tender(self):
        approved_tender = self.env['hiworth.tender'].search([('state','=','approved')])
        self.todays_approved_tenders = len(approved_tender)

    def get_todays_purchase_order(self):
        confirmed_order = self.env['purchase.order'].search([('date_order','=',date.today().strftime("%Y-%m-%d")),('state','=','approved')])
        self.total_purchase_order = len(confirmed_order)

    def get_todays_purchase_comparisons(self):
        purchase_comparison = self.env['purchase.comparison'].search([('date','=',date.today().strftime("%Y-%m-%d")),('state','=','validated2')])
        self.todays_purchase_comparison = len( purchase_comparison)

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")
    total_employee = fields.Float(string="Total Employee",compute='get_total_employee')
    total_supervisor=fields.Float(string="Total Supervisor",compute='get_total_supervisor')
    total_driver = fields.Float(string="Total Driver",compute ='get_total_drivers')
    pending_daily_statement =fields.Float(string="pending statements",compute='pending_daily_statements')
    pending_driver_statement = fields.Float(string = "pending driver statements",compute ="get_pending_driver_statement")
    yes_pending_daily_statement = fields.Float(string ="yesterday",compute ='pending_yesterday_daily_statements')
    yes_pending_driver_daily_statement = fields.Float(string = "yesterday driver",compute="pending_yesterday_driver_daily_statements")
    attendance = fields.Float(string="Present",compute='get_attendance')
    absent = fields.Float(string='Total Absent',compute='get_absent')
    prev_absent = fields.Float(String = 'Total Absent',compute='get_prev_absent')
    leaves_to_approve = fields.Float(string="Leaves to Approve",compute='get_leaves_to_approve')
    daily_statements_approve = fields.Float(string="Daily Statement Approve", compute='get_daily_statements')
    driver_daily_statements = fields.Float(string="Driver Daily Statement Approve", compute='get_driver_daily_statements')
    site_purchases = fields.Float(string="Site Purchases",
                                           compute='get_site_purchases')
    total_site_purchases_today = fields.Float(string = "Total site purchase today",compute ="get_total_site_purchase_today")
    total_site_purchases_yesterday = fields .Float(string ="Total site purchase yesterday",compute ="get_total_site_purchase_yesterday")
    total_site_purchase_approved_today = fields.Float(string="approved purchase",compute ="get_approved_site_purchase_today")
    total_site_purchase_approved_yesterday = fields.Float(string = "approved purchase yesterday",compute ="get_approved_site_purchase_yesterday")
    site_purchases_yesterday = fields.Float(string = "Site Purchase Yesterday",compute ="get_site_purchase_yesterday")
    events = fields.Float(string="Events",compute='get_events')
    tasks = fields.Float(string="Tasks",compute='get_tasks')
    next_day_settlement = fields.Float(string="Next Day Settlement", compute='get_next_day_settlement')
    prev_attendance = fields.Float(string="Previous Day Attendances", compute='get_prev_attendance')
    daily_statements_approve_prev = fields.Float(string="Daily Statement Approve", compute='get_daily_statements_prev')
    driver_daily_statements_prev = fields.Float(string="Driver Daily Statement Approve",
                                           compute='get_driver_daily_statements_prev')

    todays_manufacturing_orders = fields.Float(string="Todays Manufacturing Orders",
                                           compute='get_manufacuring_orders')
    todays_approved_tenders = fields.Float(string="Approved Tender",compute="get_approved_tender")
    total_purchase_order = fields.Float(string="Purchase_order",compute="get_todays_purchase_order")
    todays_purchase_comparison = fields.Float(string="Purchase Comparison",compute="get_todays_purchase_comparisons")
    @api.multi
    def dashboard_attendance_today(self):
        attendance = self.env['hiworth.hr.attendance'].search([('date','=',date.today().strftime("%Y-%m-%d")),('attendance','in',['half','full'])])

        return {
            'name': "Today's Attendance",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'hiworth.hr.attendance',
           'domain':[('id','in',attendance.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_leave_to_approve(self):
        leaves_to_approve = self.env['hr.holidays'].search([('state', '=', 'confirm')])
        return {
            'name': "Leaves to Approve",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'hr.holidays',
            'domain': [('id', 'in', leaves_to_approve.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_supervisor_daily_statement(self):
        daily_statement = self.env['partner.daily.statement'].search([('date','=',date.today().strftime("%Y-%m-%d")),('state', 'not in', ['draft','cancelled'])])
        return {
            'name': "Today's Supervisor Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'partner.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_driver_daily_statement(self):
        daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date.today().strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        return {
            'name': "Today's Driver Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'driver.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }

    

    @api.multi
    def dashboard_purchase(self):
        total_purchase = self.env['site.purchase'].search([('order_date', '>', date.today().strftime("%Y-%m-%d %H:%M:%S"))])
        return {
            'name': "Today's Purchase",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'site.purchase',
            'domain': [('id', 'in', total_purchase.ids)],
            'type': 'ir.actions.act_window'
        }

    

    @api.multi
    def dashboard_current_inventory(self):
        
        return {
            'name': "Current Inventory Valuation",
            'view_type': 'form',
            'view_mode': 'graph',
            'views': [(False, 'graph')],
            'res_model': 'stock.history',
           
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_project_task(self):
        task = self.env['event.event'].search([('date_begin','<=',date.today().strftime("%Y-%m-%d")),('date_end','>=',date.today().strftime("%Y-%m-%d")),('state','=','initial')])
        
        return {
            'name': "Task",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'event.event',
            'domain':[('id','in',task.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_project_estimation(self):
        task = self.env['project.task'].search([('date_start', '<=', date.today().strftime("%Y-%m-%d")),
                                               ('date_end', '>=', date.today().strftime("%Y-%m-%d")),
                                               ('state', 'in', ['approved','inprogress'])])
    
        return {
            'name': "Task",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'project.task',
            'domain': [('id', 'in', task.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_next_settlement(self):
        next_day_settlement = self.env['nextday.settlement'].search([('date', '=', date.today().strftime("%Y-%m-%d"))])
    
        return {
            'name': "Task",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'nextday.settlement',
            'domain': [('id', 'in', next_day_settlement.ids)],
            'type': 'ir.actions.act_window'
        }

    

    @api.multi
    def dashboard_prev_attendance(self):
        date_time = date.today() - timedelta(days=1)
        attendance = self.env['hiworth.hr.attendance'].search(
            [('date', '=',date_time.strftime("%Y-%m-%d")) , ('attendance', 'in', ['half', 'full'])])
    
        return {
            'name': "Yesterday's Attendance",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'hiworth.hr.attendance',
            'domain': [('id', 'in', attendance.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_bank_details(self):
        banks = self.env['res.partner.bank'].search(
            [('common_usage', '=', True)])
    
        return {
            'name': "Bank Details",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'res.partner.bank',
            'domain': [('id', 'in', banks.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_supervisor_daily_statement_prev(self):
        date_time = date.today() - timedelta(days=1)
        daily_statement = self.env['partner.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        return {
            'name': "Yesterday's Supervisor Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'partner.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_driver_daily_statement_prev(self):
        date_time = date.today() - timedelta(days=1)
        daily_statement = self.env['driver.daily.statement'].search(
            [('date', '=', date_time.strftime("%Y-%m-%d")), ('state', 'not in', ['draft', 'cancelled'])])
        return {
            'name': "Yesterday's Driver Daily Statement",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'driver.daily.statement',
            'domain': [('id', 'in', daily_statement.ids)],
            'type': 'ir.actions.act_window'
        }
        
    @api.multi
    def dashboard_purchase_prev(self):

        yesterday_date = date.today() - timedelta(days=1)
        total_purchase = self.env['site.purchase'].search([('order_date', '>', yesterday_date.strftime("%Y-%m-%d %H:%M:%S")),('order_date', '<', date.today().strftime("%Y-%m-%d %H:%M:%S"))])

        return {
            'name': "Yesterday's Purchase",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'site.purchase',
            'domain': [('id', 'in', total_purchase.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_mo_orders(self):
        manufacturing_orders = self.env['mrp.production'].search([('date_planned', '=', date.today().strftime("%Y-%m-%d"))])
    
        return {
            'name': "Manufacturing Orders",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'mrp.production',
            'domain': [('id', 'in', manufacturing_orders.ids)],
            'type': 'ir.actions.act_window'
        }


    @api.multi
    def dashboard_approved_tenders(self):
        approved_tender = self.env['hiworth.tender'].search([('state','=','approved')])
    
        return {
            'name': "Approved Tenders",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'hiworth.tender',
            'domain': [('id', 'in', approved_tender.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_dpr_status(self):
        dpr_status = self.env['dpr.status'].search([('date','=',date.today().strftime("%Y-%m-%d"))])
    
        return {
            'name': "Dpr Status Planning",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'form')],
            'res_model': 'dpr.status',
            'domain': [('id', 'in', dpr_status.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_dpr_status_survey(self):
        dpr_status_survey = self.env['dpr.status.survey'].search([('date','=',date.today().strftime("%Y-%m-%d"))])
    
        return {
            'name': "Dpr Status Survey",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'form')],
            'res_model': 'dpr.status.survey',
            'domain': [('id', 'in', dpr_status_survey.ids)],
            'type': 'ir.actions.act_window'
        }


    @api.multi
    def dashboard_purchase_order_today(self):
        confirmed_order = self.env['purchase.order'].search([('date_order','=',date.today().strftime("%Y-%m-%d")),('state','=','approved')])
    
        return {
            'name': "Purchase Orders",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'purchase.order',
            'domain': [('id', 'in', confirmed_order.ids)],
            'type': 'ir.actions.act_window'
        }

    @api.multi
    def dashboard_purchase_comparison(self):
        purchase_comparison = self.env['purchase.comparison'].search([('date','=',date.today().strftime("%Y-%m-%d")),('state','=','validated2')])
    
        return {
            'name': "Purchase Comparison",
            'view_type': 'form',
            'view_mode': 'tree,form',
            'views': [(False, 'tree')],
            'res_model': 'purchase.comparison',
            'domain': [('id', 'in',purchase_comparison.ids)],
            'type': 'ir.actions.act_window'
        }