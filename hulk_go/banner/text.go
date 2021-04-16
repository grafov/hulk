package banner

type FigText struct {
	art  [][]rune
	text string
}

func newFigText(height int) *FigText {
	return &FigText{art: make([][]rune, height)}
}

func (ft *FigText) width() int {
	return len(ft.art[0])
}

func (ft *FigText) height() int {
	return len(ft.art)
}

func (ft *FigText) String() string {
	str := ""
	for _, line := range ft.art {
		str += string(line) + "\n"
	}
	return str
}

func (ft *FigText) Art() [][]rune {
	return ft.art
}

func (ft *FigText) copy() *FigText {
	copied := newFigText(ft.height())

	(*copied).text = (*ft).text
	for i := 0; i < ft.height(); i++ {
		width := ft.width()
		(*copied).art[i] = make([]rune, width)
		for j := 0; j < width; j++ {
			(*copied).art[i][j] = (*ft).art[i][j]
		}
	}

	return copied
}
