package load

import (
	"fmt"
	"io/ioutil"
	"regexp"
)

func readheaderUseragents() string {
	{
		data, err := ioutil.ReadFile("../headerUseragents.txt")
		if err != nil {
			fmt.Println("Can't read file")
			panic(err)
		}
		var re = regexp.MustCompile(`\r?\n`)
		var output = re.ReplaceAllString(string(data), "")
		return output
	}
}

func readheaderReferers() string {
	{
		data, err := ioutil.ReadFile("../headersReferers.txt")
		if err != nil {
			fmt.Println("Can't read file")
			panic(err)
		}
		var re = regexp.MustCompile(`\r?\n`)
		var output = re.ReplaceAllString(string(data), "")
		return output
	}
}
