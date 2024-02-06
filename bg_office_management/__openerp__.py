{
    'name': 'BG Office Management',
    'description': 'office management forms,tender,surveys etc',
    'author': 'hiworth',
    'depends': [

        'hiworth_project_management'
    ],
    'data': [

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

    ],
    'installable': True
}