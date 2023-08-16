from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError

class HrMissionForm(models.Model):
    _name = "hr.mission.form"
    _description = "Mission Form Request"

    employee_ids = fields.Many2many("hr.employee")

    start_date = fields.Date() 
    end_date = fields.Date()

    target_name = fields.Text("Target Name")
    goal = fields.Text("Goal")

    expense = fields.Monetary("Expense of mission")

    need_second_approver = fields.Boolean("Need second approver?")
    approver_id = fields.Many2one(
        "res.users",
        string="Approver",
        required=True, 
        default=lambda self: self._get_default_approver_id()
    )
    second_approver_id = fields.Many2one("res.users")

    state = fields.Selection([
        ("draft", "Draft"),
        ("to_be_approved", "To Be Approved"),
        ("to_be_second_approved", "To Be Second Approved"),
        ("approved", "Approved"),
        ("rejected", "Rejected")
    ], string="Status", default="draft", track_visibility="onchange", required=True)

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
        return setting_obj.get_mission_form_permission_tag_id()
    
    def _get_default_approver_id(self):
        setting_obj = self.env['res.config.settings'].create({})
        return setting_obj.get_mission_form_permission_tag_id()
    
    # def _get

    @api.depends("state")
    def _compute_can_edit(self):
        for hr_mission_form in self:
            try:
                hr_mission_form._check_edition_update()
            except(UserError):
                hr_mission_form.write({"can_edit": False})
            else:
                hr_mission_form.write({"can_edit": True})


    @api.depends("state")
    def _compute_can_reject(self):
        for hr_mission_form in self:
            if hr_mission_form.state not in ('to_be_approved', 'to_be_second_approved'):
                hr_mission_form.write({"can_reject": False})
                continue

            try:
                if hr_mission_form.state in ('to_be_approved', 'to_be_second_approved'):
                    hr_mission_form._check_approval_update()
            except (AccessError, UserError):
                hr_mission_form.write({"can_reject": False})
            else:
                hr_mission_form.write({"can_reject": True})

    @api.depends("state")
    def _compute_can_approve(self):
        for hr_mission_form in self:
            if hr_mission_form.state not in ('to_be_approved', 'to_be_second_approved'):
                hr_mission_form.write({"can_approve": False})
                continue

            try:
                if hr_mission_form.state in ('to_be_approved', 'to_be_second_approved'):
                    hr_mission_form._check_approval_update()
            except (AccessError, UserError):
                hr_mission_form.write({"can_approve": False})
            else:
                hr_mission_form.write({"can_approve": True})

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

        for hr_mission_form in self:
            approver = hr_mission_form.approver_id
            second_approver = hr_mission_form.second_approver_id

            # Check if state is in the "to_be_approve" or "to_be_second_approve"
            if hr_mission_form.state in ('to_be_approved', 'to_be_second_approved'):
                # If it's in the "to_be_approve", we will check it with approver
                if hr_mission_form.state == "to_be_approved":
                    if current_employee.id != approver.id:
                        raise UserError(_("You can not use this function."))
                # If it's in the "to_be_second_approve", we will check it with second approver
                elif hr_mission_form.state == "to_be_second_approved":
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
        is_admin = self.env.user.has_group('hr_mission_form.group_op_mission_form')
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
