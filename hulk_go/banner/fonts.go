package banner

import (
	"fmt"
	"io/ioutil"
	"regexp"
	"strconv"
	"strings"
)

var deutsch = []rune{196, 214, 220, 228, 246, 252, 223}

type fontHeader struct {
	hardblank  rune
	charheight int
	baseline   int
	maxlen     int
	smush      int
	cmtlines   int
	right2left bool
	smush2     int
}

func readHeader(header string) (fontHeader, error) {
	h := fontHeader{}

	magic_num := "flf2a"
	if !strings.HasPrefix(header, magic_num) {
		return h, fmt.Errorf("invalid font header: %v", header)
	}

	trimmedHeader := strings.TrimSpace(header[len(magic_num):])
	headerParts := strings.Split(trimmedHeader, " ")
	h.hardblank = []rune(headerParts[0])[0]

	nums := make([]int, len(headerParts)-1)
	for i, s := range headerParts[1:] {
		num, err := strconv.ParseInt(s, 10, 32)
		if err != nil {
			return h, fmt.Errorf("invalid font header: %v: %v", header, err)
		}
		nums[i] = int(num)
	}

	h.charheight = nums[0]
	h.baseline = nums[1]
	h.maxlen = nums[2]
	h.smush = nums[3]
	h.cmtlines = nums[4]

	// these are optional for backwards compatibility
	if len(nums) > 5 {
		h.right2left = nums[5] != 0
	}
	if len(nums) > 6 {
		h.smush2 = nums[6]
	}

	// if no smush2, decode smush into smush2
	if len(nums) < 7 {
		if h.smush == 0 {
			h.smush2 = SMKern
		} else if h.smush < 0 {
			h.smush2 = 0
		} else {
			h.smush2 = (h.smush & 31) | SMSmush
		}
	}

	return h, nil
}

func readFontChar(lines []string, currline int, height int) [][]rune {
	char := make([][]rune, height)
	for row := 0; row < height; row++ {
		line := lines[currline+row]

		k := len(line) - 1

		// remove any trailing whitespace after end char
		ws := regexp.MustCompile(`\s`)
		for k > 0 && ws.MatchString(line[k:k+1]) {
			k--
		}

		if k > 0 {
			// remove end marks
			endchar := line[k]
			for k > 0 && line[k] == endchar {
				k--
			}
		}

		char[row] = []rune(line[:k+1])
	}

	return char
}

type Font struct {
	header  fontHeader
	comment string
	chars   map[rune][][]rune
}

func (f *Font) Settings() Settings {
	return Settings{
		smushmode: f.header.smush2,
		hardblank: f.header.hardblank,
		rtol:      f.header.right2left,
	}
}

func ReadFont(filename string) (*Font, error) {
	bytes, err := ioutil.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	return ReadFontFromBytes(bytes)
}

func ReadFontFromBytes(bytes []byte) (*Font, error) {
	lines := strings.Split(string(bytes), "\n")

	header, err := readHeader(lines[0])
	if err != nil {
		return nil, err
	}

	f := Font{
		header:  header,
		comment: strings.Join(lines[1:header.cmtlines+1], "\n"),
		chars:   make(map[rune][][]rune),
	}

	charheight := int(f.header.charheight)
	currline := int(f.header.cmtlines) + 1

	// allocate 0, the 'missing' character
	f.chars[0] = make([][]rune, charheight)

	// standard ASCII characters
	for ord := ' '; ord <= '~'; ord++ {
		f.chars[ord] = readFontChar(lines, currline, charheight)
		currline += charheight
	}

	// 7 german characters
	for i := 0; i < 7; i++ {
		f.chars[deutsch[i]] = readFontChar(lines, currline, charheight)
		currline += charheight
	}

	// code-tagged characters
	for currline < len(lines) {
		var code int
		_, err := fmt.Sscan(lines[currline], &code)
		if err != nil {
			break
		}

		currline++
		f.chars[rune(code)] = readFontChar(lines, currline, charheight)

		currline += charheight
	}

	return &f, nil
}
