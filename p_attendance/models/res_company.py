# -*- coding: utf-8 -*-
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    p_wfh_code = fields.Char(string='Work From Home Code', default='WFH')
    p_wfo_code = fields.Char(string='Work From Office Code', default='WFO')
    p_worked_hours_base = fields.Selection(selection=[('flexible', 'Flexible'), ('employee', 'Employee Calendar'), ('company', 'Company Calendar')], string='Worked Hours Base', default='flexible')
    p_work_hour_day = fields.Float(string='Work Hour Day', default=8.0)