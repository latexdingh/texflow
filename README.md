# texflow

> Watch LaTeX source files and hot-reload PDF output with smart error parsing and inline diff previews.

---

## Installation

```bash
pip install texflow
```

Or install from source:

```bash
git clone https://github.com/yourname/texflow.git && cd texflow && pip install -e .
```

---

## Usage

Start watching a `.tex` file and automatically recompile on save:

```bash
texflow watch main.tex
```

Specify a custom output directory and PDF viewer:

```bash
texflow watch main.tex --out ./build --viewer zathura
```

On each save, **texflow** will:
- Recompile the LaTeX source using `pdflatex` (or `xelatex`, configurable)
- Parse compiler errors and display them with file, line, and context
- Show an inline diff preview of what changed between the last two builds

### Options

| Flag | Description |
|------|-------------|
| `--compiler` | LaTeX compiler to use (default: `pdflatex`) |
| `--out` | Output directory for build artifacts |
| `--viewer` | PDF viewer to auto-reload (e.g. `zathura`, `evince`) |
| `--no-diff` | Disable inline diff previews |

---

## Requirements

- Python 3.8+
- A LaTeX distribution (e.g. [TeX Live](https://tug.org/texlive/), [MiKTeX](https://miktex.org/))

---

## License

MIT © 2024 — see [LICENSE](LICENSE) for details.