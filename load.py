import logging
import random
import re
import ssl
import subprocess
import copy
import time
import os
from base64 import b64encode
from collections import OrderedDict

from requests.sessions import Session
from requests.adapters import HTTPAdapter
from requests.compat import urlparse, urlunparse
from requests.exceptions import RequestException

from urllib3.util.ssl_ import create_urllib3_context, DEFAULT_CIPHERS

def headersKey():
    with open('headeruseragents.txt', 'r') as r:
        headerUseragents = r.read().replace(",", '').split()
    return headerUseragents

DEFAULT_USER_AGENT = random.choice(headersKey())

DEFAULT_HEADERS = OrderedDict(
    (
        ("Host", None),
        ("Connection", "keep-alive"),
        ("Upgrade-Insecure-Requests", "1"),
        ("User-Agent", DEFAULT_USER_AGENT),
        (
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        ),
        ("Accept-Language", "en-US,en;q=0.9"),
        ("Accept-Encoding", "gzip, deflate"),
    )
)

DEFAULT_CIPHERS += ":!ECDHE+SHA:!AES128-SHA:!AESCCM:!DHE:!ARIA"


class HulkAdapter(HTTPAdapter):
    """ HTTPS adapter that creates a SSL context with custom ciphers """

    def get_connection(self, *args, **kwargs):
        conn = super(HulkAdapter, self).get_connection(*args, **kwargs)

        if conn.conn_kw.get("ssl_context"):
            conn.conn_kw["ssl_context"].set_ciphers(DEFAULT_CIPHERS)
        else:
            context = create_urllib3_context(ciphers=DEFAULT_CIPHERS)
            conn.conn_kw["ssl_context"] = context

        return conn


class HulkError(RequestException):
    pass


class HulkCaptchaError(HulkError):
    pass


