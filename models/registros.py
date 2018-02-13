# -*- coding: utf-8 -*-
import sys
import requests
import json
import logging

from datetime import datetime

from odoo.exceptions import ValidationError
from odoo import models, fields, api

from odoo.tools.translate import _

logger = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding("utf-8")

RENIEC_ERR = 'Error!'


class MinsaReasonForCancellation(models.Model):
    _name = 'minsa.reason.for.cancellation'

    name = fields.Char(
        string=u'Motivo de Cancelacion'
    )
    code = fields.Char(
        string=u'Codigo de Cancelacion'
    )


class RegistroSobre(models.Model):
    _name = 'registro.sobre'
    _order = "secuencia asc"
    _inherit = ['mail.thread']

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        domain = [
            '|',
            ('dni', operator, name),
            '|',
            ('codigo_tubo', operator, name),
            ('apellidos', operator, name)
        ]
        recs = self.search(domain + args, limit=limit)
        if recs:
            return recs.name_get()

        return super(RegistroSobre, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.multi
    def name_get(self):
        return [(obj.id, u'{}'.format(obj.codigo_sobre))
                for obj in self]

    secuencia = fields.Integer(
        string=u'secuencia de registro'
    )
    usuario_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.uid,
        string="Usuario"
    )
    fecha = fields.Date(
        string=u'Fecha de Registro',
        default=fields.Datetime.now,
        track_visibility='onchange'
    )
    fecha_nacimiento = fields.Date(
        string=u'Fecha de Nacimiento',
    )
    codigo_sobre = fields.Char(
        string=u'Codigo de Sobre',
        track_visibility='onchange'
    )
    codigo_tubo = fields.Char(
        string=u'Codigo de Tubo',
        track_visibility='onchange'
    )
    estado_muestra = fields.Selection(
        string="Codigo Valido",
        selection=[
            ('yes', 'Si'),
            ('not', 'No'),
        ],
        track_visibility='onchange'
    )
    nombres = fields.Char(
        string=u'Nombres',
        required=True,
        track_visibility='onchange'
    )
    apellidos = fields.Char(
        string=u'Apellidos',
        required=True,
        track_visibility='onchange'
    )
    dni = fields.Char(
        string=u'DNI / CARNET DE EXTRANJERIA',
        required=True,
        size=10,
        track_visibility='onchange'
    )
    edad = fields.Integer(
        string=u'Edad',
        default=0,
        track_visibility='onchange'
    )
    mobile = fields.Char(
        size=9,
        track_visibility='onchange'
    )
    direccion = fields.Char(
        string=u'Direccion',
        track_visibility='onchange'
    )
    fecha_toma_muestra = fields.Date(
        string=u'Fecha Toma Muestra',
        track_visibility='onchange'
    )
    estado_muestra_valido_invalido = fields.Selection(
        string="Estado de la Muestra",
        selection=[
            ('valido', 'Muestra Valida'),
            ('invalido', 'Muestra Invalida'),
        ],
        track_visibility='onchange'
    )
    reazones_muestra_invalidad = fields.Selection(
        string="Razones de Muestra Invalida",
        selection=[
            ('edadfuera', 'Edad fuera de rango'),
            ('dnisindato', 'DNI sin Dato'),
            ('dniequivocado', 'DNI Equivocado'),
            ('codigo', 'Código diferente entre tubo y sobre'),
            ('muestra', 'Muestra con moco'),
            ('tubo', 'Tubo sin liquido'),
            ('tubo1', 'Tubo sin cepillo'),
            ('sobre', 'Sobre sin tubo'),
            ('sobre1', 'Sobre sin datos'),
            ('reniec', 'Datos RENIEC no coinciden con sobre'),
        ],
        track_visibility='onchange'
    )
    codigo_valido_invalido = fields.Char(
        string="Confirmacion de Codigo",
        store=True,
        track_visibility='onchange'
    )
    estado_muestra_b = fields.Boolean(
        string='Estado de la Muestra',
        default=True,
        track_visibility='onchange'
    )
    otros = fields.Char(
        string=u'Otros',
        track_visibility='onchange'
    )
    codigo_valido_invalido1 = fields.Char(
        string="Confirmacion de Codigo",
        related='codigo_valido_invalido',
        store=True,
        track_visibility='onchange'
    )
    enviado = fields.Boolean(
        string=u'Enviado',
        track_visibility='onchange'
    )
    matriz = fields.Boolean(
        string=u'Matriz',
        track_visibility='onchange'
    )
    tipo_documento = fields.Selection(
        string="Tipo de Documento",
        selection=[
            ('dni', 'DNI'),
            ('carnet', 'Carnet de Extranjeria'),
        ],
        track_visibility='onchange',
        required=True
    )
    procesamiento_id = fields.Many2one(
        comodel_name='reportes',
        string=u'Placa'
    )
    registros_id = fields.Many2one(
        comodel_name='minsa.records.line',
        string=u'Lineas de Registros'
    )
    respuesta = fields.Selection(
        string=u'Resultado',
        selection=[
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
            ('invalido', 'Invalido'),
        ],
        related='registros_id.respuesta',
        store=True,
    )

    @api.constrains('edad')
    def _check_something(self):
        for record in self:
            if record.edad <= 0 and record.es_pap:
                raise ValidationError("Su edad no debe ser menor a: %s" % record.edad)

    @api.onchange('reazones_muestra_invalidad')
    def _onchange_reazones_muestra_invalidad(self):
        if not self.reazones_muestra_invalidad:
            self.estado_muestra_valido_invalido = 'valido'
        else:
            self.estado_muestra_valido_invalido = 'invalido'

    @api.onchange('edad')
    def _onchange_edad_si(self):
        if self.edad < 30 or self.edad >= 50 and self.dni:
            self.reazones_muestra_invalidad = 'edadfuera'
        else:
            self.reazones_muestra_invalidad = ''

    @api.onchange('codigo_sobre', 'codigo_tubo')
    def _onchange_valido_invalido(self):
        if self.codigo_sobre and self.codigo_tubo:
            if self.codigo_sobre == self.codigo_tubo:
                self.estado_muestra = 'yes'
                self.reazones_muestra_invalidad = False
            elif self.codigo_sobre != self.codigo_tubo:
                self.estado_muestra = 'not'
                self.reazones_muestra_invalidad = 'codigo'

    @api.onchange('dni', 'tipo_documento')
    def click_aprobado(self):
        if self.tipo_documento == 'dni':
            if not self.dni:
                self.edad = False
                return {}
            # Consulta de Datos Reniec
            try:
                data = self.env['consultadatos.reniec'].consultardni(self.dni)
                fecha = data['nacimiento']['fecha']
                if fecha:
                    edad = (datetime.now().date() - datetime.strptime(fecha, '%Y-%m-%d').date()).days / 365
                    if edad < 0:
                        edad = 0
                    else:
                        self.edad = edad
                if not data:
                    return True
                elif data:
                    self.nombres = data['nombres']
                    self.apellidos = u'{} {}'.format(data['ape_paterno'], data['ape_materno'])
                    self.direccion = data['domicilio']['direccion_descripcion']
                    self.fecha_nacimiento = data['nacimiento']['fecha']
            except Exception as ex:
                raise ValidationError("%s : %s" % (RENIEC_ERR, ex.message))

    @api.model
    def create(self, vals):
        if not vals.get('secuencia'):
            vals['secuencia'] = self.env['ir.sequence'].next_by_code('registro.sobre')  # noqa
        res = super(RegistroSobre, self).create(vals)
        if res.codigo_sobre:
            registro = self.env['minsa.records.line'].search([
                ('codigo', '=', res.codigo_sobre)])
            if registro:
                registro.write({
                    'sobre_id': res.id,
                    'estado_muestra': res.estado_muestra,
                    'reazones_muestra_invalidad': res.reazones_muestra_invalidad or '',
                    'otros': res.otros or '',
                    'fecha_recepcion': res.fecha_toma_muestra,
                    'fecha_registro': res.fecha,
                    'regitro': True,
                    'state': 'laboratorio',
                })
            for reg in registro:
                reg.record_id._compute_record_line_laboratio_ids()
                reg.record_id._compute_record_line_pendiente_ids()
                res.registros_id = reg.id
        return res

    @api.multi
    def update_documento(self):
        for obj in self:
            if len(obj.dni) == 8:
                obj.tipo_documento = 'dni'

    @api.multi
    def update_dni(self):
        for obj in self:
            if obj.tipo_documento == 'dni':
                if not obj.dni:
                    obj.edad = ''
                    return {}
                # Consulta de Datos Reniec
                try:
                    data = self.env['consultadatos.reniec'].consultardni(obj.dni)
                    fecha = data['nacimiento']['fecha']
                    if fecha:
                        edad = (datetime.now().date() - datetime.strptime(fecha, '%Y-%m-%d').date()).days / 365
                        if edad < 0:
                            edad = 0
                        else:
                            obj.edad = edad
                    if not data:
                        return True
                    elif data:
                        obj.nombres = data['nombres']
                        obj.apellidos = u'{} {}'.format(data['ape_paterno'], data['ape_materno'])
                        obj.direccion = data['domicilio']['direccion_descripcion']
                        obj.fecha_nacimiento = data['nacimiento']['fecha']
                except Exception as ex:
                    raise ValidationError("%s : %s" % (RENIEC_ERR, ex.message))

    @api.multi
    def update_os(self):
        for obj in self:
            registros = self.env['minsa.records.line'].search([
                ('codigo', '=', obj.codigo_sobre), ('regitro', '=', False)])
            if registros:
                registros.write({
                    'sobre_id': obj.id,
                    'estado_muestra': obj.estado_muestra,
                    'reazones_muestra_invalidad': obj.reazones_muestra_invalidad or '',
                    'otros': obj.otros or '',
                    'fecha_recepcion': obj.fecha_toma_muestra,
                    'fecha_registro': obj.fecha,
                    'regitro': True,
                    'state': 'laboratorio',
                })
            for reg in registros:
                reg.record_id._compute_record_line_laboratio_ids()
                reg.record_id._compute_record_line_pendiente_ids()
                obj.write({
                    'registros_id': reg.id
                })
        return True

    @api.multi
    def update_positivas(self):
        for obj in self:
            registros = self.env['minsa.records.line'].search([
                ('codigo', '=', obj.codigo_sobre)])
            for reg in registros:
                obj.write({
                    'registros_id': reg.id
                })
        return True

    _sql_constraints = [
        ('field_unique_codigo',
         'unique(codigo_sobre)',
         'Ya existe Codigo!')
    ]


