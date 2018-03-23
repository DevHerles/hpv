# -*- encoding: utf-8 -*-
# Es parte del archivo registros.py

from odoo import api, models, fields


class ReportesLineas(models.Model):
    _name = "reportes.line"

    reporte_id = fields.Many2one("reportes", string="Reporte Muestra")
    pos_x = fields.Char()
    pos_y = fields.Integer()
    number = fields.Integer("Secuencia")
    record_lista_id = fields.Many2one("registro.sobre", string=u"Registros")
    record_id = fields.Many2one("minsa.records.line", string=u"Registros")
    codigo_nombre = fields.Char(
        string=u"Nombre",
        related="record_id.codigo",
    )
    positivo = fields.Boolean(string=u"Positivo")
    positivo_valores = fields.Selection(
        string="Positivo",
        selection=[
            ("positivo", "Positivo"),
            ("negativo", "Negativo"),
        ],
        default="negativo"
    )

    @api.onchange("positivo")
    def _onchange_positivo(self):
        if self.positivo:
            self.positivo_valores = "positivo"
        else:
            self.positivo_valores = "negativo"
