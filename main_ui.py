import re

import wx
import start_creation


class Main(wx.Frame):
    def __init__(self):
        super(Main, self).__init__(None, title="创建RF脚本", size=(600, 540))
        self.Centre()
        self.main_ui()
        self.Show()

    def main_ui(self):
        self.panpel = wx.Panel(self)
        font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False, 'Consolas')
        title_list = ["接口描述", "URL地址", "请求方式", "请求报文", "作者名称", "用例版本", "待添加变量"]
        pos_y = 20
        for i in range(len(title_list)):
            title = wx.StaticText(self.panpel, label=title_list[i], pos=(20,pos_y))
            title.SetFont(font1)
            pos_y += 50
        button = wx.Button(self.panpel, -1, "提交", pos=(100, 430), size=(400,50)).SetFont(font1)
        self.des_text = wx.TextCtrl(self.panpel, pos=(150, 16), size=(400, 25))   # 接口描述
        self.url_text = wx.TextCtrl(self.panpel, pos=(150, 66), size=(400, 25))   # URL地址
        self.method = wx.ComboBox(self.panpel, -1, size=(400, 25), pos=(150, 116), value="post", choices=["post", "get"])  # 请求方式
        self.post_text = wx.TextCtrl(self.panpel, pos=(150, 166), size=(400, 25))  # 请求报文
        self.name_text = wx.TextCtrl(self.panpel, pos=(150, 216), size=(400, 25))  # 作者名称
        self.ver_text = wx.TextCtrl(self.panpel, pos=(150, 266), size=(400, 25))  # 用例版本
        self.version_text = wx.TextCtrl(self.panpel, pos=(150, 316), size=(400, 45), style=wx.VSCROLL)
        self.success_code = wx.TextCtrl(self.panpel, pos=(150, 386), size=(140, 25))
        success_title = wx.StaticText(self.panpel, label="预期code", pos=(20, 386)).SetFont(font1)
        self.fail_code = wx.TextCtrl(self.panpel, pos=(410, 386), size=(140, 25))
        fail_title = wx.StaticText(self.panpel, label="异常code", pos=(300, 386)).SetFont(font1)
        self.Bind(wx.EVT_BUTTON, self.start)


    def start(self, event):
        method = self.method.GetValue()
        url_str = self.url_text.GetValue()
        module = re.search("\w+(?=api|service)", url_str).group().upper()       # 将模块名匹配出来
        c_name = self.des_text.GetValue()
        if self.des_text.GetValue() !="" and self.url_text.GetValue() !="" and self.name_text.GetValue() !="" and self.ver_text.GetValue() !="":
            if method == "post":
                url_name = url_str.split("/")[-1]
                self.request_post(c_name, module, url_name, url_str)
            else:
                url_name = url_str.split("/")[-2]
                self.request_get(c_name, module, url_name, url_str)
        else:
            error = wx.MessageDialog(None, "可能存在以下必填参数未填！\n  接口描述、URL地址、作者名称、用例版本", "ERROR", wx.ICON_ERROR | wx.OK)
            if error.ShowModal() == wx.OK:
                error.Destroy()

    def request_get(self, c_name, module, url_name, url_str):
        new_url = "/".join(url_str.split("/")[:-1])
        body = '{"body": ' + url_str.split("/")[-1] + '}'
        all_str = '${G_' + module + '_' + url_name + '}' + '    ' + new_url + '    ' + f"#{c_name}"
        self.version_text.SetLabel(all_str)
        creat = start_creation.Creation(self.des_text.GetValue(), self.url_text.GetValue())
        creat.start_op(body, self.ver_text.GetValue(), self.name_text.GetValue(),
                       self.method.GetValue()
                       , self.success_code.GetValue(), self.fail_code.GetValue())
        self.message()

    def request_post(self, c_name, module, url_name, url_str):
        all_str = '${G_' + module + '_' + url_name + '}' + '    ' + url_str + '    ' + f"#{c_name}"
        self.version_text.SetLabel(all_str)
        creat = start_creation.Creation(self.des_text.GetValue(), self.url_text.GetValue())
        creat.start_op(self.post_text.GetValue(), self.ver_text.GetValue(), self.name_text.GetValue(),
                       self.method.GetValue()
                       , self.success_code.GetValue(), self.fail_code.GetValue())
        self.message()

    def message(self):
        tone = wx.MessageDialog(None, "RF文件已生成至同级目录", "提示", wx.ICON_QUESTION | wx.OK)
        if tone.ShowModal() == wx.OK:
            tone.Destroy()


app = wx.App()
Main()
app.MainLoop()