class HulkScraper(Session):
    def __init__(self, *args, **kwargs):
        self.delay = kwargs.pop("delay", None)

        headers = OrderedDict(kwargs.pop("headers", DEFAULT_HEADERS))

        headers.setdefault("User-Agent", DEFAULT_USER_AGENT)

        super(HulkScraper, self).__init__(*args, **kwargs)

        self.headers = headers
        self.org_method = None

        self.mount("https://", HulkAdapter())

    @staticmethod
    def is_Hulk_iuam_challenge(resp):
        return (
            resp.status_code in (503, 429)
            and resp.headers.get("Server", "").startswith("Hulk")
            and b"jschl_vc" in resp.content
            and b"jschl_answer" in resp.content
        )

    @staticmethod
    def is_Hulk_captcha_challenge(resp):
        return (
            resp.status_code == 403
            and resp.headers.get("Server", "").startswith("Hulk")
            and b"/cdn-cgi/l/chk_captcha" in resp.content
        )

    def request(self, method, url, *args, **kwargs):
        resp = super(HulkScraper, self).request(method, url, *args, **kwargs)

        if self.is_Hulk_captcha_challenge(resp):
            self.counter_captcha(resp, url)

        if self.is_Hulk_iuam_challenge(resp):
            resp = self.counter_cf(resp, **kwargs)

        return resp

    def bypassed(self, url, resp=None):
        cookie_domain = ".{}".format(urlparse(url).netloc)
        return (
            self.cookies.get("cf_clearance", None, domain=cookie_domain) or
            (resp and resp.cookies.get("cf_clearance", None, domain=cookie_domain))
        )

    def counter_captcha(self, resp, url):
        error = (
            "Hulk captcha challenge presented for %s (hulk cannot solve captchas)"
            % urlparse(url).netloc
        )
        if ssl.OPENSSL_VERSION_NUMBER < 0x10101000:
            error += ". Your OpenSSL version is lower than 1.1.1. Please upgrade your OpenSSL library and recompile Python."

        raise HulkCaptchaError(error, response=resp)

    def counter_cf(self, resp, **original_kwargs):
        start_time = time.time()

        body = resp.text
        parsed_url = urlparse(resp.url)
        domain = parsed_url.netloc
        challenge_form = re.search(r'\<form.*?id=\"challenge-form\".*?\/form\>',body, flags=re.S).group(0) # find challenge form
        method = re.search(r'method=\"(.*?)\"', challenge_form, flags=re.S).group(1)
        if self.org_method is None:
            self.org_method = resp.request.method
        submit_url = "%s://%s%s" % (parsed_url.scheme,
                                     domain,
                                    re.search(r'action=\"(.*?)\"', challenge_form, flags=re.S).group(1).split('?')[0])

        Hulk_kwargs = copy.deepcopy(original_kwargs)

        headers = Hulk_kwargs.setdefault("headers", {})
        headers["Referer"] = resp.url

        try:
            Hulk_kwargs["params"] = dict()
            Hulk_kwargs["data"] = dict()
            if len(re.search(r'action=\"(.*?)\"', challenge_form, flags=re.S).group(1).split('?')) != 1:
                for param in re.search(r'action=\"(.*?)\"', challenge_form, flags=re.S).group(1).split('?')[1].split('&'):
                    Hulk_kwargs["params"].update({param.split('=')[0]:param.split('=')[1]})

            for input_ in re.findall(r'\<input.*?(?:\/>|\<\/input\>)', challenge_form, flags=re.S):
                if re.search(r'name=\"(.*?)\"',input_, flags=re.S).group(1) != 'jschl_answer':
                    if method == 'POST':
                        Hulk_kwargs["data"].update({re.search(r'name=\"(.*?)\"',input_, flags=re.S).group(1):
                                                          re.search(r'value=\"(.*?)\"',input_, flags=re.S).group(1)})
                    elif method == 'GET':
                        Hulk_kwargs["params"].update({re.search(r'name=\"(.*?)\"',input_, flags=re.S).group(1):
                                                          re.search(r'value=\"(.*?)\"',input_, flags=re.S).group(1)})
            if method == 'POST':
                for k in ("jschl_vc", "pass"):
                    if k not in Hulk_kwargs["data"]:
                        raise ValueError("%s is missing from challenge form" % k)
            elif method == 'GET':
                for k in ("jschl_vc", "pass"):
                    if k not in Hulk_kwargs["params"]:
                        raise ValueError("%s is missing from challenge form" % k)

        except Exception as e:
    
            raise ValueError(
                "Unable to parse Cloudfare anti-bot IUAM page: %s %s"
                % (e)
            )

        answer, delay = self.solve_challenge(body, domain)
        if method == 'POST':
            Hulk_kwargs["data"]["jschl_answer"] = answer
        elif method == 'GET':
            Hulk_kwargs["params"]["jschl_answer"] = answer

        Hulk_kwargs["allow_redirects"] = False

        time.sleep(max(delay - (time.time() - start_time), 0))

        redirect = self.request(method, submit_url, **Hulk_kwargs)
        if "Location" in redirect.headers:
            redirect_location = urlparse(redirect.headers["Location"])

            if not redirect_location.netloc:
                redirect_url = urlunparse(
                    (
                        parsed_url.scheme,
                        domain,
                        redirect_location.path,
                        redirect_location.params,
                        redirect_location.query,
                        redirect_location.fragment,
                    )
                )
                return self.request(method, redirect_url, **original_kwargs)
            return self.request(method, redirect.headers["Location"], **original_kwargs)
        elif "Set-Cookie" in redirect.headers:
            if 'cf_clearance' in redirect.headers['Set-Cookie']:
                resp = self.request(self.org_method, submit_url, cookies = redirect.cookies)
                return resp
            else:
                return self.request(method, submit_url, **original_kwargs)
        else:
            resp = self.request(self.org_method, submit_url, **Hulk_kwargs)
            return resp


    def solve_challenge(self, body, domain):
        try:
            all_scripts = re.findall(r'\<script type\=\"text\/javascript\"\>\n(.*?)\<\/script\>',body, flags=re.S)
            javascript = next(filter(lambda w: "jschl-answer" in w,all_scripts)) #find the script tag which would have obfuscated js
            challenge, ms = re.search(
                r"setTimeout\(function\(\){\s*(var "
                r"s,t,o,p,b,r,e,a,k,i,n,g,f.+?\r?\n[\s\S]+?a\.value\s*=.+?)\r?\n"
                r"(?:[^{<>]*},\s*(\d{4,}))?",
                javascript, flags=re.S
            ).groups()

            innerHTML = ''
            for i in javascript.split(';'):
                if i.strip().split('=')[0].strip() == 'k':   
                    k = i.strip().split('=')[1].strip(' \'')    
                    innerHTML = re.search(r'\<div.*?id\=\"'+k+r'\".*?\>(.*?)\<\/div\>',body).group(1) 

            challenge = """
                var document = {
                    createElement: function () {
                      return { firstChild: { href: "http://%s/" } }
                    },
                    getElementById: function () {
                      return {"innerHTML": "%s"};
                    }
                  };

                %s; a.value
            """ % (
                domain,
                innerHTML,
                challenge,
            )

            challenge = b64encode(challenge.encode("utf-8")).decode("ascii")
            delay = self.delay or (float(ms) / float(1000) if ms else 8)
        except Exception:
            raise ValueError(
                "Unable to identify IUAM Javascript on website."
            )

        js = (
            """\
            var atob = Object.setPrototypeOf(function (str) {\
                try {\
                    return Buffer.from("" + str, "base64").toString("binary");\
                } catch (e) {}\
            }, null);\
            var challenge = atob("%s");\
            var context = Object.setPrototypeOf({ atob: atob }, null);\
            var options = {\
                filename: "iuam-challenge.js",\
                contextOrigin: "Hulk:iuam-challenge.js",\
                contextCodeGeneration: { strings: true, wasm: false },\
                timeout: 5000\
            };\
            process.stdout.write(String(\
                require("vm").runInNewContext(challenge, context, options)\
            ));\
        """
            % challenge
        )
        stderr = ''

        try:
            node = subprocess.Popen(
                ["node", "-e", js], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True
                )
            result, stderr = node.communicate()
            if node.returncode != 0:
                stderr = "Node.js Exception:\n%s" % (stderr or None)
                raise subprocess.CalledProcessError(node.returncode, "node -e ...", stderr)
        except OSError as e:
            if e.errno == 2:
                raise EnvironmentError(
                    "Missing Node.js runtime. Node is required and must be in the PATH (check with `node -v`). Your Node binary may be called `nodejs` rather than `node`, in which case you may need to run `apt-get install nodejs-legacy` on some Debian-based systems. (Please read the hulk"
                    " README's Dependencies section: https://github.com/Anorov/Hulk-scrape#dependencies."
                )
            raise
        except Exception:
            logging.error("Error executing Hulk IUAM Javascript.")
            raise

        try:
            float(result)
        except Exception:
            raise ValueError(
                "IUAM challenge returned unexpected answer."
            )

        return result, delay

    @classmethod
    def doser(cls, sess=None, **kwargs):
        """
        Convenience function for creating a ready-to-go HulkScraper object.
        """
        scraper = cls(**kwargs)

        if sess:
            attrs = [
                "auth",
                "cert",
                "cookies",
                "headers",
                "hooks",
                "params",
                "proxies",
                "data",
            ]
            for attr in attrs:
                val = getattr(sess, attr, None)
                if val:
                    setattr(scraper, attr, val)

        return scraper


    @classmethod
    def get_tokens(cls, url, user_agent=None, **kwargs):
        scraper = cls.doser()
        if user_agent:
            scraper.headers["User-Agent"] = user_agent

        try:
            resp = scraper.get(url, **kwargs)
            resp.raise_for_status()
        except Exception:
            logging.error("'%s' returned an error. Could not collect tokens." % url)
            raise

        domain = urlparse(resp.url).netloc
        cookie_domain = None

        for d in scraper.cookies.list_domains():
            if d.startswith(".") and d in ("." + domain):
                cookie_domain = d
                break
        else:
            raise ValueError(
                'Unable to find cookies. Does the site actually have "I\'m Under Attack Mode" enabled?'
            )

        return (
            {
                "__cfduid": scraper.cookies.get("__cfduid", "", domain=cookie_domain),
                "cf_clearance": scraper.cookies.get(
                    "cf_clearance", "", domain=cookie_domain
                ),
            },
            scraper.headers["User-Agent"],
        )

    @classmethod
    def get_cookie_string(cls, url, user_agent=None, **kwargs):

        tokens, user_agent = cls.get_tokens(url, user_agent=user_agent, **kwargs)
        return "; ".join("=".join(pair) for pair in tokens.items()), user_agent


doser = HulkScraper.doser
get_tokens = HulkScraper.get_tokens
get_cookie_string = HulkScraper.get_cookie_string
