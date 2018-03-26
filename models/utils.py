# -*- encoding: utf-8 -*-

from datetime import datetime


class Utils(object):
    def calcular_edad(self, fecha):
        edad = 0
        try:
            if fecha:
                if datetime.strptime(fecha, '%Y-%m-%d'):
                    edad = (datetime.now().date() - datetime.strptime(fecha,
                                                                      '%Y-%m-%d').date()).days / 365 # noqa
                else:
                    pass
            else:
                pass
            return edad
        except ValueError:
            raise ValueError('Formato de fecha incorrecto.')
