package banner

import (
	"fmt"
	"io"
	"os"
	"strings"
)

func FPrintLines(w io.Writer, lines []FigText, hardblank rune, maxwidth int, align string) {
	padleft := func(linelen int) {
		switch align {
		case "right":
			fmt.Fprint(w, strings.Repeat(" ", maxwidth-linelen))
		case "center":
			fmt.Fprint(w, strings.Repeat(" ", (maxwidth-linelen)/2))
		}
	}

	for _, line := range lines {
		for _, subline := range line.Art() {
			padleft(len(subline))
			for _, outchar := range subline {
				if outchar == hardblank {
					outchar = ' '
				}
				fmt.Fprintf(w, "%c", outchar)
			}
			if len(subline) < maxwidth && align != "right" {
				fmt.Fprintln(w)
			}
		}
	}
}

func FPrintMsg(w io.Writer, msg string, f *Font, maxwidth int, s Settings, align string) {
	lines := GetLines(msg, f, maxwidth, s)
	FPrintLines(w, lines, s.HardBlank(), maxwidth, align)
}

func PrintMsg(msg string, f *Font, maxwidth int, s Settings, align string) {
	FPrintMsg(os.Stdout, msg, f, maxwidth, s, align)
}