class PacentePap(models.Model):
    _name = 'paciente.pap'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('dni', 'ilike', name)] + args, limit=limit)
        if not recs:
            recs = self.search([('nombres', operator, name)] + args, limit=limit)
        return recs.name_get()

    @api.multi
    def name_get(self):
        return [(obj.id, u'{} {}'.format(obj.nombres, obj.apellidos))
                for obj in self]

    nombres = fields.Char(
        string=u'Nombres',
        required=True
    )
    apellidos = fields.Char(
        string=u'Apellidos',
        required=True
    )
    dni = fields.Char(
        string=u'DNI',
        size=8
    )
    edad = fields.Integer(
        string=u'Edad',
        default=0
    )
    mobile = fields.Char(
        size=9
    )
    direccion = fields.Char(
        string=u'Direccion'
    )
    gestante = fields.Selection(
        string=u'Gestante',
        selection=[
            ('si', 'Si'),
            ('no', 'No'),
        ]
    )
    obstetra_id = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Obstetra',
        default=lambda self: self._default_empleado(),
    )
    eess = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS',
        default=lambda self: self.env.user.company_id.id
    )
    microred = fields.Many2one(
        comodel_name='minsa.micro.rede',
        string=u'MicroRed',
        related='eess.microred_id',
        readonly=True,
        store=True
    )
    fecha_pap = fields.Date(
        string=u'Fecha'
    )
    fecha_resulado = fields.Date(
        string=u'Fecha Resultado'
    )
    resultado_pap = fields.Selection(
        string=u"Resultado",
        selection=[
            ('negativo', 'Negativo'),
            ('insactifactorio', 'PAP insatifactorio'),
            ('lei', 'LEI bajo grado'),
            ('lei1', 'LEI alto grado'),
            ('carcinoma', 'Carcinoma Insitu'),
            ('ascos', 'ASCUS'),
            ('asgos', 'AGUS'),
        ]
    )
    otro_pap = fields.Char(
        string=u'Otro'
    )
    pap = fields.Selection(
        string=u'Pap',
        selection=[
            ('si', 'Si'),
            ('no', 'No'),
        ],
        default='si'
    )

    @api.multi
    def _default_empleado(self):
        user_login = self.env.uid,
        hremployee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_login)])
        return hremployee

    @api.onchange('dni')
    def click_aprobado(self):
        if not self.dni:
            self.edad = ''
            return {}
        # Consulta de Datos Reniec
        try:
            data = self.env['consultadatos.reniec'].consultardni(self.dni)
            fecha = data['nacimiento']['fecha']
            if fecha:
                edad = (datetime.now().date() - datetime.strptime(fecha, '%Y-%m-%d').date()).days / 365
                if edad < 0:
                    edad = 0
                else:
                    self.edad = edad
        except Exception as ex:
            raise ValidationError("%s : %s" % (RENIEC_ERR, ex.message))


