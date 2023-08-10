from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from lxml import etree

class HrOvertime(models.Model):
    _name = "hr.overtime"
    _description = "Overtime Request"
    
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True)
    approver_id = fields.Many2one(
        "res.users", 
        string="Approver", 
        required=True, 
        default=lambda self: self._get_default_approver_id()
    )

    need_second_approver = fields.Boolean(
        "Need Second Approver", 
        default=lambda self: self._get_default_need_second_approver() or False)
    second_approver_id = fields.Many2one("res.users", string="Second Approver")

    state = fields.Selection([
        ("draft", "Draft"),
        ("to_be_approve", "To Be Approved"),
        ("to_be_second_approve", "To Be Second Approved"),
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ], string="Status", default="draft", track_visibility="onchange", required=True)
    
    overtime_hours = fields.Float("Overtime Hour(s)", default=0.0, required=True)
    date = fields.Date("Date", default=lambda self: fields.Date.today())
    reason = fields.Text("Reason")
    
    def action_submit(self):
        self.write({"state": "to_be_approve"})
    
    def action_approve(self):
        if self.need_second_approver and self.state == 'to_be_approve':
            self.write({"state": "to_be_second_approve"})
        else:
            self.write({"state": "approved"})
    
    def action_reject(self):
        self.write({"state": "rejected"})
    
    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def _get_default_approver_id(self):
        setting_obj = self.env['res.config.settings'].create({})
        return setting_obj.get_overtime_approver_id()
    
    def _get_default_need_second_approver(self):
        setting_obj = self.env['res.config.settings'].create({})
        return setting_obj.get_need_second_approver()
    
    @api.constrains('overtime_hours')
    def _check_overtime_hours(self):
        for rec in self:
            if (rec.overtime_hours <= 0):
                raise ValidationError(_(
                    "The overtime hours must be greater than 0."
                ))
    