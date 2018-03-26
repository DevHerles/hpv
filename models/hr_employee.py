# -*- encoding: utf-8 -*-

from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    autorizado = fields.Boolean('Autorizada', oldname='autorizadas')
