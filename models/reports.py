# -*- encoding: utf-8 -*-

from odoo import models, fields, api, tools


class ReportVph(models.Model):
    _name = "report.vph"
    _auto = False

    resultado = fields.Char(readonly=True)
    fecha_resultado = fields.Date(string='Date')
    paciente = fields.Char(readonly=True)
    microred = fields.Char(readonly=True)
    edad = fields.Integer(readonly=True)

    @api.model_cr
    def init(self):
        """ VPH Positives main report """
        tools.drop_view_if_exists(self._cr, 'report_vph')
        self._cr.execute(""" CREATE VIEW report_vph AS (
            SELECT T0.id, T2.nombre AS microred, T0.edad, T1.respuesta AS resultado, T1.fecha_registro AS fecha_resultado,
                CONCAT(T0.apellidos, ' ', T0.nombres) AS paciente
            FROM registro_sobre T0 
                INNER JOIN minsa_records_line T1 ON T0.codigo_sobre = T1.codigo 
                INNER JOIN minsa_micro_rede T2 ON T1.microred = T2.id
            WHERE T0.estado_muestra_valido_invalido = 'valido'
        )""")
