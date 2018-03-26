# -*- encoding: utf-8 -*-

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    tipo_documento = fields.Selection(
        [
            ('dni', 'DNI'),
            ('carnet', 'Carnet de Extranjería'),
        ],
        'Tipo de documento',
        default='dni'
    )
