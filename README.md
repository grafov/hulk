Hulk DoS tool
=============

HULK DoS tool ported to Go language from Python. 
Original Python utility by Barry Shteiman http://www.sectorix.com/2012/05/17/hulk-web-server-dos-tool/
I just ported the code as is quick and dirty. Original functions names are keeped and original logic mostly keeped too.

The main difference from Python version layed in Golang architecture for concurrency: the goroutines. hulk.py runs
a new thread for each connection in the connection pool so it uses hundreds and thousands of threads. 
hulk.go just uses lightweight goroutines that used only tens of threads (commonly golang runtime started one thread for
CPU core + several service threads). This architecture allows golang version better consume resources and got much higher 
connection pool on the same hardware than Python version can.

This tool targeted for stress testing and may really down badly configured server or badly made app. Use it carefully.

Examples:

    $ hulk -site http://example.com/test/ 2>/dev/null

    $ HULKMAXPROCS=4096 hulk -site http://example.com 2>/tmp/errlog

Useful environment vars:

* GOMAXPROCS
  Set it to number of your CPUs or higher (no more actual for latest golang versions).
* HULKMAXPROCS
  Limit the connection pool (1024 by default).

More details: http://old.siberian.laika.name/node/7 

Update: well, I created this utility for one time task when I only played a bit with golang. Surprisingly I found that
this utility used by other people, got some stars on github and even included in [BlackArch Linux distro](http://blackarch.org/dos.html). So I cleaned up code a bit.

License
=======

I think it may be public domain because of it is just simple and short piece of code but for reason I don't remember already
I have choose GPL for it. Okey. So, Go version of HULK licensed under GPLv3. See LICENSE.

I am not related with original HULK utility in Python. Original HULK utility is authority of Barry Shteiman (http://sectorix.com). There are not any references to license in the original source then it is not under GPL. Ask author of the original utility about license. 
 

