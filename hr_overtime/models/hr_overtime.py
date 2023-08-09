from odoo import api, fields, models

class HrOvertime(models.Model):
    _name = "hr.overtime"
    _description = "Overtime Request"
    
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    approver_id = fields.Many2one("res.users", string="Approver", required=True)

    need_second_approver = fields.Boolean("Need Second Approver", default=False)
    second_approver_id = fields.Many2one("res.users", string="Second Approver")

    state = fields.Selection([
        ("draft", "Draft"),
        ("to_be_approve", "To Be Approved"),
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ], string="Status", default="draft", track_visibility="onchange", required=True)
    
    overtime_hours = fields.Float("Overtime Hour(s)", default=0.0, required=True)
    date = fields.Date("Date", default=lambda self: fields.Date.today())
    reason = fields.Text("Reason")
    
    def action_submit(self):
        self.write({"state": "to_be_approve"})
    
    def action_approve(self):
        self.write({"state": "approved"})
    
    def action_reject(self):
        self.write({"state": "rejected"})
    
    def action_reset_to_draft(self):
        self.write({"state": "draft"})