#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import urllib
import urllib2
import cookielib
import socket
from gzip import GzipFile
from StringIO import StringIO


class UrlRequestResponseData:
    def __init__(self, content=None, url=None, headers=None, code=None):
        self.content = content
        self.url = url
        self.headers = headers
        self.code = code


class UrlRequest:
    def __init__(self):
        self.__opener = urllib2.build_opener()
        self.EnableCookie()

    def __FindInstalledHandlers(self,handlerName):
        nameList = [i.__class__.__name__ for i in self.__opener.handlers]
        if handlerName not in nameList:
            return None
        return [self.__opener.handlers[i] for i, n in enumerate(nameList) if n == handlerName]

    def __RemoveInstalledHandler(self,handlerName):
        searchedHandlers = self.__FindInstalledHandlers(handlerName)
        if searchedHandlers:
            for i in searchedHandlers:
                self.__opener.handlers.remove(i)
                for protocol in self.__opener.handle_error.keys():
                    handlerDict = self.__opener.handle_error[protocol]
                    for dictKey in handlerDict:
                        for item in handlerDict.get(dictKey):
                            if item == i:
                                handlerDict.get(dictKey).remove(item)

                self.__RemoveHandlerInDictList(self.__opener.handle_error, i)
                self.__RemoveHandlerInDictList(self.__opener.process_request, i)
                self.__RemoveHandlerInDictList(self.__opener.process_response, i)

    def __RemoveHandlerInDictList(self,dictList,handlerWantRemove):
        for protocol in dictList.keys():
            handlerList = self.__opener.handle_open[protocol]
            for item in handlerList:
                if item == handlerWantRemove:
                    handlerList.remove(item)

    def EnableAutoRedirect(self):
        """Enable auto redirect 301,302... pages"""
        self.__opener.add_handler(urllib2.HTTPRedirectHandler())

    def DisableAutoRedirect(self):
        """Disable auto redirect 301,302... pages"""
        self.__RemoveInstalledHandler('HTTPRedirectHandler')

    def EnableCookie(self):
        """Enable cookie, need this after your login"""
        cj = cookielib.CookieJar()
        self.__opener.add_handler(urllib2.HTTPCookieProcessor(cj))

    def DisableCookie(self):
        """Disable cookie"""
        self.__RemoveInstalledHandler('HTTPCookieProcessor')

    def Request(self, url, data=None, headers={}, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        if url is None or url == '':
            raise ValueError("Url can't be empty!")
        if 'user-agent' not in headers:
            headers['user-agent'] = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
        if 'Accept-Encoding' not in headers:
            headers['Accept-Encoding'] = 'gzip'
        self.__opener.addheaders = headers.items()

        try:
            if data is not None:
                req = self.__opener.open(url, data=urllib.urlencode(data), timeout=timeout)
            else:
                req = self.__opener.open(url, timeout=timeout)

            if req.headers.get("content-encoding") == "gzip":
                gz = GzipFile(fileobj=StringIO(req.read()))
                resData = UrlRequestResponseData(gz.read(), req.geturl(), req.info().dict, req.getcode())
            else:
                resData = UrlRequestResponseData(req.read(), req.geturl(), req.info().dict, req.getcode())
            req.close()

            return resData
        except urllib2.HTTPError, e:
            return UrlRequestResponseData(e.fp.read(), '', e.headers, e.code)

    def RequestHeader(self, url, data=None, headers={}, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        """Only Request header of the url, use HEAD method to request, we can use this test if a url is accessable"""
        request = urllib2.Request(url, data=data, headers=headers)
        request.get_method = lambda: 'HEAD'
        req = urllib2.urlopen(request, timeout=timeout)
        resData = UrlRequestResponseData(req.read(), req.geturl(), req.info().dict, req.getcode())
        return resData


if __name__ == '__main__':
    r = UrlRequest()
    d = r.RequestHeader('https://127.0.0.1')
    print d.headers
