# -*- encoding: utf-8 -*-
# Es parte del archivo registros.py

from odoo import api, fields, models

from odoo.exceptions import ValidationError
from utils import Utils

RENIEC_ERR = 'Error!'


class Verificacion(models.Model):
    _name = 'verificacion'

    dni = fields.Char('Documento Nacional de Identidad')
    ape_paterno = fields.Char('Apellido paterno')
    ape_materno = fields.Char('Apellido materno')
    nombres = fields.Char('Nombres')
    nombres_dase = fields.Char('Nombres')
    birthday = fields.Char('Fecha de nacimiento')
    legal_street = fields.Char('Domicilio')
    gender = fields.Selection([('male', 'Masculino'), ('female', 'Femenino')])
    image = fields.Binary(u'Fotografía')
    edad = fields.Char('Edad')
    sobre = fields.Char(u'Código de sobre')
    sobre1 = fields.Char('Código  de sobre')
    apellidos = fields.Char(u'Apellidos')
    fecha_muestra = fields.Date('Fecha de muestra')
    fecha_muestra1 = fields.Date('Fecha de muestra')
    resultado = fields.Selection(
        [
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
            ('invalido', 'Invalido'),
        ],
        'Resultado'
    )
    resultado1 = fields.Selection(
        [
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
            ('invalido', 'Invalido'),
        ],
        'Resultado'
    )
    eess = fields.Char('EESS')
    eess_r = fields.Char('EESS')
    establecimiento = fields.Boolean('Establecimiento')

    @api.one
    def click_aprobado(self):
        if not self.dni:
            return {}
        try:
            # Consulta de Datos Reniec
            data = self.env['consultadatos.reniec'].consultardni(self.dni)
            data1 = self.env['registro.sobre'].search([('dni', '=',
                                                        self.dni)], limit=1)
            if data1:
                data2 = self.env['minsa.records.line'].search([('sobre_id',
                                                                '=',
                                                                data1.id)],
                                                              limit=1)
            fecha = data['nacimiento']['fecha']
            if fecha:
                util = Utils()
                edad = util.calcular_edad(fecha)
                if edad < 0:
                    edad = 0
                res = {'edad': edad}
            if not data:
                return True
            elif data and data1 and data2:
                values = {
                    'ape_paterno': data['ape_paterno'],
                    'ape_materno': data['ape_materno'],
                    'nombres': data['nombres'],
                    'birthday': data['nacimiento']['fecha'],
                    'legal_street': data['domicilio']['direccion_descripcion'],
                    'gender': data['sexo'],
                    'edad': res['edad'],
                    'image': data['fotografia'],
                    'sobre1': data1['codigo_sobre'],
                    'fecha_muestra1': data1['fecha_toma_muestra'],
                    'resultado1': data2['respuesta'],
                    'eess_r': data2['eess'].name,
                }
            else:
                values = {
                    'ape_paterno': data['ape_paterno'],
                    'ape_materno': data['ape_materno'],
                    'nombres_dase': data['nombres'],
                    'birthday': data['nacimiento']['fecha'],
                    'legal_street': data['domicilio']['direccion_descripcion'],
                    'gender': data['sexo'],
                    'edad': res['edad'],
                    'image': data['fotografia'],
                }
            self.write(values)
        except Exception as ex:
            raise ValidationError('%s : %s' % (RENIEC_ERR, ex.message))

    @api.one
    def click_buscar(self):
        data = self.env['registro.sobre'].search([('dni', '=', self.dni)],
                                                 limit=1)
        data1 = self.env['minsa.records.line'].search([('sobre_id', '=',
                                                        data.id)], limit=1)
        self.establecimiento = True
        if data and data1:
            for resultado in data1:
                values = {
                    'apellidos': data.apellidos,
                    'nombres': data.nombres,
                    'sobre': data.codigo_sobre,
                    'eess': resultado.eess.name,
                    'fecha_muestra': data.fecha_toma_muestra,
                    'resultado': resultado.respuesta,
                }
                self.write(values)
        else:
            raise ValidationError(u'Paciente no se realizó las pruebas PVH')
