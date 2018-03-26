# -*- encoding: utf-8 -*-

from odoo import api, fields, models

from odoo.exceptions import ValidationError

from utils import Utils

RENIEC_ERR = 'Error!'


class Paciente(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _default_empleado(self):
        user_login = self.env.uid,
        hremployee = self.env['hr.employee'].search([
            ('user_id.id', '=', user_login)])
        return hremployee

    es_promotor = fields.Boolean('Es promotor')
    es_paciente = fields.Boolean('Es paciente')
    es_profesional = fields.Boolean('Es profesional')
    es_pap = fields.Boolean('Es paciente PAP')
    paciente_vph = fields.Boolean('Paciente vph')
    procedimientos_ids = fields.One2many(
        comodel_name='procedimientos',
        inverse_name='dni_id',
        string=u'Líneas de procedimientos'
    )
    registros_ids = fields.One2many(
        comodel_name='minsa.records.line',
        inverse_name='paciente_id',
        string=u'Líneas de registros'
    )
    codigo_sobre = fields.Char(u'Código de sobre')
    codigo_tubo = fields.Char(u'Código de tubo')
    nombres = fields.Char('Nombres', required=True)
    apellidos = fields.Char('Apellidos', required=True)
    dni = fields.Char('DNI', size=8)
    edad = fields.Integer('Edad', default=0)
    mobile = fields.Char(size=9)
    direccion = fields.Char(u'Dirección')
    fecha = fields.Date('Fecha de registro', default=fields.Datetime.now())
    fecha_toma_muestra = fields.Date('Fecha de la toma de muestra')
    codigo_valido_invalido = fields.Char(u'Confirmación de código')
    codigo_valido_invalido1 = fields.Char(u'Confirmación de código')
    estado_muestra = fields.Selection(
        [
            ('yes', 'Si'),
            ('not', 'No'),
        ],
        'Código válido'
    )
    estado_muestra_b = fields.Boolean('Estado de la muestra', default=True)
    estado_muestra_valido_invalido = fields.Selection(
        [
            ('valido', 'Muestra Valida'),
            ('invalido', 'Muestra Invalida'),
        ],
        'Estado de la muestra',
    )
    reazones_muestra_invalidad = fields.Selection(
        [
            ('edadfuera', 'Edad fuera de rango'),
            ('dnisindato', 'DNI sin dato'),
            ('dniequivocado', 'DNI equivocado'),
            ('codigo', 'Código diferente entre tubo y sobre'),
            ('muestra', 'Muestra con moco'),
            ('tubo', 'Tubo sin líquido'),
            ('tubo1', 'Tubo sin cepillo'),
            ('sobre', 'Sobre sin tubo'),
            ('sobre1', 'Sobre sin datos'),
            ('reniec', 'Datos RENIEC no coinciden con sobre'),
        ],
        'Razones de muestra inválida'
    )
    otros = fields.Char('Otros')
    gestante = fields.Selection(
        [
            ('si', 'Si'),
            ('no', 'No'),
        ],
        'Gestante',
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
        [
            ('si', 'Si'),
            ('no', 'No'),
        ],
        'PAP',
        default='si'
    )
    fecha_pap = fields.Date('Fecha')
    fecha_resulado = fields.Date('Fecha de resultado')
    resultado_pap = fields.Selection(
        [
            ('negativo', 'Negativo'),
            ('insactifactorio', 'PAP insactifactorio'),
            ('lei', 'LEI bajo grado'),
            ('lei1', 'LEI alto grado'),
            ('carcinoma', 'Carcinoma Insitu'),
            ('ascos', 'ASCUS'),
            ('asgos', 'AGUS'),
        ],
        'Resultado',
    )
    otro_pap = fields.Char(u'Otro')
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
        help='Used to select automatically the right address according to the context in sales and purchases documents.')  # noqa

    @api.constrains('edad')
    def _check_something(self):
        for record in self:
            if record.edad <= 0 and record.es_pap:
                raise ValidationError('Su edad no debe ser menor a: %s' %
                                      record.edad)

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
                util = Utils()
                edad = util.calcular_edad(fecha)
                if edad < 0:
                    edad = 0
                else:
                    self.edad = edad
        except Exception as ex:
            raise ValidationError('%s : %s' % (RENIEC_ERR, ex.message))

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
                    'reazones_muestra_invalidad':
                        res.reazones_muestra_invalidad or '',
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
                    'reazones_muestra_invalidad':
                        obj.reazones_muestra_invalidad or '',
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
