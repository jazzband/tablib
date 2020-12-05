# Release checklist

Jazzband guidelines: https://jazzband.co/about/releases

* [ ] Get master to the appropriate code release state.
      [GitHub Actions](https://github.com/jazzband/tablib/actions)
      should pass on master.
      [![GitHub Actions status](https://github.com/jazzband/tablib/workflows/Test/badge.svg)](https://github.com/jazzband/tablib/actions)

* [ ] Check [HISTORY.md](https://github.com/jazzband/tablib/blob/master/HISTORY.md),
      update version number and release date

* [ ] Tag with version number and push tag, for example:
```bash
git tag -a v3.1.0 -m v3.1.0
git push --tags
```

* [ ] Create new GitHub release: https://github.com/jazzband/tablib/releases/new
  * Tag: Pick existing tag "v3.1.0"

* [ ] Once GitHub Actions has built and uploaded distributions, check files at
      [Jazzband](https://jazzband.co/projects/tablib) and release to
      [PyPI](https://pypi.org/pypi/tablib)

* [ ] Check installation:
```bash
pip uninstall -y tablib && pip install -U tablib
```
