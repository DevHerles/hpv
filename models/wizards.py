# coding: utf-8

import base64
from odoo import models, fields, api
from StringIO import StringIO
from xlwt import easyxf, Workbook


class PoiWizardExcelReport(models.TransientModel):
    _name = "poi.wizard.excel.report"

    txt_filename = fields.Char()
    txt_binary = fields.Binary(string=u"Pacientes Positivas")
    eess = fields.Many2one(
        comodel_name="res.company",
        string=u"Establecimiento"
    )
    general = fields.Boolean(
        string=u"Todos los Establecimientos"
    )

    @api.multi
    def generate_file(self):
        """
        function called from button
        """
        self.ensure_one()
        # make something to generate content
        wbk = Workbook()
        ws = wbk.add_sheet("Reporte")
        ws.col(0).width = 10000
        ws.col(1).width = 10000
        ws.col(2).width = 10000
        ws.col(3).width = 10000
        ws.col(4).width = 10000
        ws.col(5).width = 10000
        ws.col(6).width = 10000
        ws.col(7).width = 10000
        ws.col(8).width = 10000
        style0 = easyxf("font: height 200, name Calibri, colour_index black")
        style1_1 = easyxf(
            "font: height 200, name Calibri, colour_index white;pattern: pattern solid, fore_colour black; align: horiz center")

        s2 = 3
        s3 = 4

        # header
        ws.write(s2, 0, u"Codigo", style1_1)
        ws.write(s2, 1, u"Resultado", style1_1)
        ws.write(s2, 2, u"Apellidos", style1_1)
        ws.write(s2, 3, u"Nombres", style1_1)
        ws.write(s2, 4, u"Direccion", style1_1)
        ws.write(s2, 5, u"Celular", style1_1)
        ws.write(s2, 6, u"Establecimiento de Salud", style1_1)
        ws.write(s2, 7, u"Agente Comunitario", style1_1)
        ws.write(s2, 8, u"Micro Red", style1_1)

        domain = [
            ("eess", "=", self.eess.id)
        ]
        values = {}
        if not self.general:
            for obj in self.env["minsa.records.line"].search(domain):
                if obj.respuesta == "positivo":
                    if obj.codigo not in values:
                        values = {
                            "codigo": obj.codigo or "",
                            "respuesta": obj.respuesta or "",
                            "apellidos": obj.sobre_id.apellidos or "",
                            "nombres": obj.sobre_id.nombres or "",
                            "direccion": obj.sobre_id.direccion or "",
                            "mobile": obj.sobre_id.mobile or "",
                            "eess": obj.nom_eess or "",
                            "promotor_id": obj.promotor_id.name or "",
                            "microred": obj.microred.nombre or "",
                        }
                        ws.write(s3, 0, values.get("codigo"), style0)
                        ws.write(s3, 1, values.get("respuesta"), style0)
                        ws.write(s3, 2, values.get("apellidos", ""), style0)
                        ws.write(s3, 3, values.get("nombres", ""), style0)
                        ws.write(s3, 4, values.get("direccion", ""), style0)
                        ws.write(s3, 5, values.get("mobile", ""), style0)
                        ws.write(s3, 6, values.get("eess", ""), style0)
                        ws.write(s3, 7, values.get("promotor_id", ""), style0)
                        ws.write(s3, 8, values.get("microred", ""), style0)
                        s3 += 1
        else:
            for obj in self.env["minsa.records.line"].search([]):
                if obj.respuesta == "positivo":
                    if obj.codigo not in values:
                        values = {
                            "codigo": obj.codigo or "",
                            "respuesta": obj.respuesta or "",
                            "apellidos": obj.sobre_id.apellidos or "",
                            "nombres": obj.sobre_id.nombres or "",
                            "direccion": obj.sobre_id.direccion or "",
                            "mobile": obj.sobre_id.mobile or "",
                            "eess": obj.nom_eess or "",
                            "promotor_id": obj.promotor_id.name or "",
                            "microred": obj.microred.nombre or "",
                        }
                        ws.write(s3, 0, values.get("codigo"), style0)
                        ws.write(s3, 1, values.get("respuesta"), style0)
                        ws.write(s3, 2, values.get("apellidos", ""), style0)
                        ws.write(s3, 3, values.get("nombres", ""), style0)
                        ws.write(s3, 4, values.get("direccion", ""), style0)
                        ws.write(s3, 5, values.get("mobile", ""), style0)
                        ws.write(s3, 6, values.get("eess", ""), style0)
                        ws.write(s3, 7, values.get("promotor_id", ""), style0)
                        ws.write(s3, 8, values.get("microred", ""), style0)
                        s3 += 1
        file_data = StringIO()
        wbk.save(file_data)

        self.write({
            "txt_filename": "Pacientes_pasivas.xls",
            "txt_binary": base64.encodestring(file_data.getvalue())
        })
        if self.general:
            form = self.env.ref("modulos_registros.view_pruebas_excel_report_wizard", False)
            return {
                "type": "ir.actions.act_window",
                "name": "Pacientes Positivas",
                "res_model": "poi.wizard.excel.report",
                "res_id": self.id,
                "views": [(form.id, "form")],
                "view_type": "form",
                "view_mode": "form",
                "view_id": form.id,
                "target": "new",
            }
        else:
            form = self.env.ref("modulos_registros.view_pruebas_obtetras_excel_report_wizard", False)
            return {
                "type": "ir.actions.act_window",
                "name": "Pacientes Positivas",
                "res_model": "poi.wizard.excel.report",
                "res_id": self.id,
                "views": [(form.id, "form")],
                "view_type": "form",
                "view_mode": "form",
                "view_id": form.id,
                "target": "new",
            }
