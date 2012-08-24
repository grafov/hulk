hulk dos tool
=============

HULK DoS tool ported to Go language from Python. 
Original Python utility by Barry Shteiman http://www.sectorix.com/2012/05/17/hulk-web-server-dos-tool/
I just ported utility as is quick and dirty. Original functions names are keeped and original logic mostly keeped too.

This tool targeted for load testing and may really down badly configured server. Use it wisely.

Example:

    $ hulk -url http://example.com/test/

Useful environment vars:

* GOMAXPROCS - set it to number of your CPUs or higher
* HULKMAXPROC - limit the connection pool

license
=======

This go program licensed under GPLv3. See LICENSE.
Copyright Alexander I.Grafov <grafov@gmail.com>

 