# Release checklist

Jazzband guidelines: https://jazzband.co/about/releases

* [ ] Get master to the appropriate code release state.
      [Travis CI](https://travis-ci.org/jazzband/tablib)
      should pass on master.
      [![Build Status](https://travis-ci.org/jazzband/tablib.svg?branch=master)](https://travis-ci.org/jazzband/tablib)

* [ ] Check [HISTORY.md](https://github.com/jazzband/tablib/blob/master/HISTORY.md),
      update version number and release date

* [ ] Tag with version number and push tag, for example:
```bash
git tag -a v0.14.0 -m v0.14.0
git push --tags
```

* [ ] Once Travis CI has built and uploaded distributions, check files at
      [Jazzband](https://jazzband.co/projects/tablib) and release to
      [PyPI](https://pypi.org/pypi/tablib)

* [ ] Check installation:
```bash
pip uninstall -y tablib && pip install -U tablib
```

* [ ] Create new GitHub release: https://github.com/jazzband/tablib/releases/new
  * Tag: Pick existing tag "v0.14.0"
