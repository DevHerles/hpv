# -*- encoding: utf-8 -*-
# Es parte del archivo registros.py

from odoo import api, fields, models


class ReportesLineas(models.Model):
    _name = 'reportes.line'

    reporte_id = fields.Many2one('reportes', 'Reporte Muestra')
    pos_x = fields.Char()
    pos_y = fields.Integer()
    number = fields.Integer('Secuencia')
    record_lista_id = fields.Many2one('registro.sobre', 'Registros')
    record_id = fields.Many2one('minsa.records.line', 'Registros')
    codigo_nombre = fields.Char(u'Nombre', related='record_id.codigo')
    positivo = fields.Boolean('Positivo')

    positivo_valores = fields.Selection(
        [
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
        ],
        'Positivo',
        default='negativo'
    )
    @api.onchange('positivo')
    def _onchange_positivo(self):
        if self.positivo:
            self.positivo_valores = 'positivo'
        else:
            self.positivo_valores = 'negativo'
