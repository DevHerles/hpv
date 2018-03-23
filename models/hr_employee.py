# -*- encoding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    autorizados = fields.Boolean(
        string=u"Autorizadas"
    )
