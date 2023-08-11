from odoo import api, fields, models

class HrPayslipOvertime(models.Model):
    _inherit = "hr.payslip"

    total_overtime_hr = fields.Float("Total Overtime Hour(s)", compute="_compute_total_overtime_hr")

    @api.depends("employee_id")
    def _compute_total_overtime_hr(self):
        for record in self:
            if not record.employee_id:
                record.total_overtime_hr = 0.0
                continue
            
            employee_obj = self.env['hr.overtime'].search([
                ('employee_id', '=', record.employee_id.id),
                ('date', '<=', record.date_to), 
                ('date', '>=', record.date_from),
                ('state', '=', 'approved')                
            ])

            total_overtime = sum(employee_obj.mapped('overtime_hours'))
            record.total_overtime_hr = total_overtime