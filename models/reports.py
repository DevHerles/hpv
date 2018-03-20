# -*- encoding: utf-8 -*-

from odoo import api, models, fields, tools


class ReportVph(models.Model):
    _name = "vph.reportvph"
    _auto = False

    resultado = fields.Char(readonly=True)
    fecha_resultado = fields.Date("Fecha de resultado")
    paciente = fields.Char(readonly=True)
    microred = fields.Char("Microred", readonly=True)
    edad = fields.Integer(readonly=True)
    establecimiento = fields.Char("Establecimiento", readonly=True)
    procedencia = fields.Char("Procedencia", readonly=True)
    nacionalidad = fields.Char("Nacionalidad", readonly=True)

    @api.model_cr
    def init(self):
        """ VPH Positives main report """
        tools.drop_view_if_exists(self._cr, "vph_reportvph")
        self._cr.execute(""" CREATE VIEW vph_reportvph AS (
            SELECT
                sobre.id,
                microred.nombre AS microred,
                records_line.nom_eess as establecimiento,
                CONCAT(sobre.apellidos,' ', sobre.nombres) AS paciente,
                sobre.edad, UPPER(records_line.respuesta) AS resultado,
                records_line.fecha_registro AS fecha_resultado,
                UPPER(sobre.nacionalidad) AS nacionalidad,
                UPPER(sobre.procedencia) AS procedencia
            FROM registro_sobre sobre
                INNER JOIN minsa_records_line records_line ON
                sobre.codigo_sobre = records_line.codigo
                INNER JOIN minsa_micro_rede microred ON
                records_line.microred = microred.id
            WHERE sobre.estado_muestra_valido_invalido = 'valido' AND
            records_line.respuesta IN ('negativo','positivo')
        )""")


class ReportVphInvalido(models.Model):
    _name = "vph.reportvphinvalido"
    _auto = False

    razon = fields.Char(readonly=True)
    fecha_resultado = fields.Date("Fecha de resultado")
    paciente = fields.Char(readonly=True)
    microred = fields.Char("Microred", readonly=True)
    edad = fields.Integer(readonly=True)
    establecimiento = fields.Char("Establecimiento", readonly=True)
    procedencia = fields.Char("Procedencia", readonly=True)
    nacionalidad = fields.Char("Nacionalidad", readonly=True)

    @api.model_cr
    def init(self):
        """ VPH Invalids main report """
        tools.drop_view_if_exists(self._cr, "vph_reportvphinvalido")
        self._cr.execute(""" CREATE VIEW vph_reportvphinvalido AS (
            SELECT
                sobre.id,
                microred.nombre AS microred,
                records_line.nom_eess as establecimiento,
                CONCAT(sobre.apellidos,' ', sobre.nombres) AS paciente,
                records_line.fecha_registro AS fecha_resultado,
                UPPER(sobre.nacionalidad) AS nacionalidad,
                UPPER(sobre.procedencia) AS procedencia,
                UPPER(sobre.reazones_muestra_invalidad) AS razon
            FROM registro_sobre sobre
                INNER JOIN minsa_records_line records_line ON
                sobre.codigo_sobre = records_line.codigo
                INNER JOIN minsa_micro_rede microred ON
                records_line.microred = microred.id
            WHERE sobre.estado_muestra_valido_invalido = 'invalido'
        )""")


class ReportPap(models.Model):
    _name = "vph.reportpap"
    _auto = False

    resultado = fields.Char(readonly=True)
    fecha_resultado = fields.Date("Fecha de resultado", readonly=True)
    paciente = fields.Char(readonly=True)
    microred = fields.Many2one(
        comodel_name="minsa.micro.rede",
        string=u"MicroRed",
        readonly=True,
    )
    edad = fields.Integer(readonly=True)
    establecimiento = fields.Many2one(
        comodel_name="res.company",
        string=u"Establecimiento",
        readolny=True,
    )
    procedencia = fields.Char("Procedencia", readonly=True)
    nacionalidad = fields.Char("Nacionalidad", readonly=True)

    @api.model_cr
    def init(self):
        """ PAP Positives main report """
        tools.drop_view_if_exists(self._cr, "vph_reportpap")
        self._cr.execute(""" CREATE VIEW vph_reportpap AS (
            SELECT
                id,
                microred,
                eess AS establecimiento,
                UPPER(CONCAT(apellidos,' ',nombres)) AS paciente,
                edad,
                fecha_resulado AS fecha_resultado,
                UPPER(resultado_pap) AS resultado,
                UPPER(nacionalidad) AS nacionalidad,
                UPPER(procedencia) AS procedencia
            FROM paciente_pap
            WHERE resultado_pap <> 'negativo'
        )""")


class ReportAnonimo(models.Model):
    _name = "vph.reportanonimo"
    _auto = False

    fecha_entrega = fields.Date("Fecha de entrega", readonly=True)
    microred = fields.Many2one(
        comodel_name="minsa.micro.rede",
        string=u"MicroRed",
        readonly=True,
    )
    establecimiento = fields.Char("Establecimiento", readonly=True)
    codigo = fields.Char("Código de sobre", readonly=True)
    estado = fields.Char("Estado", readonly=True)

    @api.model_cr
    def init(self):
        """ VPH unset main report """
        tools.drop_view_if_exists(self._cr, "vph_reportanonimo")
        self._cr.execute(""" CREATE VIEW vph_reportanonimo AS (
            SELECT
                id,
                microred,
                nom_eess AS establecimiento,
                fecha_entrega,
                codigo,
                UPPER(state) AS estado
            FROM minsa_records_line
            WHERE regitro = False
        )""")
