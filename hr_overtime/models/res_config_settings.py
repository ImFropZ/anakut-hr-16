# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    overtime_permission_tag_id = fields.Many2one(
        "hr.employee.category", 
        string="Permission Tag", 
        config_parameter="hr_overtime.overtime_permission_tag_id"
    )
    overtime_approver_id = fields.Many2one(
        "res.users", 
        string="Approver", 
        required=True, 
        config_parameter="hr_overtime.overtime_approvor"
    )

    need_second_approver = fields.Boolean(
        "Need second approver?", 
        default=False, 
        config_parameter="hr_overtime.need_second_approver"
    )
    overtime_second_approver_id = fields.Many2one(
        "res.users", 
        string="Second Approver",
        config_parameter="hr_overtime.overtime_second_approvor"
    )

    @api.model
    def get_overtime_permission_tag_id(self):
        config_parameter_key = "hr_overtime.overtime_permission_tag_id"
        id = self.env["ir.config_parameter"].sudo().get_param(config_parameter_key)
        return self.env["hr.employee.category"].search([('id', '=', id)])
    
    @api.model
    def get_overtime_approver_id(self):
        config_parameter_key = "hr_overtime.overtime_approvor"

        id = self.env["ir.config_parameter"].sudo().get_param(config_parameter_key)
        return self.env["res.users"].search([('id', '=', id)])
    
    @api.model
    def get_need_second_approver(self):
        config_parameter_key = "hr_overtime.need_second_approver"
        return self.env["ir.config_parameter"].sudo().get_param(config_parameter_key)
    
    @api.model
    def get_overtime_second_approver_id(self):
        config_parameter_key = "hr_overtime.overtime_second_approvor"
        return self.env["ir.config_parameter"].sudo().get_param(config_parameter_key)