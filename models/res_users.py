# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResUsers(models.Model):
    _inherit = "res.users"

    tipo_documento = fields.Selection(
        string="Tipo de documento",
        selection=[
            ("dni", "DNI"),
            ("carnet", "Carnet de Extranjería"),
        ],
        default="dni"
    )
