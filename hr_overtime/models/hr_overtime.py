from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, AccessError, UserError
from lxml import etree

class HrOvertime(models.Model):
    _name = "hr.overtime"
    _description = "Overtime Request"
    
    employee_id = fields.Many2one("hr.employee", string="Employee", required=True, default=lambda self: self._get_current_user_employee())
    approver_id = fields.Many2one(
        "res.users", 
        string="Approver", 
        required=True, 
        default=lambda self: self._get_default_approver_id()
    )

    need_second_approver = fields.Boolean(
        "Need Second Approver", 
        default=lambda self: self._get_default_need_second_approver() or False
    )
    second_approver_id = fields.Many2one(
        "res.users", 
        string="Second Approver", 
        default=lambda self:self._get_default_second_approver() or False
    )

    state = fields.Selection([
        ("draft", "Draft"),
        ("to_be_approved", "To Be Approved"),
        ("to_be_second_approved", "To Be Second Approved"),
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ], string="Status", default="draft", track_visibility="onchange", required=True)
    
    overtime_hours = fields.Float("Overtime Hour(s)", default=0.0, required=True)
    date = fields.Date("Date", default=lambda self: fields.Date.today())
    reason = fields.Text("Reason")
    
    can_approve = fields.Boolean('Can Approve', compute='_compute_can_approve')
    can_reject = fields.Boolean('Can Reject', compute='_compute_can_reject')
    can_edit = fields.Boolean("Can Edit", compute="_compute_can_edit")
    
    
    def action_submit(self):
        self.write({"state": "to_be_approved"})
    
    def action_approve(self):
        if self.need_second_approver and self.state == 'to_be_approved':
            self.write({"state": "to_be_second_approved"})
        else:
            self.write({"state": "approved"})
    
    def action_reject(self):
        self.write({"state": "rejected"})
    
    def action_reset_to_draft(self):
        self.write({"state": "draft"})

    def _get_default_permission_tag_id(self):
        setting_obj = self.env['res.config.settings'].create({})
        return setting_obj.get_overtime_permission_tag_id()

    def _get_default_approver_id(self):
        setting_obj = self.env['res.config.settings'].create({})
        return setting_obj.get_overtime_approver_id()
    
    def _get_default_need_second_approver(self):
        setting_obj = self.env['res.config.settings'].create({})
        return setting_obj.get_need_second_approver()
    
    def _get_default_second_approver(self):
        setting_obj = self.env['res.config.settings'].create({})
        return setting_obj.get_overtime_second_approver_id()

    @api.constrains("approver_id", "second_approver_id")
    def _check_duplicate_approver(self):
        for hr_overtime in self:
            if not hr_overtime.approver_id or not hr_overtime.second_approver_id:
                continue

            if hr_overtime.approver_id == hr_overtime.second_approver_id:
                raise ValidationError(_("Approver can't be the same users."))
    
    @api.constrains('overtime_hours')
    def _check_overtime_hours(self):
        for rec in self:
            if (rec.overtime_hours <= 0):
                raise ValidationError(_(
                    "The overtime hours must be greater than 0."
                ))
        
    def _get_current_user_employee(self):
        if self.env.is_superuser():
            return
        
        return self.env.user.employee_id

    @api.depends("state")
    def _compute_can_edit(self):
        for hr_overtime in self:
            try:
                hr_overtime._check_edition_update()
            except(UserError):
                hr_overtime.write({"can_edit": False})
            else:
                hr_overtime.write({"can_edit": True})


    @api.depends("state")
    def _compute_can_reject(self):
        for hr_overtime in self:
            if hr_overtime.state not in ('to_be_approved', 'to_be_second_approved'):
                hr_overtime.write({"can_reject": False})
                continue

            try:
                if hr_overtime.state in ('to_be_approved', 'to_be_second_approved'):
                    hr_overtime._check_approval_update()
            except (AccessError, UserError):
                hr_overtime.write({"can_reject": False})
            else:
                hr_overtime.write({"can_reject": True})

    @api.depends("state")
    def _compute_can_approve(self):
        for hr_overtime in self:
            if hr_overtime.state not in ('to_be_approved', 'to_be_second_approved'):
                hr_overtime.write({"can_approve": False})
                continue

            try:
                if hr_overtime.state in ('to_be_approved', 'to_be_second_approved'):
                    hr_overtime._check_approval_update()
            except (AccessError, UserError):
                hr_overtime.write({"can_approve": False})
            else:
                hr_overtime.write({"can_approve": True})
    
    """
    Check if user is able to approve and reject or not

    :return None
    :exception: Fail to authenticate user will result in error
        - AccessError
        - UserError
    """
    def _check_approval_update(self):
        if self.env.is_superuser():
            return
        
        current_employee = self.env.user

        for hr_overtime in self:
            approver = hr_overtime.approver_id
            second_approver = hr_overtime.second_approver_id

            # Check if state is in the "to_be_approve" or "to_be_second_approve"
            if hr_overtime.state in ('to_be_approved', 'to_be_second_approved'):
                # If it's in the "to_be_approve", we will check it with approver
                if hr_overtime.state == "to_be_approved":
                    if current_employee.id != approver.id:
                        raise UserError(_("You can not use this function."))
                # If it's in the "to_be_second_approve", we will check it with second approver
                elif hr_overtime.state == "to_be_second_approved":
                    if current_employee.id != second_approver.id:
                        raise UserError(_("You can not use this function."))
                else:
                    raise AccessError(_("You can't access this function."))
            # If the state is not satisfy, we will raise error
            else:
                raise AccessError(_("You can't access this function."))

    """
    Check if user is able to edit the data or not

    :return None
    :exception: Fail to authenticate user will result in error
        - AccessError
        - UserError
    """
    def _check_edition_update(self):
        if self.env.is_superuser():
            return
        """
        Check if employee is an admin
        If they are admin, they will have Admin Overtime group
        """
        is_admin = self.env.user.has_group('hr_overtime.group_op_overtime')
        if is_admin:
            return    
        """
        Check if employee have permission to edit
        Get the tag from setting and compare it to employee tag
        """
        employee_tag_objs = self.env.user.employee_id.category_ids
        tag_obj = self._get_default_permission_tag_id()
        for employee_tag in employee_tag_objs:
            if employee_tag == tag_obj:
                return
        """
        Will raise the error if any of the condition above doesn't satisfy
        """
        raise UserError(_(""))
    