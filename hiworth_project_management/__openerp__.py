# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Hiworth Project Management',
    'version': '1.1',
    'website': 'https://www.odoo.com/page/project-management',
    'category': 'Project',
    'sequence': 10,
    'summary': 'Projects, Tasks',
    'depends': ['event','hiworth_construction'
    ],
    'description': """
..
    """,
    'data': [
    'security/project_security.xml',
    'views/project.xml',
    'security/res.country.state.csv',
    # 'views/external_signup.xml',
    'security/ir.model.access.csv',
       # 'views/web_login.xml',
       # 'views/auth_signup.xml',
       'security/ir.rule.csv',
       'views/sequence.xml',
       
       'views/index.xml',
       'views/messaging_prime.xml',
       # 'views/project_task.xml',
       # 'views/task_calendar.xml',
       'views/access_project.xml',
       # 'views/popup_notification.xml',
       'views/job_summary.xml',
       'views/customer_file_details.xml',
       'views/work_report.xml',
       'views/account_invoice.xml',
       # 'views/birthday_cron.xml',
       # 'edi/birthday_reminder_action_data.xml',
       # 'views/gallery.xml',
       # 'views/greetings.xml',
       
       # 'views/work_order_contractor.xml'
       # 'views/popup_notification.xml'
       # 'views/im_chat.xml'
       # 'views/website_templates.xml'


        'views/overhead_costing_commercial.xml',
        'views/project_overhead_distribution.xml',
        'views/recurring_expense.xml',
        'views/project_costing_progress_commercial.xml',
        'views/boq_estimated_by_qs.xml',
        'views/boq_excess_order_by_qs.xml',
        'views/work_hours_planned_by_qs.xml',
        'views/marketing.xml',
        'views/marketing_work_sub_plan.xml',
        # 'views/document_collection.xml',
        'report/report_recurring_expense.xml',
        'report/over_head_costing_report.xml',
        'report/costing_and_progress.xml',
        'report/work_hours_planned.xml',
        'report/boq_excess_order.xml',
        'report/boq_estimated_by_qs.xml',
        'report/project_oh.xml',

        'views/tender.xml',

    ],
    
    # 'qweb': [
    #     'static/xml/popup_notification.xml',

    #     'static/src/xml/*.xml',
    #         ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
