# -*- encoding: utf-8 -*-

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    product_id = fields.Many2one('product.template', 'Prueba')
    prefijo = fields.Char('Prefijo')
    codigo_renipes = fields.Char(u'Código Renipes')
    microred_id = fields.Many2one('minsa.micro.rede', 'MicroRed')