class Paciente(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _default_empleado(self):
        user_login = self.env.uid,
        hremployee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_login)])
        return hremployee

    es_promotor = fields.Boolean(
        string="Es Promotor"
    )
    es_paciente = fields.Boolean(
        string="Es Paciente"
    )
    es_profesional = fields.Boolean(
        string="Es Paciente"
    )
    es_pap = fields.Boolean(
        string="Es Paciente Pap"
    )
    paciente_vph = fields.Boolean(
        string=u'paciente vph'
    )
    procedimientos_ids = fields.One2many(
        comodel_name='procedimientos',
        inverse_name='dni_id',
        string=u'Lineas de Procedimientos'
    )
    registros_ids = fields.One2many(
        comodel_name='minsa.records.line',
        inverse_name='paciente_id',
        string=u'Lineas de Registros'
    )
    codigo_sobre = fields.Char(
        string=u'Codigo de Sobre'
    )
    codigo_tubo = fields.Char(
        string=u'Codigo de Tubo'
    )
    nombres = fields.Char(
        string=u'Nombres',
        required=True
    )
    apellidos = fields.Char(
        string=u'Apellidos',
        required=True
    )
    dni = fields.Char(
        string=u'DNI',
        size=8
    )
    edad = fields.Integer(
        string=u'Edad',
        default=0
    )
    mobile = fields.Char(
        size=9
    )
    direccion = fields.Char(
        string=u'Direccion'
    )
    fecha = fields.Date(
        string=u'Fecha de Registro',
        default=fields.Datetime.now(),
    )
    fecha_toma_muestra = fields.Date(
        string=u'Fecha Toma Muestra'
    )
    codigo_valido_invalido = fields.Char(
        string="Confirmacion de Codigo",
        store=True,
    )
    codigo_valido_invalido1 = fields.Char(
        string="Confirmacion de Codigo",
        related='codigo_valido_invalido',
        store=True,
    )
    estado_muestra = fields.Selection(
        string="Codigo Valido",
        selection=[
            ('yes', 'Si'),
            ('not', 'No'),
        ],
    )
    estado_muestra_b = fields.Boolean(
        string='Estado de la Muestra',
        default=True
    )
    estado_muestra_valido_invalido = fields.Selection(
        string="Estado de la Muestra",
        selection=[
            ('valido', 'Muestra Valida'),
            ('invalido', 'Muestra Invalida'),
        ],
    )
    reazones_muestra_invalidad = fields.Selection(
        string="Razones de Muestra Invalida",
        selection=[
            ('edadfuera', 'Edad fuera de rango'),
            ('dnisindato', 'DNI sin Dato'),
            ('dniequivocado', 'DNI Equivocado'),
            ('codigo', 'Código diferente entre tubo y sobre'),
            ('muestra', 'Muestra con moco'),
            ('tubo', 'Tubo sin liquido'),
            ('tubo1', 'Tubo sin cepillo'),
            ('sobre', 'Sobre sin tubo'),
            ('sobre1', 'Sobre sin datos'),
            ('reniec', 'Datos RENIEC no coinciden con sobre'),
        ]
    )
    otros = fields.Char(
        string=u'Otros'
    )
    gestante = fields.Selection(
        string=u'Gestante',
        selection=[
            ('si', 'Si'),
            ('no', 'No'),
        ]
    )
    obstetra_id = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Obstetra',
        default=lambda self: self._default_empleado(),
    )
    eess = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS',
        default=lambda self: self.env.user.company_id.id
    )
    pap = fields.Selection(
        string=u'Pap',
        selection=[
            ('si', 'Si'),
            ('no', 'No'),
        ],
        default='si'
    )
    fecha_pap = fields.Date(
        string=u'Fecha'
    )
    fecha_resulado = fields.Date(
        string=u'Fecha Resultado'
    )
    resultado_pap = fields.Selection(
        string=u"Resultado",
        selection=[
            ('negativo', 'Negativo'),
            ('insactifactorio', 'PAP insactifactorio'),
            ('lei', 'LEI bajo grado'),
            ('lei1', 'LEI alto grado'),
            ('carcinoma', 'Carcinoma Insitu'),
            ('ascos', 'ASCUS'),
            ('asgos', 'AGUS'),
        ]
    )
    otro_pap = fields.Char(
        string=u'Otro'
    )
    compania = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS'
    )
    type = fields.Selection(
        [('contact', 'Contact'),
         ('invoice', 'Invoice address'),
         ('delivery', 'Shipping address'),
         ('other', 'Other address')], string='Address Type',
        default='other',
        help="Used to select automatically the right address according to the context in sales and purchases documents.")

    @api.constrains('edad')
    def _check_something(self):
        for record in self:
            if record.edad <= 0 and record.es_pap:
                raise ValidationError("Su edad no debe ser menor a: %s" % record.edad)

    @api.onchange('reazones_muestra_invalidad')
    def _onchange_reazones_muestra_invalidad(self):
        if not self.reazones_muestra_invalidad:
            self.estado_muestra_valido_invalido = 'valido'
        else:
            self.estado_muestra_valido_invalido = 'invalido'

    @api.onchange('edad')
    def _onchange_edad_si(self):
        if self.edad < 30 and self.dni:
            self.reazones_muestra_invalidad = 'edadfuera'
        elif self.edad > 49 and self.dni:
            self.reazones_muestra_invalidad = 'edadfuera'
        else:
            self.reazones_muestra_invalidad = ''

    @api.onchange('codigo_sobre', 'codigo_tubo')
    def _onchange_valido_invalido(self):
        if self.codigo_sobre and self.codigo_tubo:
            if self.codigo_sobre == self.codigo_tubo:
                self.estado_muestra = 'yes'
                self.reazones_muestra_invalidad = ''
            elif self.codigo_sobre != self.codigo_tubo:
                self.estado_muestra = 'not'
                self.reazones_muestra_invalidad = 'codigo'

    @api.onchange('es_paciente')
    def _onchange_pap_si(self):
        if self.es_paciente:
            self.paciente_vph = True

    @api.onchange('dni')
    def click_aprobado(self):
        if not self.dni:
            self.edad = ''
            return {}
        # Consulta de Datos Reniec
        try:
            data = self.env['consultadatos.reniec'].consultardni(self.dni)
            fecha = data['nacimiento']['fecha']
            if fecha:
                edad = (datetime.now().date() - datetime.strptime(fecha, '%Y-%m-%d').date()).days / 365
                if edad < 0:
                    edad = 0
                else:
                    self.edad = edad
        except Exception as ex:
            raise ValidationError("%s : %s" % (RENIEC_ERR, ex.message))

    @api.model
    def create(self, vals):
        res = super(Paciente, self).create(vals)
        if res.codigo_sobre:
            registro = self.env['minsa.records.line'].search([
                ('codigo', '=', res.codigo_sobre)])
            if registro:
                registro.write({
                    'paciente_id': res.id,
                    'estado_muestra': res.estado_muestra,
                    'reazones_muestra_invalidad': res.reazones_muestra_invalidad or '',
                    'otros': res.otros or '',
                    'fecha_recepcion': res.fecha_toma_muestra,
                    'fecha_registro': res.fecha,
                    'regitro': True,
                    'state': 'laboratorio',
                })
            for reg in registro:
                reg.record_id._compute_record_line_laboratio_ids()
                reg.record_id._compute_record_line_pendiente_ids()
        return res

    @api.multi
    def update_os(self):
        for obj in self:
            registros = self.env['minsa.records.line'].search([
                ('codigo', '=', obj.codigo_sobre)])
            if registros:
                registros.write({
                    'paciente_id': obj.id,
                    'estado_muestra': obj.estado_muestra,
                    'reazones_muestra_invalidad': obj.reazones_muestra_invalidad or '',
                    'otros': obj.otros or '',
                    'fecha_recepcion': obj.fecha_toma_muestra,
                    'fecha_registro': obj.fecha,
                    'regitro': True,
                    'state': 'laboratorio',
                })
            for reg in registros:
                reg.record_id._compute_record_line_laboratio_ids()
                reg.record_id._compute_record_line_pendiente_ids()
        return True


