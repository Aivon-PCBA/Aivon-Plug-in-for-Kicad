import os
import wx
import pcbnew

from .thread import *
from .result_event import *
from .process import *

class KiCadToAivonForm(wx.Dialog):
    def __init__(self):
        wx.Dialog.__init__(
            self,
            None,
            id=wx.ID_ANY,
            title=u"AIVON is processing...",
            pos=wx.DefaultPosition,
            size=wx.DefaultSize,
            style=wx.DEFAULT_DIALOG_STYLE)

        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)

        bSizer1 = wx.BoxSizer(wx.VERTICAL)

        self.m_gaugeStatus = wx.Gauge(
            self, wx.ID_ANY, 100, wx.DefaultPosition, wx.Size(
                300, 20), wx.GA_HORIZONTAL)
        self.m_gaugeStatus.SetValue(0)
        bSizer1.Add(self.m_gaugeStatus, 0, wx.ALL, 5)

        self.SetSizer(bSizer1)
        self.Layout()
        bSizer1.Fit(self)

        self.Centre(wx.BOTH)

        EVT_RESULT(self, self.updateDisplay)
        AivonThread(self)

    def updateDisplay(self, status):
        if status.data == -1:
            pcbnew.Refresh()
            self.Destroy()
        else:
            self.m_gaugeStatus.SetValue(int(status.data))


class AivonPlugin(pcbnew.ActionPlugin):
    def defaults(self):
        self.name = "AIVON Plug-in for KiCad"
        self.category = "Manufacturing"
        self.description = "Start prototype and assembly by sending files to AIVON with just one click."
        self.show_toolbar_button = True
        plugin_dir = os.path.dirname(os.path.abspath(__file__))
        self.icon_file_name = os.path.join(plugin_dir, 'icon.png')
        self.dark_icon_file_name = os.path.join(plugin_dir, 'icon.png')

    def Run(self):
        KiCadToAivonForm().Show()
