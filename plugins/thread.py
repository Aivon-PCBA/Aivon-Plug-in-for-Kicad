#https://opensource.org/licenses/MIT

import json
import os
import uuid
import webbrowser
import shutil
import wx
import tempfile
from threading import Thread
from urllib import error, request

from .result_event import *
from .config import *
from .process import *


def _post_multipart(url, fields, file_field, file_path):
    boundary = '----KiCadAivonBoundary' + uuid.uuid4().hex
    body = bytearray()

    for name, value in fields.items():
        body.extend(
            '--{}\r\n'
            'Content-Disposition: form-data; name="{}"\r\n'
            '\r\n'
            '{}\r\n'.format(boundary, name, value).encode('utf-8'))

    filename = os.path.basename(file_path)
    body.extend(
        '--{}\r\n'
        'Content-Disposition: form-data; name="{}"; filename="{}"\r\n'
        'Content-Type: application/zip\r\n'
        '\r\n'.format(boundary, file_field, filename).encode('utf-8'))

    with open(file_path, 'rb') as upload_file:
        body.extend(upload_file.read())

    body.extend('\r\n--{}--\r\n'.format(boundary).encode('utf-8'))

    req = request.Request(
        url,
        data=bytes(body),
        headers={
            'Content-Type': 'multipart/form-data; boundary={}'.format(boundary),
        },
        method='POST')

    try:
        with request.urlopen(req) as rsp:
            return rsp.status, rsp.read().decode('utf-8')
    except error.HTTPError as http_error:
        return http_error.code, http_error.read().decode('utf-8', errors='replace')


class AivonThread(Thread):
    def __init__(self, wxObject):
        Thread.__init__(self)
        self.process = AivonProcess()
        self.wxObject = wxObject
        self.start()

    def run(self):

        temp_dir = tempfile.mkdtemp()
        zip_path = None
        urls = None

        try:
            self.report(5)

            self.process.get_gerber_file(temp_dir)

            self.report(15)

            self.process.get_netlist_file(temp_dir)

            self.report(25)

            self.process.get_components_file(temp_dir)

            self.report(35)

            gerberData = self.process.get_gerber_parameter()

            self.report(45)

            p_name = self.process.get_name()

            zip_path = shutil.make_archive(p_name, 'zip', temp_dir)

            self.report(55)

            upload_url = baseUrl + uploadPath

            self.report(65)

            status_code, response_text = _post_multipart(
                upload_url,
                {
                    'boardWidth': gerberData['boardWidth'],
                    'boardHeight': gerberData['boardHeight'],
                    'boardLayer': gerberData['boardLayer'],
                },
                'upload[file]',
                zip_path)

            self.report(75)

            if status_code < 200 or status_code >= 300:
                raise Exception(
                    'Upload API returned HTTP {} from {}. '
                    'Check baseUrl in config.py.'.format(
                        status_code, upload_url))

            try:
                urls = json.loads(response_text)
            except ValueError:
                preview = response_text.strip()[:200]
                raise Exception(
                    'Upload API did not return JSON from {}. '
                    'Response preview: {}'.format(upload_url, preview))

            if 'redirect' not in urls:
                raise Exception(urls.get('error', response_text))

            readsofar = 0
            totalsize = os.path.getsize(zip_path)
            with open(zip_path, 'rb') as file:
                while True:
                    data = file.read(10)
                    if not data:
                        break
                    readsofar += len(data)
                    percent = readsofar * 1e2 / totalsize
                    self.report(75 + percent / 9)

        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            self.report(-1)
            return
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
            if zip_path and os.path.exists(zip_path):
                os.remove(zip_path)

        webbrowser.open(urls['redirect'])
        self.report(-1)

    def report(self, status):
        wx.PostEvent(self.wxObject, ResultEvent(status))