class MinsaRecords(models.Model):
    _name = 'minsa.records'
    _order = "fecha_entrega desc"
    _inherit = ['mail.thread']

    @api.constrains('numero_inicio', 'numero_fin')
    def _check_numeor_inicio_y_fin(self):
        if self.numero_inicio and self.numero_fin:
            obj_vats = self.search([('numero_inicio', '=', self.numero_inicio), ('numero_fin', '=', self.numero_fin)])
            if len(obj_vats) > 1:
                raise ValidationError('El rango ya existe!')

    @api.one
    @api.depends('record_line_ids')
    def _compute_record_line_entregados_ids(self):
        entregados = len(self.record_line_ids)
        self.cod_entregados = entregados

    @api.multi
    @api.depends('record_line_ids')
    def _compute_record_line_laboratio_ids(self):
        laboratorio = 0
        for reg in self:
            for line in reg.record_line_ids:
                if line.state == 'laboratorio' or line.state == 'resultado':
                    laboratorio = laboratorio + 1

        if self.record_line_ids:
            self.cod_laboratorio = laboratorio

    @api.multi
    @api.depends('record_line_ids')
    def _compute_record_line_pendiente_ids(self):
        pendiente = ''
        for reg in self:
            for line in reg.record_line_ids:
                if line.state == 'promotor':
                    pendiente = pendiente + ', ' + line.codigo

        if self.record_line_ids:
            self.cod_pendiente = pendiente

    @api.multi
    @api.onchange('record_line_ids')
    def _onchange_record_line_ids(self):
        for reg in self.record_line_ids:
            if self.servicio:
                self.fecha_entrega = reg.fecha_entrega

    @api.one
    @api.depends('numero_inicio', 'numero_fin')
    def _compute_tango(self):
        self.rango = u'{} - {}'.format(self.numero_inicio, self.numero_fin)

    eess = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS',
        default=lambda self: self.env.user.company_id.id,
    )
    microred = fields.Many2one(
        comodel_name='minsa.micro.rede',
        string=u'MicroRed',
        related='eess.microred_id',
        readonly=True,
        store=True
    )
    eess_entrega = fields.Many2one(
        comodel_name='registros.generales',
        string=u'Entrega a Establecimientos'
    )
    cod_entregados = fields.Integer(
        string=u"# Entregados",
        compute='_compute_record_line_entregados_ids',
        store=True
    )
    cod_laboratorio = fields.Integer(
        string=u"# Laboratorio",
        compute='_compute_record_line_laboratio_ids',
        store=True
    )
    cod_pendiente = fields.Char(
        string="Codigo Faltantes",
        compute='_compute_record_line_pendiente_ids',
        store=True
    )
    promotor_id = fields.Many2one(
        comodel_name='res.partner',
        string=u'Nombre de ACS'
    )
    obstetra_id = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Obstetra',
        default=lambda self: self._default_empleado(),
        readonly=True
    )
    usuario_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.uid,
        string="Usuario"
    )
    fecha_entrega = fields.Date(
        string=u'Fecha de Entrega',
        default=lambda self: fields.datetime.now(),
        track_visibility='onchange'
    )
    servicio = fields.Boolean(
        string=u'Servicio'
    )
    codigo_servicio = fields.Char(
        string=u'Codigo en servico',
        compute='_compute_codigo',
        store=True
    )
    promotora = fields.Boolean(
        string=u'ACS'
    )
    numero_inicio = fields.Char(
        string=u'Número de Inicio'
    )
    numero_fin = fields.Char(
        string=u'Número de Fin'
    )
    rango = fields.Char(
        string=u'Rango de Muestras',
        store=True,
        compute=_compute_tango
    )
    product_id = fields.Many2one(
        comodel_name='product.template',
        string=u'Prueba'
    )
    record_line_ids = fields.One2many(
        comodel_name='minsa.records.line',
        inverse_name='record_id',
        string=u'Registros',
        track_visibility='onchange',
        store=True
    )
    state = fields.Selection(
        string="Estado",
        selection=[
            ('borrador', 'Borrador'),
            ('entregado', 'Entregado'),
        ],
        default='borrador',
    )
    eess_a = fields.Boolean(
        string=u'EESS'
    )
    eessa_a = fields.Many2one(
        comodel_name='res.company',
        string=u'Nombre de EESS'
    )
    obstetra_a_id = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Nombre de Obstetra'
    )
    codigo_servicio_obstetra = fields.Char(
        string=u'Codigo',
        size=5
    )

    @api.multi
    def _default_empleado(self):
        user_login = self.env.uid,
        hremployee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_login)])
        return hremployee

    @api.one
    @api.depends('servicio')
    def _compute_codigo(self):
        if self.servicio:
            for obj in self.record_line_ids:
                self.codigo_servicio = obj.codigo

    @api.one
    def click_aprobado(self):
        prefijo = self.env.user.company_id.prefijo
        if int(self.numero_inicio) < int(self.numero_fin):
            if self.promotora:
                for i in range(int(self.numero_inicio), int(self.numero_fin) + 1):
                    codigo = u'{}{}'.format(prefijo, str(i).zfill(5))
                    values = {
                        'fecha_entrega': self.fecha_entrega,
                        'codigo': codigo,
                        'record_id': self.id,
                        'promotor_id': self.promotor_id.id,
                        'state': 'promotor',
                    }
                    self.env['minsa.records.line'].create(values)
                self.write({'state': 'entregado'})
            elif self.eess_a:
                for i in range(int(self.numero_inicio), int(self.numero_fin) + 1):
                    codigo = u'{}{}'.format(prefijo, str(i).zfill(5))
                    record_line = {
                        'fecha_entrega': self.fecha_entrega,
                        'codigo': codigo,
                        'record_id': self.id,
                        'eessa_a': self.eessa_a.id,
                        'obstetra_a_id': self.obstetra_a_id.id,
                        'state': 'promotor',
                    }
                    self.env['minsa.records.line'].create(record_line)
                self.write({'state': 'entregado'})
            elif self.servicio:
                codigo = u'{}{}'.format(prefijo, str(i).zfill(5))
                record_line = {
                    'fecha_entrega': self.fecha_entrega,
                    'codigo': codigo,
                    'record_id': self.id,
                    'promotor_id': self.promotor_id.id,
                }
                self.env['minsa.records.line'].create(record_line)
            self.write({'state': 'entregado'})
        else:
            raise ValidationError(
                u'La número de Inicio debe ser mayor al número de fin y el Producto debe ser Ingresado')

    @api.model
    def create(self, vals):
        prefijo = self.env.user.company_id.prefijo
        res = super(MinsaRecords, self).create(vals)
        if res.eess_a and not res.numero_inicio:
            raise ValidationError(u'Debe ingresar un rango')
        if res.codigo_servicio_obstetra and res.servicio:
            vals = {
                'codigo': u'{}{}'.format(prefijo, str(res.codigo_servicio_obstetra).zfill(5)),
                'fecha_entrega': res.fecha_entrega,
                'record_id': res.id
            }
            res.record_line_ids.create(vals)

        if res.servicio:
            for obj in res.record_line_ids:
                res.codigo_servicio = obj.codigo
        if res.promotora:
            prefijo = self.env.user.company_id.prefijo

            if int(res.numero_inicio) < int(res.numero_fin):
                if res.promotora:
                    for i in range(int(res.numero_inicio), int(res.numero_fin) + 1):
                        codigo = u'{}{}'.format(prefijo, str(i).zfill(5))
                        record_line = {
                            'fecha_entrega': res.fecha_entrega,
                            'codigo': codigo,
                            'record_id': res.id,
                            'promotor_id': res.promotor_id.id,
                            'state': 'promotor',
                        }
                        self.env['minsa.records.line'].create(record_line)
                    res.write({'state': 'entregado'})
                elif res.eess_a:
                    for i in range(int(res.numero_inicio), int(res.numero_fin) + 1):
                        y = i
                        if len(str(y)) == 1:
                            company = self.env.user.company_id.prefijo
                            codigo = u'{}{}{}'.format(company, '0000', i)
                        elif len(str(y)) == 2:
                            company = self.env.user.company_id.prefijo
                            codigo = u'{}{}{}'.format(company, '000', i)
                        elif len(str(y)) == 3:
                            company = self.env.user.company_id.prefijo
                            codigo = u'{}{}{}'.format(company, '00', i)
                        elif len(str(y)) == 4:
                            company = self.env.user.company_id.prefijo
                            codigo = u'{}{}{}'.format(company, '0', i)
                        elif len(str(y)) == 5:
                            company = self.env.user.company_id.prefijo
                            codigo = u'{}{}{}'.format(company, i, '')
                        record_line = {
                            'fecha_entrega': self.fecha_entrega,
                            'codigo': codigo,
                            'record_id': self.id,
                            'eessa_a': self.eessa_a.id,
                            'obstetra_a_id': self.obstetra_a_id.id,
                            'state': 'promotor',
                        }
                        self.env['minsa.records.line'].create(record_line)
                    res.write({'state': 'entregado'})
                elif res.servicio:
                    if len(str(self.numero_inicio)) == 1:
                        company = self.env.user.company_id.prefijo
                        codigo = u'{}{}{}'.format(company, '0000', res.numero_inicio)
                    elif len(str(self.numero_inicio)) == 2:
                        company = self.env.user.company_id.prefijo
                        codigo = u'{}{}{}'.format(company, '000', res.numero_inicio)
                    elif len(str(self.numero_inicio)) == 3:
                        company = self.env.user.company_id.prefijo
                        codigo = u'{}{}{}'.format(company, '00', res.numero_inicio)
                    elif len(str(self.numero_inicio)) == 4:
                        company = self.env.user.company_id.prefijo
                        codigo = u'{}{}{}'.format(company, '0', res.numero_inicio)
                    elif len(str(self.numero_inicio)) == 5:
                        company = self.env.user.company_id.prefijo
                        codigo = u'{}{}{}'.format(company, res.numero_inicio, '')
                    record_line = {
                        'fecha_entrega': res.fecha_entrega,
                        'codigo': codigo,
                        'record_id': res.id,
                        'promotor_id': res.promotor_id.id,
                    }
                    self.env['minsa.records.line'].create(record_line)
                res.write({'state': 'entregado'})
            else:
                raise ValidationError(
                    u'La número de Inicio debe ser mayor al número de fin y el Producto debe ser Ingresado')
        return res

    @api.multi
    def update_codigos(self):
        for obj in self:
            for line in obj.record_line_ids:
                if line.state == 'laboratorio' or line.state == 'resultado':
                    line.record_id._compute_record_line_laboratio_ids()
                elif line.state == 'promotor':
                    line.record_id._compute_record_line_pendiente_ids()


