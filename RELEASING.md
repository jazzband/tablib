# Release checklist

Jazzband guidelines: https://jazzband.co/about/releases

* [ ] Get `master` to the appropriate code release state.
      [GitHub Actions](https://github.com/jazzband/tablib/actions)
      should pass on `master`.
      [![GitHub Actions status](https://github.com/jazzband/tablib/workflows/Test/badge.svg)](https://github.com/jazzband/tablib/actions)

* [ ] Edit release draft, adjust text if needed:
      https://github.com/hugovk/em-keyboard/releases

* [ ] Check next tag is correct, amend if needed

* [ ] Publish release

* [ ] Once GitHub Actions has built and uploaded distributions, check files at
      [Jazzband](https://jazzband.co/projects/tablib) and release to
      [PyPI](https://pypi.org/pypi/tablib)

* [ ] Check installation:
```bash
pip uninstall -y tablib && pip install -U tablib
```
