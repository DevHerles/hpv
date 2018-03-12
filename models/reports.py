# -*- encoding: utf-8 -*-

from odoo import models, fields, api, tools


class ReportVphPositivos(models.Model):
    _name = "vph.positives.report"
    _auto = False

    @api.model_cr
    def init(self):
        """ VPH Positives main report """
        tools.drop_view_if_exists(self._cr,'vph_positives_report')
        self._cr.execute(""" CREATE VIEW vph_positives_report AS (
            SELECT T2.nombre, COUNT(*) AS Total
            FROM registro_sobre T0 INNER JOIN minsa_records_line T1 ON T0.codigo_sobre = T1.codigo INNER JOIN minsa_micro_rede T2 ON T1.microred = T2.id
            WHERE T0.estado_muestra_valido_invalido = 'valido' 
            AND T1.respuesta = 'positivo' AND DATE_PART('year',age(CURRENT_DATE, T0.fecha_nacimiento)) BETWEEN 30 AND 49
            GROUP BY T2.nombre
            ORDER BY Total DESC
        )""")