class MinsaRecordsLine(models.Model):
    _name = 'minsa.records.line'
    _inherit = ['mail.thread']

    @api.multi
    def name_get(self):
        return [(obj.id, u'{}'.format(obj.codigo or ''))
                for obj in self]

    record_id = fields.Many2one(
        comodel_name='minsa.records',
        string='Registros'
    )
    obstetra_id = fields.Many2one(
        comodel_name='hr.employee',
        related='record_id.obstetra_id',
        string=u'Obstetra'
    )
    eess = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS',
        default=lambda self: self.env.user.company_id.id
    )
    microred = fields.Many2one(
        comodel_name='minsa.micro.rede',
        string=u'MicroRed',
        related='eess.microred_id',
        readonly=True,
        store=True
    )
    promotor_id = fields.Many2one(
        comodel_name='res.partner',
        string=u'Nombre de agente comunitario',
        related='record_id.promotor_id',
        store=True
    )
    servicio = fields.Boolean(
        string=u'servicio',
        related='record_id.servicio'
    )
    product_id = fields.Many2one(
        comodel_name='product.template',
        string=u'Prueba',
        related='eess.product_id',
        readonly=True,
        store=True,
    )
    fecha_entrega = fields.Date(
        string=u'Fecha de Entrega',
    )
    codigo = fields.Char(
        string=u'Codigo de Entrega'
    )
    paciente_id = fields.Many2one(
        comodel_name='res.partner',
        string=u'Paciente'
    )
    sobre_id = fields.Many2one(
        comodel_name='registro.sobre',
        string=u'Paciente'
    )
    nombre_apellido = fields.Char(
        string=u'Nombre y Apellido',
        compute='_compute_nombres_apellidos',
        store=True,
    )
    estado_muestra = fields.Selection(
        string=u'Muestra en Buen Estado',
        selection=[
            ('yes', 'Si'),
            ('not', 'No'),
            ('codigo', 'Codigo Invalido'),
        ]
    )
    fecha_recepcion = fields.Date(
        string=u'Fecha de Recepcion de Muestra'
    )
    fecha_registro = fields.Date(
        string=u'Fecha de Registro de Diagnostico'
    )
    respuesta = fields.Selection(
        string=u'Resultado',
        selection=[
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
            ('invalido', 'Invalido'),
        ]
    )
    motivo_cancelacion = fields.Many2one(
        comodel_name='minsa.reason.for.cancellation',
        string=u'Motivo de Cancelacion'
    )
    state = fields.Selection(
        string="Estado",
        selection=[
            ('servicio', 'Servicio'),
            ('promotor', 'Agente comunitario'),
            ('laboratorio', 'Con Laboratorio'),
            ('resultado', 'Con Resultado'),
        ],
        default='servicio',
    )
    code_lab = fields.Char('Codigo Lab')
    sync = fields.Boolean(
        string=u'Sincronizado'
    )
    regitro = fields.Boolean(
        string=u'Registrado'
    )
    reazones_muestra_invalidad = fields.Selection(
        string="Razones de Muestra Invalida",
        selection=[
            ('edadfuera', 'Edad fuera de rango'),
            ('dnisindato', 'DNI sin Dato'),
            ('dniequivocado', 'DNI Equivocado'),
            ('codigo', 'Código diferente entre tubo y sobre'),
            ('muestra', 'Muestra con moco'),
            ('tubo', 'Tubo sin liquido'),
            ('tubo1', 'Tubo sin cepillo'),
            ('sobre', 'Sobre sin tubo'),
            ('sobre1', 'Sobre sin datos'),
            ('reniec', 'Datos RENIEC no coinciden con sobre'),
        ]
    )
    otros = fields.Char(
        string=u'Otros'
    )
    eess_a = fields.Boolean(
        string=u'EESS-A',
        related='record_id.eess_a'
    )
    eessa_a = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS-A'
    )
    obstetra_a_id = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Obstetra-A'
    )
    nom_eess = fields.Char(
        string=u'Nombre de Establecimiento',
        compute='_compute_nombre_eess',
        store=True
    )
    his = fields.Boolean(
        string=u'Migracion HISMINSA'
    )

    @api.multi
    def update_os(self):
        atenciones = []
        for obj in self:
            if obj.promotor_id and obj.estado_muestra == 'yes' and not obj.his:
                words = obj.sobre_id.apellidos.split(" ")
                ap1 = words[0]
                ap2 = words[-1]
                lista = {
                    'paciente': {'tipo_documento': '01' if obj.sobre_id.tipo_documento == 'dni' else '02',
                                 'nro_documento': obj.sobre_id.dni,
                                 'renipress': obj.obstetra_id.company_id.codigo_renipes,
                                 'apellido_paterno': ap1,
                                 'apellido_materno': ap2,
                                 'nombres': obj.sobre_id.nombres,
                                 'sexo': 'F',
                                 'pais': 'Peru' if obj.sobre_id.tipo_documento == 'dni' else 'Otro',
                                 'fecha_nacimiento': obj.sobre_id.fecha_nacimiento,
                                 'edad': obj.sobre_id.edad,
                                 },
                    'registrador': {'nro_documento': obj.obstetra_id.user_id.login,
                                    'tipo_documento': '01' if obj.obstetra_id.user_id.tipo_documento == 'dni' else '02',
                                    },
                    'prestador': {'nro_documento': obj.sobre_id.usuario_id.login,
                                  'tipo_documento': '01' if obj.sobre_id.usuario_id.tipo_documento == 'dni' else '02',
                                  'renipress': obj.obstetra_id.company_id.codigo_renipes,
                                  },
                    'atencion': {'fecha': obj.sobre_id.fecha_toma_muestra},
                    'registro_id': obj.id,
                }
                atenciones += [lista]
        parametro_host = 'his_migrate_host'
        migrator_host_parametro = self.env['ir.config_parameter'].get_param(parametro_host) or None
        if migrator_host_parametro is None:
            raise ValidationError('No Existe el Parametro en el Sistema')
        if migrator_host_parametro == 'his_migrate_host':
            raise ValidationError('Falta configurar el parametro para la migraccion al HisMinsa')
        settings = {
            'HISMIGRATOR_HOST': migrator_host_parametro
        }
        self.migrate(settings, atenciones)

    def migrate(self, settings, atenciones):
        lista_data = []
        prestadores = {}
        registradores = {}
        for registro in atenciones:
            if registro['paciente'].get('tipo_documento') == '01':
                paciente = self.env['consultadatos.mpi'].ver(
                    registro['paciente'].get("nro_documento"), registro['paciente'].get('tipo_documento'))
                paciente = {
                    "idtipodoc": registro['paciente'].get('tipo_documento'),
                    "nrodocumento": registro['paciente'].get('nro_documento'),
                    "apepaterno": u"{}".format(paciente.get("apellido_paterno", "")),
                    "apematerno": u"{}".format(paciente.get("apellido_materno", "")),
                    "nombres": u"{}".format(paciente.get("nombres", "")),
                    "fechanacimiento": "{:%Y%m%d}".format(
                        datetime.strptime(paciente.get('fecha_nacimiento'), '%Y-%m-%d')),
                    "idsexo": "M" if paciente.get('sexo') == "1" else "F",
                    "idestablecimiento": registro['prestador'].get('renipress'),
                    "idetnia": paciente.get("etnia", "80"),
                    "nrohistoriaclinica": registro['paciente'].get('nro_documento'),
                    "idpais": registro['paciente'].get('pais'),
                    "idflag": "7"
                }

            else:

                paciente = {
                    "idtipodoc": registro['paciente'].get('tipo_documento'),
                    "nrodocumento": 'SD-0000000' if registro['paciente'].get('tipo_documento') == '5' else registro[
                        'paciente'].get('nro_documento'),
                    "apepaterno": u"{}".format(registro['paciente'].get('apellido_paterno')),
                    "apematerno": u"{}".format(registro['paciente'].get('apellido_marteno')),
                    "nombres": u"{}".format(registro['paciente'].get('nombres')),
                    "fechanacimiento": "{:%Y%m%d}".format(
                        datetime.strptime(registro['paciente'].get('fecha_nacimiento'), '%Y-%m-%d')),
                    "idsexo": registro['paciente'].get('sexo'),
                    "idestablecimiento": registro['prestador'].get('renipress'),
                    "idetnia": registro['paciente'].get("etnia", "80"),
                    "nrohistoriaclinica": 'SD-0000000' if registro['paciente'].get('tipo_documento') == '5' else
                    registro['paciente'].get('nro_documento'),
                    "idpais": registro['paciente'].get('pais'),
                    "idflag": "7"
                }

            # traer de mpi datos del digitador
            nro_documento = registro['registrador'].get("nro_documento")
            if nro_documento not in registradores:
                registrador = self.env['consultadatos.mpi'].ver(
                    nro_documento, registro['registrador'].get('tipo_documento'))
                registradores[nro_documento] = registrador
            registrador = registradores.get(nro_documento)
            personal_registra = {
                "idtipodoc": "1",
                "nrodocumento": registro['registrador'].get("nro_documento"),
                "apepaterno": u"{}".format(registrador.get("apellido_paterno", "")),
                "apematerno": u"{}".format(registrador.get("apellido_materno", "")),
                "nombres": u"{}".format(registrador.get("nombres", "")),
                "fechanacimiento": "{:%Y%m%d}".format(
                    datetime.strptime(registrador.get('fecha_nacimiento'), '%Y-%m-%d')),
                "idsexo": "M" if registrador.get('sexo') == "1" else "F",
                "idpais": "PER",
                "idprofesion": "42",
                "idcondicion": "8"
            }

            # Prestador del Servicio
            nro_documento = registro['prestador'].get("nro_documento")
            if nro_documento not in prestadores:
                prestador = self.env['consultadatos.mpi'].ver(
                    nro_documento, registro['prestador'].get('tipo_documento'))
                prestadores[nro_documento] = prestador
            prestador = prestadores.get(nro_documento)
            personal_atiende = {
                "idtipodoc": "1",
                "nrodocumento": registro['prestador'].get("nro_documento"),
                "apepaterno": u"{}".format(prestador.get("apellido_paterno", "")),
                "apematerno": u"{}".format(prestador.get("apellido_materno", "")),
                "nombres": u"{}".format(prestador.get("nombres", "")),
                "fechanacimiento": "{:%Y%m%d}".format(
                    datetime.strptime(prestador.get('fecha_nacimiento'), '%Y-%m-%d')),
                "idsexo": "M" if prestador.get('sexo') == "1" else "F",
                "idpais": "PER",
                "idprofesion": "42",
                "idcondicion": "8"
            }

            proxy = self.env['consultadatos.mpi']
            ciudadano = proxy.ver(registro['paciente'].get("nro_documento"),
                                  "01" if registro['paciente'].get('tipo_documento') == "1" else registro[
                                      'paciente'].get('tipo_documento'))
            idfinanciador = "10"
            componente = "1"
            numeroafiliacion = ""
            if ciudadano.get('tipo_seguro', '') == '2':
                datos_sis = proxy.ver_datos_sis(ciudadano['uid'])
                idfinanciador = "2"
                componente = "2"
                numeroafiliacion = datos_sis.get("nro_contrato", "")

            items = []
            item = {
                "tipoitem": "PL",
                "labs": [],
                "codigo": "87621",
                "tipodiagnostico": "D",
                "fechasolicitud": "{:%Y%m%d}".format(datetime.today()),
                "fecharesultado": ''
            }

            items.append(item)

            cita = {
                "edadregistro": registro['paciente'].get('edad'),
                "idfinanciador": idfinanciador,
                "idturno": 'Mañana',
                "componente": componente,
                "idestablecimiento": registro['prestador'].get('renipress'),
                "numeroafiliacion": numeroafiliacion,
                "items": items,
                "idtipedadregistro": "A",
                "fechaatencion": "{:%Y%m%d}".format(
                    datetime.strptime(registro['atencion'].get('fecha'), '%Y-%m-%d')),
                "idups": "303203",
                "estadoregistro": "A",
                "fgdiag": 7,
            }
            if paciente and personal_registra and personal_atiende:
                lista_data.append(dict(paciente=paciente,
                                       personal_registra=personal_registra,
                                       personal_atiende=personal_atiende,
                                       cita=cita,
                                       registro_id=registro['registro_id']))
            else:
                raise ValidationError("Falta Datos")

        for data in lista_data:
            trama = data.copy()
            del trama['registro_id']
            try:
                headers = {'content-type': 'application/json'}
                response = requests.post(
                    '{}/wsrest-his/hisminsa/paquete/actualizar/'.format(settings.get('HISMIGRATOR_HOST')),
                    data=json.dumps(trama), headers=headers)
                if response and response.status_code == 200:
                    try:
                        res = response.json()
                        if res.get('estado', '') == 'ERROR':
                            logger.error(
                                'Se producio un error(1) {} en el envio de la trama de servicio al HIS-MINSA'.format(
                                    res.get('descripcion', '')))
                        else:
                            logger.info('Se envio la atencion al HIS-MINSA')
                            self.browse(data['registro_id']).his = True
                    except:
                        result = response.__dict__
                        logger.error(
                            u'Se producio un error(2) {} en el envio de la trama de servicio al HIS-MINSA'.format(
                                result[u'_content']))
                else:
                    logger.error(u'El servidor no proceso correctamente el paquete de servicio al HIS-MINSA')

            except Exception as ex:
                logger.error(
                    u'Se producio un error(3) {} en el envio de la trama de servicio al HIS-MINSA'.format(str(ex)))

    @api.one
    @api.depends('sobre_id')
    def _compute_nombres_apellidos(self):
        if self.sobre_id:
            self.nombre_apellido = u'{} {}'.format(self.sobre_id.nombres, self.sobre_id.apellidos)
        else:
            self.nombre_apellido = ''

    @api.one
    @api.depends('eess')
    def _compute_nombre_eess(self):
        if self.eess:
            self.nom_eess = self.eess.name
        else:
            self.nom_eess = ''

    @api.model
    def create(self, vals):
        res = super(MinsaRecordsLine, self).create(vals)
        if res.codigo:
            cantidad = res.codigo
            if len(cantidad) == 1:
                company = self.env.user.company_id.prefijo
                res.codigo = u'{}{}{}'.format(company, '0000', res.codigo)
            elif len(cantidad) == 2:
                company = self.env.user.company_id.prefijo
                res.codigo = u'{}{}{}'.format(company, '000', res.codigo)
            elif len(cantidad) == 3:
                company = self.env.user.company_id.prefijo
                res.codigo = u'{}{}{}'.format(company, '00', res.codigo)
            elif len(cantidad) == 4:
                company = self.env.user.company_id.prefijo
                res.codigo = u'{}{}{}'.format(company, '0', res.codigo)
            elif len(cantidad) == 5:
                company = self.env.user.company_id.prefijo
                res.codigo = u'{}{}{}'.format(company, res.codigo, '')
        return res

    _sql_constraints = [
        ('field_unique_codigo',
         'unique(codigo)',
         'Ya existe Codigo!')
    ]


