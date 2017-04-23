#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import urllib
import urllib2
import cookielib
import socket
from gzip import GzipFile
from StringIO import StringIO


class UrlRequestException(Exception): pass


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

    def EnableProxyHandler(self, proxyDict):
        """Enable proxy handler
        args:
            proxyDict:proxy info for connect, eg. {'http':'10.182.45.231:80','https':'10.182.45.231:80'}
        """
        if not isinstance(proxyDict, dict):
            raise UrlRequestException('you must specify proxyDict when enabled Proxy')
        self.__opener.add_handler(urllib2.ProxyHandler(proxyDict))

    def DisableProxyHandler(self):
        """Disable proxy handler"""
        self.__RemoveInstalledHandler('ProxyHandler')

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

    def Request(self, url, data=None, headers={}, timeout=30):
        if url is None or url == '':
            raise ValueError("Url can't be empty!")
        if 'user-agent' not in headers:
            headers['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:53.0) Gecko/20100101 Firefox/53.0'
        if 'Accept-Encoding' not in headers:
            headers['Accept-Encoding'] = 'gzip'
        self.__opener.addheaders = headers.items()

        try:
            if data is not None:
                if isinstance(data, dict):
                    req = self.__opener.open(url, data=urllib.urlencode(data), timeout=timeout)
                else:
                    req = self.__opener.open(url, data=data, timeout=timeout)
            else:
                req = self.__opener.open(url, timeout=timeout)

            if req.headers.get("content-encoding") == "gzip":
                gz = GzipFile(fileobj=StringIO(req.read()))
                resData = UrlRequestResponseData(gz.read(), url, req.info().dict, req.getcode())
            else:
                resData = UrlRequestResponseData(req.read(), url, req.info().dict, req.getcode())
            req.close()

            return resData
        except urllib2.HTTPError, e:
            if e.headers.get("content-encoding") == "gzip":
                gz = GzipFile(fileobj=StringIO(e.fp.read()))
                return UrlRequestResponseData(gz.read(), url, e.headers, e.code)
            else:
                return UrlRequestResponseData(e.fp.read(), url, e.headers, e.code)
        except (urllib2.URLError, socket.error, socket.timeout), e:
            return UrlRequestResponseData(str(e), url, None, -1)

if __name__ == '__main__':
    r = UrlRequest()
    d = r.Request('http://127.0.0.1:445')
    print d.headers
