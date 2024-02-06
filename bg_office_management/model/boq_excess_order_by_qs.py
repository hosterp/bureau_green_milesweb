from openerp import models, fields, api, _


class BoqExcessOrderByQs(models.Model):
    _name = 'boq.excessorder.qs'
    _rec_name = 'project_id'

    project_id = fields.Many2one('project.project', 'Project Name')
    overhead_category = fields.Many2one('overhead.category', 'Category')
    overhead_sub_category = fields.Many2one('overhead.subcategory', 'Sub Category')
    material = fields.Many2one('product.product','Material')
    description = fields.Char('Description')
    qty = fields.Integer('Quantity')
    unit = fields.Many2one('product.uom','Unit')
    measure_length = fields.Float('Measure Length')
    unit_cost = fields.Float('Unit Cost')
    remarks = fields.Text('Remarks')