class Procedimientos(models.Model):
    _name = 'procedimientos'
    _inherit = ['mail.thread']

    @api.multi
    @api.depends('vph_id')
    def _compute_vph_id(self):
        if self.vph_id:
            registro = self.env['minsa.records.line'].search([
                ('codigo', '=', self.vph_id.codigo_sobre)])
            self.eess_paciente_vph = registro.eess

    eess = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS',
        default=lambda self: self.env.user.company_id.id
    )
    microred = fields.Many2one(
        comodel_name='minsa.micro.rede',
        string=u'MicroRed',
        related='eess.microred_id',
        readonly=True,
        store=True
    )
    eess_paciente_vph = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS',
        compute=_compute_vph_id,
        readonly=True
    )
    usuario_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.uid,
        string="Usuario"
    )
    dni_id = fields.Many2one(
        comodel_name='res.partner',
        string=u'Datos de Paciente'
    )
    pap_id = fields.Many2one(
        comodel_name='paciente.pap',
        string=u'Busqueda Paciente PAP  mmmmm'
    )
    vph_id = fields.Many2one(
        comodel_name='registro.sobre',
        string=u'Busqueda Paciente VPH xxx'
    )
    image = fields.Binary(related='dni_id.image')
    medico0 = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Profesional'
    )
    medico = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Profesional'
    )
    medico2 = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Profesional'
    )
    medico3 = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Profesional'
    )
    medico4 = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Profesional'
    )
    medico1 = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Responsable de registrar'
    )
    fecha_procedimiento = fields.Date(
        string=u'Fecha',
    )
    fecha_no_iva = fields.Date(
        string=u'Fecha',
    )
    procedimientos_ids = fields.One2many(
        comodel_name='procedimientos.lineas',
        inverse_name='procedimientos_id',
        string=u'Lineas de Procedimientos'
    )
    fecha_realizada = fields.Date(
        string=u'Fecha que se Realiza'
    )
    resultado_iva = fields.Selection(
        string=u'Resultado',
        selection=[
            ('true', 'Positivo'),
            ('false', 'Negativo'),
        ]
    )
    pap = fields.Selection(
        string=u'Pap',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ],
        related='pap_id.pap'
    )
    obstetra_pap_id = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Profesional',
        related='pap_id.obstetra_id'
    )
    eess_pap = fields.Many2one(
        comodel_name='res.company',
        string=u'Lugar',
        related='pap_id.eess'
    )
    fecha_pap = fields.Date(
        string=u'Fecha',
        related='pap_id.fecha_pap'
    )
    fecha_resulado_pap = fields.Date(
        string=u'Fecha Resultado',
        related='pap_id.fecha_resulado'
    )
    paciente_vph = fields.Boolean(
        string="Es Paciente"
    )
    resultado_pap = fields.Selection(
        string=u"Resultado",
        selection=[
            ('negativo', 'Negativo'),
            ('insactifactorio', 'PAP insactifactorio'),
            ('lei', 'LEI bajo grado'),
            ('lei1', 'LEI alto grado'),
            ('carcinoma', 'Carcinoma Insitu'),
            ('ascos', 'Ascos'),
            ('asgos', 'Agos'),
        ],
        related='pap_id.resultado_pap'
    )
    otro_pap = fields.Char(
        string=u'Otro',
        related='pap_id.otro_pap'
    )
    iva = fields.Selection(
        string=u'IVAA',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    luegar_iva = fields.Char(
        string='Lugar'
    )
    razon_iva = fields.Char(
        string=u'Razon'
    )
    crioterapia = fields.Selection(
        string=u'Crioterapia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    luegar_crioterapia = fields.Char(
        string='Lugar'
    )
    fecha_de_crio = fields.Date(
        string=u'Fecha'
    )
    razon_crio = fields.Char(
        string=u'Razon'
    )
    fecha_de_contro = fields.Date(
        string=u'Fecha de Control'
    )
    fecha_de_refe_post_contro = fields.Date(
        string=u'Fecha Referencia Post Control'
    )
    razon1 = fields.Char(
        string=u'Razón'
    )
    fecha_de_referencia = fields.Date(
        string=u'Fecha de Referencia'
    )
    referencia = fields.Selection(
        string=u'Referencia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    razon_de_referencia = fields.Selection(
        string=u'Razón Referencia',
        selection=[
            ('gestacion', 'Gestación'),
            ('sospecha', 'Sospecha de microinvasión o cáncer'),
            ('lesion', 'Lesión Blanda en canal endocervical'),
            ('lesion1', 'Lesión que ocupa más del 70% y se extiende a pared vaginal'),
            ('alteracion', 'Alteraciones anatómicas de cuello'),
        ]
    )
    otros = fields.Char(
        string=u'Otros'
    )
    coloscopia = fields.Selection(
        string=u'Colposcopia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    luegar_coloscopia = fields.Char(
        string=u'Lugar'
    )
    fecha_coloscopia = fields.Date(
        string=u'Fecha'
    )
    biopsia = fields.Selection(
        string=u'Biopsia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    lugar_biopsia = fields.Char(
        string=u'Lugar'
    )
    fecha_biopcia = fields.Date(
        string=u'Fecha'
    )
    resultado_biopsia = fields.Selection(
        string=u"Resultado",
        selection=[
            ('negativo', 'Normal'),
            ('insactifactorio', 'Cervicitis'),
            ('lei', 'LEI bajo grado NIC I'),
            ('lei1', 'LEI alto grado NIC II'),
            ('lei2', 'LEI alto grado NIC III'),
            ('carcinoma', 'Carcinoma'),
        ]
    )
    otros_biosia = fields.Char(
        string=u'Otros'
    )
    cono_leep = fields.Selection(
        string=u'Cono Leep',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    lugar_conoleep = fields.Char(
        string=u'Lugar'
    )
    fecha_conoleep = fields.Date(
        string=u'Fecha'
    )
    fecha_control_conoleep = fields.Date(
        string=u'Fecha de Control'
    )
    resultado_conoleep = fields.Char(
        string=u'Resultado'
    )
    histerectomia = fields.Selection(
        string=u'Histerectomia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    fecha_histerectomia = fields.Date(
        string=u'Fecha'
    )
    lugar_histerectomia = fields.Char(
        string=u'Lugar'
    )
    resultado_histerectomia = fields.Char(
        string=u'Resultado'
    )
    contrareferencia = fields.Selection(
        string=u'Contrareferencia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ],
    )
    fecha_contrareferencia = fields.Date(
        string=u'Fecha de la Contrareferencia'
    )
    fecha_de_retornode_de_la_cabecera = fields.Date(
        string=u'Fecha de Retorno a la Cabecera de Microred'
    )
    readioterapia = fields.Selection(
        string=u'Radioterapia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ],
    )
    fecha_radioterapia = fields.Date(
        string=u'Fecha'
    )
    lugar_radioterapia = fields.Char(
        string=u'Lugar'
    )
    finalizoreadioterapia = fields.Selection(
        string=u'Finalizo Tratamiento',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    razon_no = fields.Char(
        string=u'Razón'
    )
    quimioterapia = fields.Selection(
        string=u'Quimioterapia',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    fecha_quimioterapia = fields.Date(
        string=u'Fecha'
    )
    lugar_quimioterapia = fields.Char(
        string=u'Lugar'
    )
    finalizoquimio = fields.Selection(
        string=u'Finalizo Tratamiento',
        selection=[
            ('yes', 'Si'),
            ('no', 'No'),
        ]
    )
    razon_noq = fields.Char(
        string=u'Razón'
    )
    paciente_culmino_tratamiento = fields.Selection(
        string="Paciente culmino tratamiendo",
        selection=[
            ('yes', 'Si'),
            ('not', 'No'),
        ]
    )
    otros2 = fields.Char(
        string=u'Razón'
    )
    otros_si = fields.Char(
        string=u'¿Con que tratamiento culmino?'
    )
    fecha_fin_tratamiento = fields.Date(
        string=u'Fecha de Culminacion de Tratamiento'
    )
    razon_de_tratamiento = fields.Char(
        string=u'Razón (es) de no Tratamiento'
    )
    no_acudio = fields.Char(
        string=u'No Acudio a Cita'
    )
    no_procedimiento = fields.Char(
        string=u'No Realizan el Procedimiento'
    )
    no_insumos = fields.Char(
        string=u'No hay Insumos para Realizar el Procedimiento'
    )
    no_profesional = fields.Char(
        string=u'No hay Profesional para Realizar el Tratamiento'
    )
    state = fields.Selection(
        string="Estado",
        selection=[
            ('borrador', 'Borrador'),
            ('entregado', 'Entregado'),
        ],
        default='borrador',
    )
    procedimiento_tratamiento = fields.Char(
        string=u'NÚMERO DE HISTORIA CLINICA'
    )
    nombre_apellido = fields.Char(
        string=u'Nombre y Apellido',
    )

    @api.onchange('vph_id')
    def _onchange_vhp_id(self):
        if self.vph_id:
            self.paciente_vph = True
            self.pap_id = ''
            self.nombre_apellido = u'{} {}'.format(self.vph_id.nombres, self.vph_id.apellidos)
        else:
            self.paciente_vph = False
            self.nombre_apellido = ''

    @api.model
    def create(self, vals):
        res = super(Procedimientos, self).create(vals)
        if res.vph_id:
            res.nombre_apellido = u'{} {}'.format(res.vph_id.nombres, res.vph_id.apellidos)
        else:
            res.nombre_apellido = ''
        return res


class ProcedimientosLineas(models.Model):
    _name = 'procedimientos.lineas'

    procedimientos = fields.Selection(
        string="Pruebas",
        selection=[
            ('ivva', 'IVAA'),
            ('biopsia', 'BIOPSIA'),
            ('crioterapia', 'CRIOTERAPIA'),
            ('cono_leep', 'CONO LEEP'),
            ('colposcopia', 'COLPOSCOPIA'),
            ('histerectomia', 'HISTERECTOMIA'),
        ]
    )
    fecha = fields.Date(
        string=u'Fecha de Prueba'
    )
    resultado = fields.Char(
        string=u'Resultado de Prueba'
    )
    lugar_prueba = fields.Char(
        string=u'Lugar de Prueba'
    )
    procedimientos_id = fields.Many2one(
        comodel_name='procedimientos',
        string=u'Procedimientos'
    )
    dni_id = fields.Many2one(
        comodel_name='res.partner',
        related='procedimientos_id.dni_id',
        string=u'Datos de Paciente',
        store=True
    )


class Reportes(models.Model):
    _name = 'reportes'
    _rec_name = "numero_placa"
    _order = "fecha desc"
    _inherit = ['mail.thread']

    @api.constrains('numero_muestras')
    def _check_numero_muestras(self):
        if self.numero_muestras > 96:
            raise ValidationError('Numero de Muestras no permitido')

    eess = fields.Many2one('res.company', string="Lugar")
    usuario_id = fields.Many2one(
        "res.users",
        default=lambda self: self.env.uid,
        string="Usuario"
    )
    fecha = fields.Date(
        string=u'Fecha'
    )
    user_id = fields.Many2one('res.users', string='Nombre Operador')
    temperatura = fields.Integer(string=u'Temperatura °C')
    lote_kit = fields.Char(string=u'Lote Kit')
    fecha_expiracion = fields.Date(string=u'Fecha expiracion')
    placa_valida = fields.Selection(
        string="Valida",
        selection=[
            ('si', 'Si'),
            ('no', 'No'),
        ]
    )
    numero_placa = fields.Integer(
        string=u'Número de Placa'
    )
    rango = fields.Integer(default=1)
    numero_muestras = fields.Integer(
        string=u'Número de Muestras',
        required=True
    )
    state = fields.Selection(
        string="Estado",
        selection=[
            ('abierto', 'Abierto'),
            ('procesado', 'Procesado'),
        ],
        default='abierto',
    )
    numero_positivos = fields.Integer('Número Positivos')
    registros_lines_ids = fields.One2many(
        comodel_name='reportes.line',
        inverse_name='reporte_id',
        string=u'Lineas de reporte'
    )

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
            domain = [('estado_muestra', '=', 'yes'), ('reazones_muestra_invalidad', '=', False),
                      ('matriz', '=', False)]
            c = 0
            lista = []
            positivo = False
            indice = indicen = secuencia = 0
            for l in range(0, 96):
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

            data2 = self.env['registro.sobre'].search(domain, order="secuencia", limit=self.numero_muestras)
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
                if len(data2) < 90:
                    raise ValidationError(u'No tiene suficientes registros para continuar')
                else:
                    self.env['reportes.line'].create(rr)

            self.write({'state': 'procesado'})
        else:
            raise ValidationError(
                u'La número de Inicio debe ser mayor al número de fin y el Producto debe ser Ingresado')

    @api.multi
    def click_procesados(self):
        domain = [('state', '=', 'laboratorio'),
                  ('regitro', '=', True), ('sync', '=', False)]
        data2 = self.env['minsa.records.line'].search(domain, order="fecha_registro")
        for record in self:
            for line in record.registros_lines_ids:
                if line.record_lista_id.mobile and not line.positivo and not line.record_lista_id.enviado:
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
        msg_url_parametro = self.env['ir.config_parameter'].get_param(parametro_url) or None
        msg_token_parametro = self.env['ir.config_parameter'].get_param(parametro_token) or None
        if msg_token_parametro is None:
            raise ValidationError('No Existe el Parametro en el Sistema')
        if msg_url_parametro == 'host':
            raise ValidationError('Falta configurar el parametro para el envio de Mensajes')
        msg_url = msg_url_parametro
        msg_token = msg_token_parametro
        msg_texto = " Su resultado de la prueba para el Virus Papiloma Humano es NEGATIVO " \
                    "Continue cuidando su salud. " \
                    "Atte " \
                    "Laboratorio Referencial Regional Tumbes"
        requests.post(msg_url, {'recipient': celular, 'sender': 'EXTRANET', 'body': msg_texto},
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


class ReportesLineas(models.Model):
    _name = 'reportes.line'

    reporte_id = fields.Many2one('reportes', string='Reporte Muestra')
    pos_x = fields.Char()
    pos_y = fields.Integer()
    number = fields.Integer('Secuencia')
    record_lista_id = fields.Many2one('registro.sobre', string=u'Registros')
    record_id = fields.Many2one('minsa.records.line', string=u'Registros')
    codigo_nombre = fields.Char(
        string=u'Nombre',
        related='record_id.codigo',
        store=True
    )
    positivo = fields.Boolean(string=u'Positivo')
    positivo_valores = fields.Selection(
        string="Positivo",
        selection=[
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
        ],
        default='negativo'
    )

    @api.onchange('positivo')
    def _onchange_positivo(self):
        if self.positivo:
            self.positivo_valores = 'positivo'
        else:
            self.positivo_valores = 'negativo'


class Verificacion(models.Model):
    _name = 'verificacion'

    dni = fields.Char(
        string=u'Documento Nacional de Identidad'
    )
    ape_paterno = fields.Char(
        string=u'Apellido Paterno'
    )
    ape_materno = fields.Char(
        string=u'Apellido Materno'
    )
    nombres = fields.Char(
        string=u'Nombres'
    )
    nombres_dase = fields.Char(
        string=u'Nombres'
    )
    birthday = fields.Char(
        string=u'Fecha de Nacimiento'
    )
    legal_street = fields.Char(
        string=u'Domicilio'
    )
    gender = fields.Selection([('male', 'Masculino'), ('female', 'Femenino')])
    image = fields.Binary(
        string=u'Fotografia'
    )
    edad = fields.Char(
        string=u'Edad'
    )
    sobre = fields.Char(
        string=u'Codigo de Sobre'
    )
    sobre1 = fields.Char(
        string=u'Codigo  de Sobre'
    )
    apellidos = fields.Char(
        string=u'Apellidos'
    )
    fecha_muestra = fields.Date(
        string=u'Fecha de muestra'
    )
    fecha_muestra1 = fields.Date(
        string=u'Fecha de muestra'
    )
    resultado = fields.Selection(
        string=u'Resultado',
        selection=[
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
            ('invalido', 'Invalido'),
        ]
    )
    resultado1 = fields.Selection(
        string=u'Resultado',
        selection=[
            ('positivo', 'Positivo'),
            ('negativo', 'Negativo'),
            ('invalido', 'Invalido'),
        ]
    )
    eess = fields.Char(
        string=u'EESS'
    )
    eess_r = fields.Char(
        string=u'EESS'
    )
    establecimiento = fields.Boolean(
        string=u'Establecimiento'
    )

    @api.one
    def click_aprobado(self):
        if not self.dni:
            return {}
            # Consulta de Datos Reniec
        try:
            data = self.env['consultadatos.reniec'].consultardni(self.dni)
            data1 = self.env['registro.sobre'].search([('dni', '=', self.dni)], limit=1)
            if data1:
                data2 = self.env['minsa.records.line'].search([('sobre_id', '=', data1.id)], limit=1)
                fecha = data['nacimiento']['fecha']
            if fecha:
                edad = (datetime.now().date() - datetime.strptime(fecha, '%Y-%m-%d').date()).days / 365
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
            raise ValidationError("%s : %s" % (RENIEC_ERR, ex.message))

    @api.one
    def click_buscar(self):
        data = self.env['registro.sobre'].search([('dni', '=', self.dni)], limit=1)
        data1 = self.env['minsa.records.line'].search([('sobre_id', '=', data.id)], limit=1)
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
            raise ValidationError(u'Paciente no se realizo las pruebas PVH')


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    autorizados = fields.Boolean(
        string=u'Autorizadas'
    )


class ResUsers(models.Model):
    _inherit = 'res.users'

    tipo_documento = fields.Selection(
        string="Tipo de Documento",
        selection=[
            ('dni', 'DNI'),
            ('carnet', 'Carnet de Extranjeria'),
        ],
        default='dni'
    )


class MinsaMicroRede(models.Model):
    _name = 'minsa.micro.rede'
    _rec_name = 'nombre'

    nombre = fields.Char(
        string=u'MicroRed'
    )
    company_ids = fields.One2many(
        comodel_name='res.company',
        inverse_name='microred_id',
        string=u'EESS'
    )


class ResCompany(models.Model):
    _inherit = 'res.company'

    product_id = fields.Many2one(
        comodel_name='product.template',
        string=u'Prueba'
    )
    prefijo = fields.Char(
        string=u'Prefijo',
    )
    codigo_renipes = fields.Char(
        string=u'Codigo Renipes'
    )
    microred_id = fields.Many2one(
        comodel_name='minsa.micro.rede',
        string=u'MicroRed'
    )


class RegistrosGenerales(models.Model):
    _name = 'registros.generales'
    _order = "secuencia asc"

    @api.multi
    def name_get(self):
        return [(obj.id, u'{}{}'.format(obj.eess_origen, obj.numeracion))
                for obj in self]

    eess_origen = fields.Char(
        string=u'EESS Origen'
    )
    eess_destino = fields.Many2one(
        comodel_name='res.company',
        string=u'EESS Destino'
    )
    obstetra_entrega = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Obstetra Origen',
        default=lambda self: self._default_empleado(),
    )
    obstetra_recepciona = fields.Many2one(
        comodel_name='hr.employee',
        string=u'Obstetra Destino'
    )
    numeracion = fields.Char(
        string=u'Rangos'
    )
    fecha = fields.Date(
        string=u'Fecha de Entrega'
    )
    secuencia = fields.Integer(
        string=u'secuencia de registro'
    )

    @api.multi
    def _default_empleado(self):
        user_login = self.env.uid,
        hremployee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_login)])
        return hremployee

    @api.model
    def create(self, vals):
        if not vals.get('secuencia'):
            vals['secuencia'] = self.env['ir.sequence'].next_by_code('registros.generales')  # noqa
        return super(RegistrosGenerales, self).create(vals)
