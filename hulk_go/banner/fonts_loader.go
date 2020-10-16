package banner

import (
	"errors"
	"go/build"
	"os"
	"path/filepath"
	"strings"
)

const (
	pkgName = "hulkbanner"
)

func GuessFontsDirectory() string {
	bin := os.Args[0]
	if !filepath.IsAbs(bin) {
		maybeBin, err := filepath.Abs(bin)
		if err == nil {
			bin = maybeBin
		}
	}

	// try <bindir>
	bindir := filepath.Dir(bin)
	dirsToTry := []string{
		filepath.Join(bindir, "hulkbanner", "fonts"),
		filepath.Join(bindir, "fonts"),
	}

	// try src directory
	ctx := build.Default
	if p, err := ctx.Import(pkgName, "", build.FindOnly); err == nil {
		dirsToTry = append(dirsToTry, filepath.Join(p.Dir, "hulkbanner", "fonts"))
		dirsToTry = append(dirsToTry, filepath.Join(p.Dir, "fonts"))
	}

	for _, fontsDir := range dirsToTry {
		fontsGlob := filepath.Join(fontsDir, "*.flf")
		matches, err := filepath.Glob(fontsGlob)
		if err == nil && len(matches) > 0 {
			return fontsDir
		}
	}

	return ""
}

func FontNamesInDir(dir string) ([]string, error) {
	glob := filepath.Join(dir, "*.flf")
	matches, err := filepath.Glob(glob)
	if err != nil {
		return nil, err
	}

	fontNames := make([]string, 0)
	for _, filename := range matches {
		base := filepath.Base(filename)
		fontNames = append(fontNames, strings.TrimSuffix(base, ".flf"))
	}

	return fontNames, nil
}

func GetFontByName(dirname, name string) (*Font, error) {
	if dirname == "" {
		dirname := GuessFontsDirectory()
		if dirname == "" {
			return nil, errors.New("Could not find fonts directory!")
		}
	}

	if !strings.HasSuffix(name, ".flf") {
		name += ".flf"
	}

	fontpath := filepath.Join(dirname, name)

	return ReadFont(fontpath)
}
