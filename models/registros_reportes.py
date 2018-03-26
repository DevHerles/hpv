# -*- encoding: utf-8 -*-
# Es parte del archivo registros.py

import requests

from odoo import api, models, fields

from odoo.exceptions import ValidationError


class Reportes(models.Model):
    _name = 'reportes'
    _rec_name = 'numero_placa'
    _order = 'fecha desc'
    _inherit = ['mail.thread']

    eess = fields.Many2one('res.company', 'Establecimiento',
                           required=True)
    usuario_id = fields.Many2one(
        'res.users',
        'Usuario',
        default=lambda self: self.env.uid,
    )
    fecha = fields.Date('Fecha')
    user_id = fields.Many2one('res.users', 'Nombre del operador',
                              required=True)
    temperatura = fields.Integer('Temperatura °C')
    lote_kit = fields.Char('Lote del Kit')
    fecha_expiracion = fields.Date('Fecha expiración')
    placa_valida = fields.Selection(
        [
            ('si', 'Si'),
            ('no', 'No'),
        ],
        u'Válida'
    )
    numero_placa = fields.Integer(u'Número de placa', required=True)
    rango = fields.Integer(default=1)
    numero_muestras = fields.Integer(u'Número de muestras', required=True,
                                     default=90
    )
    state = fields.Selection(
        [
            ('abierto', 'Abierto'),
            ('procesado', 'Procesado'),
        ],
        'Estado',
        default='abierto',
    )
    numero_positivos = fields.Integer(u'Número de positivos')
    registros_lines_ids = fields.One2many(
        'reportes.line',
        'reporte_id',
        u'Líneas de reporte'
    )

    def numero_muestras_changed(self, numero_muestras):
        if numero_muestras == 90 or numero_muestras == 0:
            return {}
        else:
            return {'value': {}, 'warning': {'title': 'Cuidado!!!', 'message': 'Recuerda que el número de muestras debe ser 90. Asegúrese de que el número de muestras ingresado es el correcto.'}}  # noqa

    @api.constrains('numero_muestras')
    def _check_numero_muestras(self):
        if self.numero_muestras > 96:
            raise ValidationError('Número de Muestras no permitido')

    @api.multi
    @api.onchange('registros_lines_ids')
    def _onchange_registros_lines_ids(self):
        c = 0
        for reg in self.registros_lines_ids:
            if reg.positivo is True:
                c = c + 1
        self.numero_positivos = c - 3

    @api.one
    def click_aprobado(self):
        if self.numero_muestras:
            self.registros_lines_ids.unlink()
            letra = numero = ''
            letras = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
            numeros = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12)
            domain = [('estado_muestra', '=', 'yes'),
                      ('reazones_muestra_invalidad', '=', False),
                      ('matriz', '=', False)]
            c = 0
            lista = []
            positivo = False
            indice = indicen = secuencia = 0
            max = self.numero_muestras + 6
            for l in range(0, max):
                if l <= 5:
                    secuencia = 0
                else:
                    secuencia = l - 5
                if l in [3, 4, 5]:
                    positivo = True
                else:
                    positivo = False
                letra = letras[indice]
                numero = numeros[c]
                record_line = {
                    'pos_x': letra,
                    'pos_y': numero,
                    'number': secuencia,
                    'positivo': positivo,
                    'reporte_id': self.id,
                }
                lista.append(record_line)
                indice = indice + 1
                indicen = indicen + 1
                if indice == 8:
                    indice = 0
                if indicen == 8:
                    indicen = 0
                    c = c + 1

            data2 = self.env['registro.sobre'].search(domain,
                                                      order='secuencia',
                                                      limit=self.numero_muestras)  # noqa
            data2.write({
                'matriz': True,
                'procesamiento_id': self.id,
            })
            r = []
            cc = 0

            for data in data2:
                cc = cc + 1
                r.append({'record_lista_id': data.id})
            cc = xx = 0
            for rr in lista:
                if cc > 5 and xx < len(r):
                    rr.update(r[xx])
                    xx = xx + 1
                cc = cc + 1
                if len(data2) < self.numero_muestras:
                    raise ValidationError(u'No tiene suficientes muestras '
                                          u'disponibles para continuar.')
                else:
                    self.env['reportes.line'].create(rr)

            self.write({'state': 'procesado'})
        else:
            raise ValidationError(
                u'El número de Inicio debe ser mayor al número de fin y el '
                u'Producto debe ser Ingresado')

    @api.multi
    def click_procesados(self):
        domain = [('state', '=', 'laboratorio'),
                  ('regitro', '=', True), ('sync', '=', False)]
        data2 = self.env['minsa.records.line'].search(domain,
                                                      order='fecha_registro')
        for record in self:
            for line in record.registros_lines_ids:
                if line.record_lista_id.mobile and not line.positivo and not \
                        line.record_lista_id.enviado:
                    celular = str(line.record_lista_id.mobile)
                    record.mensaje('51' + celular)
                    line.record_lista_id.enviado = True
                for obj in data2:
                    if line.record_lista_id.codigo_sobre == obj.codigo:
                        line.record_id = obj.id
                        if line.positivo and line.record_id:
                            line.record_id.write({
                                'respuesta': 'positivo',
                                'state': 'resultado',
                                'sync': True
                            })
                        elif not line.positivo and line.record_id:
                            line.record_id.write({
                                'respuesta': 'negativo',
                                'state': 'resultado',
                                'sync': True
                            })

    @api.model
    def mensaje(self, celular):
        parametro_url = 'sms_host'
        parametro_token = 'sms_token'
        msg_url_parametro = self.env['ir.config_parameter'].get_param(
            parametro_url) or None
        msg_token_parametro = self.env['ir.config_parameter'].get_param(
            parametro_token) or None
        if msg_token_parametro is None:
            raise ValidationError('No existe el parametro en el sistema')
        if msg_url_parametro == 'host':
            raise ValidationError('Falta configurar el parametro para el '
                                  'envio de mensajes')
        msg_url = msg_url_parametro
        msg_token = msg_token_parametro
        msg_texto = '''Su resultado de la prueba para el Virus Papiloma Humano
                    es NEGATIVO. Continue cuidando su salud.
                    Atte, Laboratorio Referencial Regional Tumbes'''
        requests.post(msg_url, {'recipient': celular, 'sender': 'EXTRANET',
                                'body': msg_texto},
                      headers={'X-Api-Token': msg_token})

    @api.multi
    def resultado(self):
        for record in self:
            for line in record.registros_lines_ids:
                if line.positivo:
                    line.positivo_valores = 'positivo'
                elif not line.positivo:
                    line.positivo_valores = 'negativo'

    @api.multi
    def placa(self):
        for record in self:
            for line in record.registros_lines_ids:
                if line.record_lista_id:
                    line.record_lista_id.procesamiento_id = record.id
