# -*- encoding: utf-8 -*-

from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    product_id = fields.Many2one(
        comodel_name="product.template",
        string=u"Prueba"
    )
    prefijo = fields.Char(
        string=u"Prefijo",
    )
    codigo_renipes = fields.Char(
        string=u"Codigo Renipes"
    )
    microred_id = fields.Many2one(
        comodel_name="minsa.micro.rede",
        string=u"MicroRed"
    )
