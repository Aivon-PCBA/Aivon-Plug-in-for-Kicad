#https://opensource.org/licenses/MIT

import json
import os
import webbrowser
import shutil
import requests
import wx
import tempfile
from threading import Thread
from .result_event import *
from .config import *
from .process import *


class AivonThread(Thread):
    def __init__(self, wxObject):
        Thread.__init__(self)
        self.process = AivonProcess()
        self.wxObject = wxObject
        self.start()

    def run(self):

        temp_dir = tempfile.mkdtemp()
        zip_path = None

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

            with open(zip_path, 'rb') as upload_file:
                rsp = requests.post(
                    upload_url, files={'upload[file]': upload_file}, data={
                        'boardWidth': gerberData['boardWidth'],
                        'boardHeight': gerberData['boardHeight'],
                        'boardLayer': gerberData['boardLayer']
                    })

            self.report(75)

            if not rsp.ok:
                raise Exception(
                    'Upload API returned HTTP {} from {}. '
                    'Check baseUrl in config.py.'.format(
                        rsp.status_code, upload_url))

            try:
                urls = rsp.json()
            except ValueError:
                preview = rsp.text.strip()[:200]
                raise Exception(
                    'Upload API did not return JSON from {}. '
                    'Response preview: {}'.format(upload_url, preview))

            if 'redirect' not in urls:
                raise Exception(urls.get('error', rsp.text))

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
