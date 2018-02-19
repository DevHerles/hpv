# -*- encoding: utf-8 -*-

from odoo import models, fields, api


class Dashboard(models.Model):
    _name = "dashboard"

    @api.one
    def _get_count(self):
        # orders_count = self.env['sale.order'].search(
        #     [('state', '=', 'sales_order')])

        count_pacientes_vph = self.env['minsa.records.line'].search()
        count_pacientes_vph_positivos = self.env['minsa.records.line'].search()

        self.total_pacientes_vph = len(count_pacientes_vph)
        self.total_pacientes_vph_positivos = len(count_pacientes_vph_positivos)
        self.total_pacientes_vph_negativos = len(count_pacientes_vph) - len(count_pacientes_vph_positivos)

    name = fields.Char(string="Name")

    total_pacientes_vph = fields.Integer(compute='_get_count')
    total_pacientes_vph_positivos = fields.Integer(compute='_get_count')
    total_pacientes_vph_negativos = fields.Integer(compute='_get_count')

    def dashboard_sales_action_id(self):
        print 'dashboard_sales_action_id'