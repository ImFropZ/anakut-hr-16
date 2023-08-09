from odoo import api, fields, models

class HrPayroll(models.Model):
    _inherit = "hr.payslip"

    total_overtime_hr = fields.Float()

    @api.depends(["employee_id"])
    def _compute_total_overtime_hr(self):
        pass