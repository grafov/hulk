Hulk DoS tool
=============

HULK DoS tool ported to Go language from Python. 
Original Python utility by Barry Shteiman http://www.sectorix.com/2012/05/17/hulk-web-server-dos-tool/
I just ported utility as is quick and dirty. Original functions names are keeped and original logic mostly keeped too.

This tool targeted for load testing and may really down badly configured server. Use it wisely.

Examples:

    $ hulk -site http://example.com/test/ 2>/dev/null

    $ HULKMAXPROCS=4096 hulk -site http://example.com 2>/tmp/errlog

Useful environment vars:

* GOMAXPROCS
  Set it to number of your CPUs or higher.
* HULKMAXPROCS
  Limit the connection pool (1024 by default). To create high load use higher values.

More details: http://siberian.laika.name/node/7 


License
=======

Copyright Alexander I.Grafov <grafov@gmail.com>

Original HULK utility authority of Barry Shteiman (http://sectorix.com). There are not any references to license in the original source than it not under GPL. Ask author of the original utility about license.
 
Go version of HULK licensed under GPLv3. See LICENSE.
