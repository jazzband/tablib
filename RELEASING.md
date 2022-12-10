# Release checklist

Jazzband guidelines: https://jazzband.co/about/releases

* [ ] Get master to the appropriate code release state.
      [GitHub Actions](https://github.com/jazzband/tablib/actions)
      should pass on master.
      [![GitHub Actions status](https://github.com/jazzband/tablib/workflows/Test/badge.svg)](https://github.com/jazzband/tablib/actions)

* [ ] Check [HISTORY.md](https://github.com/jazzband/tablib/blob/master/HISTORY.md),
      update version number and release date

* [ ] Create new GitHub release: https://github.com/jazzband/tablib/releases/new
  * Tag:
    * Click "Choose a tag"
    * Enter new tag: "v3.4.0"
    * Click "**Create new tag: v3.4.0** on publish"
  * Title: Leave blank, will be same as tag
  * Click "Generate release notes" and edit as required
  * Click "Publish release"

* [ ] Once GitHub Actions has built and uploaded distributions, check files at
      [Jazzband](https://jazzband.co/projects/tablib) and release to
      [PyPI](https://pypi.org/pypi/tablib)

* [ ] Check installation:
```bash
pip uninstall -y tablib && pip install -U tablib
```
