package main

/*
 HULK DoS tool on <strike>steroids</strike> goroutines. Just ported from Python with some improvements.
 Original Python utility by Barry Shteiman http://www.sectorix.com/2012/05/17/hulk-web-server-dos-tool/
 This go program licensed under GPLv3.
 Copyright Alexander I.Grafov <grafov@gmail.com>
*/

import (
	"fmt"
	"io/ioutil"
	"math/rand"
	"time"

	"./banner"
	"./load"
)

func fontsList(index int) string {
	files, err := ioutil.ReadDir("./banner/fonts")
	if err != nil {
		fmt.Println(err)
	}
	fonts := []string{}
	for _, file := range files {
		fonts = append(fonts, file.Name())
	}
	return fonts[index]
}
func artGen() {
	s := rand.NewSource(time.Now().Unix())
	r := rand.New(s)
	f, err := banner.GetFontByName("./banner/fonts", fontsList(r.Intn(18)))
	if err != nil {
		fmt.Println("Couldnot find the font")
	}

	banner.PrintMsg("Hulk", f, 80, f.Settings(), "left")
}

func main() {
	artGen()
	load.Smash()
}
