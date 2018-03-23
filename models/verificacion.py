# -*- encoding: utf-8 -*-
# Es parte del archivo registros.py

from odoo import api, models, fields

from odoo.exceptions import ValidationError
from utils import Utils

RENIEC_ERR = "Error!"


class Verificacion(models.Model):
    _name = "verificacion"

    dni = fields.Char(
        string=u"Documento Nacional de Identidad"
    )
    ape_paterno = fields.Char(
        string=u"Apellido paterno"
    )
    ape_materno = fields.Char(
        string=u"Apellido materno"
    )
    nombres = fields.Char(
        string=u"Nombres"
    )
    nombres_dase = fields.Char(
        string=u"Nombres"
    )
    birthday = fields.Char(
        string=u"Fecha de nacimiento"
    )
    legal_street = fields.Char(
        string=u"Domicilio"
    )
    gender = fields.Selection([("male", "Masculino"), ("female", "Femenino")])
    image = fields.Binary(
        string=u"Fotografía"
    )
    edad = fields.Char(
        string=u"Edad"
    )
    sobre = fields.Char(
        string=u"Código de sobre"
    )
    sobre1 = fields.Char(
        string=u"Código  de sobre"
    )
    apellidos = fields.Char(
        string=u"Apellidos"
    )
    fecha_muestra = fields.Date(
        string=u"Fecha de muestra"
    )
    fecha_muestra1 = fields.Date(
        string=u"Fecha de muestra"
    )
    resultado = fields.Selection(
        string=u"Resultado",
        selection=[
            ("positivo", "Positivo"),
            ("negativo", "Negativo"),
            ("invalido", "Invalido"),
        ]
    )
    resultado1 = fields.Selection(
        string=u"Resultado",
        selection=[
            ("positivo", "Positivo"),
            ("negativo", "Negativo"),
            ("invalido", "Invalido"),
        ]
    )
    eess = fields.Char(
        string=u"EESS"
    )
    eess_r = fields.Char(
        string=u"EESS"
    )
    establecimiento = fields.Boolean(
        string=u"Establecimiento"
    )

    @api.one
    def click_aprobado(self):
        if not self.dni:
            return {}
            # Consulta de Datos Reniec
        try:
            data = self.env["consultadatos.reniec"].consultardni(self.dni)
            data1 = self.env["registro.sobre"].search([("dni", "=",
                                                        self.dni)], limit=1)
            if data1:
                data2 = self.env["minsa.records.line"].search([("sobre_id",
                                                                "=",
                                                                data1.id)],
                                                              limit=1)
            fecha = data["nacimiento"]["fecha"]
            if fecha:
                util = Utils()
                edad = util.calcular_edad(fecha)
                if edad < 0:
                    edad = 0
                res = {"edad": edad}
            if not data:
                return True
            elif data and data1 and data2:
                values = {
                    "ape_paterno": data["ape_paterno"],
                    "ape_materno": data["ape_materno"],
                    "nombres": data["nombres"],
                    "birthday": data["nacimiento"]["fecha"],
                    "legal_street": data["domicilio"]["direccion_descripcion"],
                    "gender": data["sexo"],
                    "edad": res["edad"],
                    "image": data["fotografia"],
                    "sobre1": data1["codigo_sobre"],
                    "fecha_muestra1": data1["fecha_toma_muestra"],
                    "resultado1": data2["respuesta"],
                    "eess_r": data2["eess"].name,
                }
            else:
                values = {
                    "ape_paterno": data["ape_paterno"],
                    "ape_materno": data["ape_materno"],
                    "nombres_dase": data["nombres"],
                    "birthday": data["nacimiento"]["fecha"],
                    "legal_street": data["domicilio"]["direccion_descripcion"],
                    "gender": data["sexo"],
                    "edad": res["edad"],
                    "image": data["fotografia"],
                }
            self.write(values)
        except Exception as ex:
            raise ValidationError("%s : %s" % (RENIEC_ERR, ex.message))

    @api.one
    def click_buscar(self):
        data = self.env["registro.sobre"].search([("dni", "=", self.dni)],
                                                 limit=1)
        data1 = self.env["minsa.records.line"].search([("sobre_id", "=",
                                                        data.id)], limit=1)
        self.establecimiento = True
        if data and data1:
            for resultado in data1:
                values = {
                    "apellidos": data.apellidos,
                    "nombres": data.nombres,
                    "sobre": data.codigo_sobre,
                    "eess": resultado.eess.name,
                    "fecha_muestra": data.fecha_toma_muestra,
                    "resultado": resultado.respuesta,
                }
                self.write(values)
        else:
            raise ValidationError(u"Paciente no se realizó las pruebas PVH")
