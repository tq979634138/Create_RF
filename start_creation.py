import copy
import json
import os
import re
import sys
import random


class Creation:
    def __init__(self, c_name, url):
        self.module = re.search("\w+(?=api|service)", url).group().upper()
        self.url_name = url.split("/")[-1]
        config_path = self.resource_path(os.path.join("config","content.json"))
        with open(config_path, 'r', encoding="utf8") as f:
            self.js_di = json.loads(f.read())
        self.path = os.getcwd() + "/" + c_name + ".robot"  # 获取要写入的文件路径

    def resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):  # 是否Bundle Resource
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def start_op(self, body, ver, writer, method="post", su_code=0000, fail_code=9999):
        body_di = json.loads(body)
        write_list = self.write_body(body_di)
        num = 1
        self.ver = ver
        self.writer = writer
        with open(self.path, "w", encoding="utf8") as file:
            num_str = "{:0>3d}".format(num)
            success_str = f"{num_str}_所有参数正常取值_校验成功"
            su_str = success_str + "\n    [Documentation]    *用例名称* " + success_str + "\n"
            file.write(self.js_di["前置"])  # 写入RF脚本的前置参数
            document = self.get_document(num_str)
            file.write("\n" + su_str + document + "\n")  # 写入第一个所有参数正常用例
            [file.write("    " + str(i)) for i in write_list]  # 所有参数正常传参
            self.write_fail(body_di, write_list, file, num, fail_code)
            create_list = self.write_arg(body_di, file, su_code)     # 写入模板，并返回需要创建list的列表
            file.writelines(create_list)
            if method == "post":
                self.method_post(body_di, file)
            else:
                self.method_get(body_di, file)

    def get_document(self, num_str):
        ver_str = f"    ...    *用例版本* {self.ver}"
        writer_str = f"    ...    *用例作者* {self.writer}"
        case_number = f"    ...\n    ...    *用例编号* {self.module}_{self.url_name}_{num_str}\n    ..."
        document = f"{case_number}\n{ver_str}\n{self.js_di['用例类型']}\n{writer_str}\n{self.js_di['用例文档']}"
        return document

    def write_body(self, body_di):
        write_list = []
        for di_key in body_di.keys():
            if type(body_di[di_key]) == list and body_di[di_key]:
                write_list.append(body_di[di_key][0])
            elif type(body_di[di_key]) != list:
                write_list.append(body_di[di_key])
            elif not body_di[di_key]:
                write_list.append("${EMPTY}")
        return write_list

    # 封装get请求
    def method_get(self, body_di, file):
        body = list(body_di.keys())[0]
        if self.module == "bitt":
            requs_str = "    ${res}    http请求_get    ${G_HOST_INTERFACE_BITT}${G_BITT_" + self.url_name+"}"+"${"+body+"}\n"
            file.write("\n" + requs_str + self.js_di["response校验"])
        else:
            requs_str = "    ${res}    http请求_get    ${G_HOST_INTERFACE}${G_" + self.url_name+"}"+"${"+body+"}\n"
            file.write("\n" + requs_str + self.js_di["response校验"])

    # 封装post请求
    def method_post(self, body_di, file):
        data_str = "    ".join([i + "=${" + i + "}" for i in body_di.keys()])
        file.write("    ${data}    Create Dictionary    " + data_str)
        if self.module == "BITT":
            requs_str = "    ${res}    http请求_post    ${G_HOST_INTERFACE_BITT}${G_BITT_" + self.url_name + "}    ${data_json}\n"
            file.write("\n" + self.js_di["创建json"] + requs_str + self.js_di["response校验"])
        else:
            requs_str = "    ${res}    http请求_post    ${G_HOST_INTERFACE}${G_" + self.module + "_" + self.url_name + "}    ${data_json}\n"
            file.write("\n" + self.js_di["创建json"] + requs_str + self.js_di["response校验"])

    # 写入模板
    def write_arg(self, body_di, file, su_code):
        create_list = []
        body_list = list(body_di.keys())
        for li_key in body_list:
            if type(body_di[li_key]) == list:
                create_list.append("    ${" + li_key + "}    Create List    ${" + li_key + "}\n")  # 需要创建空列表的参数
                # body_list.pop(body_list.index(li_key))
        arg_str = "    ".join(["${" + i + "}" for i in body_list])  # 组装成一个字符串
        file.write(self.js_di["模板"] + "\n    [Arguments]    " + arg_str + "    ${expect_code}=" + str(su_code) + self.js_di["模板文档"] + "\n")  # 写入模板文档
        return create_list

    # 写入异常场景用例
    def write_fail(self, body_di, value_list, file, num, fail_code):
        for a in range(len(value_list)):
            body_list = copy.deepcopy(value_list)  # 定义正常传参列表，以便各错误用例带入
            success_key = [i for i in body_di.keys()]
            for f in self.js_di["异常"].keys():
                num += 1
                num_str = "{:0>3d}".format(num)
                document = self.get_document(num_str)
                fail_str = f"{num_str}_参数{success_key[a]}传{f}_校验失败结果"  # 失败用例名称
                su_str = fail_str + "\n    [Documentation]    *用例名称* " + fail_str + "\n"  # 失败用例文档
                body_list[a] = str(random.choice(self.js_di["异常"][f]))  # 生成错误传参的列表
                fail_a = "    ".join([str(i) for i in body_list])  # 组装成一个字符串
                file.write("\n" + su_str + document + "\n" + "    " + fail_a + f"    {fail_code}")  # 写入


if __name__ == '__main__':
    c = Creation("查询", "/bittapi/v1/report/query/wf/passRateReportQuery")
    body = '{"timeUnit":1,"beginTime":1642348800000,"endTime":1645027199000,"bizTypes":[],"provinceIds":["100"]}'
    c.start_op(body, "bitt1.0.1", "tangziqiangwx")
