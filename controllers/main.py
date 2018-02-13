# coding: utf-8

from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition


class ReportBinary(http.Controller):

    @http.route('/web/binary/download_document5', type='http', auth='user')
    @serialize_exception
    def download_document(self, model, filename=None, **kw):
        obj = request.env[model]
        filecontent = obj.get_content()
        response = request.make_response(filecontent, [
            ('Content-Type', 'application/octet-stream;charset=utf-8;'),
            ('Content-Disposition', content_disposition(filename))
        ])
        return response
