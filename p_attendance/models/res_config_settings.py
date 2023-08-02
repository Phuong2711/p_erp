# -*- coding: utf-8 -*-
from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    p_wfh_code = fields.Char(related='company_id.p_wfh_code', readonly=False)
    p_wfo_code = fields.Char(related='company_id.p_wfo_code', readonly=False)
    p_worked_hours_base = fields.Selection(related='company_id.p_worked_hours_base', readonly=False)
    p_work_hour_day = fields.Float(related='company_id.p_work_hour_day', readonly=False)