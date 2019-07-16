"""
loxun is a Python module to write large output in XML using Unicode and
namespaces. Of course you can also use it for small XML output with plain 8
bit strings and no namespaces.

loxun's features are:

* **small memory foot print**: the document is created on the fly by writing to
  an output stream, no need to keep all of it in memory.

* **easy to use namespaces**: simply add a namespace and refer to it using the
  standard ``namespace:tag`` syntax.

* **mix unicode and io.BytesIO**: pass both unicode or plain 8 bit strings to any
  of the methods. Internally loxun converts them to unicode, so once a
  parameter got accepted by the API you can rely on it not causing any
  messy ``UnicodeError`` trouble.

* **automatic escaping**: no need to manually handle special characters such
  as ``<`` or ``&`` when writing text and attribute values.

* **robustness**: while you write the document, sanity checks are performed on
  everything you do. Many silly mistakes immediately result in an
  ``XmlError``, for example missing end elements or references to undeclared
  namespaces.

* **open source**: distributed under the GNU Lesser General Public License 3
  or later.

Here is a very basic example. First you have to create an output stream. In
many cases this would be a file, but for the sake of simplicity we use a
``io.BytesIO`` here:

    >>> from __future__ import unicode_literals
    >>> import io
    >>> out = io.BytesIO()

Then you can create an `XmlWriter` to write to this output:

    >>> xml = XmlWriter(out)

Now write the content:

    >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml")
    >>> xml.startTag("xhtml:html")
    >>> xml.startTag("xhtml:body")
    >>> xml.text("Hello world!")
    >>> xml.tag("xhtml:img", {"src": "smile.png", "alt": ":-)"})
    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()

And the result is:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <xhtml:html xmlns:xhtml="http://www.w3.org/1999/xhtml">
      <xhtml:body>
        Hello world!
        <xhtml:img alt=":-)" src="smile.png" />
      </xhtml:body>
    </xhtml:html>

Writing a simple document
=========================

The following example creates a very simple XHTML document.

To make it simple, the output goes to a ``BytesIO``, but you could also use
a binary file that has been created using ``io.open(filename, "wb")``.

    >>> from __future__ import unicode_literals
    >>> import io
    >>> out = io.BytesIO()

First create an `XmlWriter` to write the XML code to the specified output:

    >>> xml = XmlWriter(out)

This automatically adds the XML prolog:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>

Next add the ``<html>`` start tag:

    >>> xml.startTag("html")

Now comes the <body>. To pass attributes, specify them in a dictionary.
So in order to add::

    <body id="top">

use:

    >>> xml.startTag("body", {"id": "top"})

Let' add a little text so there is something to look at:

    >>> xml.text("Hello world!")

Wrap it up: close all elements and the document.

    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()

And this is what we get:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <html>
      <body id="top">
        Hello world!
      </body>
    </html>

Specifying attributes

First create a writer:

    >>> import io
    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out)

Now write the content:

    >>> xml.tag("img", {"src": "smile.png", "alt": ":-)"})

Attribute values do not have to be strings, other types will be converted to
Unicode using Python's ``unicode()`` function:

    >>> xml.tag("img", {"src": "wink.png", "alt": ";-)", "width": 32, "height": 24})

And the result is:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <img alt=":-)" src="smile.png" />
    <img alt=";-)" height="24" src="wink.png" width="32" />

Using namespaces
================

Now the same thing but with a namespace. First create the prolog
and header like above:

    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out)

Next add the namespace:

    >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml")

Now elements can use qualified tag names using a colon (:) to separate
namespace and tag name:

    >>> xml.startTag("xhtml:html")
    >>> xml.startTag("xhtml:body")
    >>> xml.text("Hello world!")
    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()

As a result, tag names are now prefixed with "xhtml:":

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <xhtml:html xmlns:xhtml="http://www.w3.org/1999/xhtml">
      <xhtml:body>
        Hello world!
      </xhtml:body>
    </xhtml:html>

Working with non ASCII characters
=================================

Sometimes you want to use characters outside the ASCII range, for example
German Umlauts, the Euro symbol or Japanese Kanji. The easiest and performance
wise best way is to use Unicode strings. For example:

    >>> import io
    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out, prolog=False)
    >>> xml.text(u"The price is \\u20ac 100") # Unicode of Euro symbol
    >>> out.getvalue().rstrip("\\r\\n")
    'The price is \\xe2\\x82\\xac 100'

Notice the "u" before the string passed to `XmlWriter.text()`, it declares the
string to be a unicode string that can hold any character, even those that are
beyond the 8 bit range.

Also notice that in the output the Euro symbol looks very different from the
input. This is because the output encoding is UTF-8 (the default), which
has the advantage of keeping all ASCII characters the same and turning any
characters with a code of 128 or more into a sequence of 8 bit bytes that
can easily fit into an output stream to a binary file or ``io.BytesIO``.

If you have to stick to classic 8 bit string parameters, loxun attempts to
convert them to unicode. By default it assumes ASCII encoding, which does
not work out as soon as you use a character outside the ASCII range:

    >>> import io
    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out, prolog=False)
    >>> xml.text("The price is \\xa4 100") # ISO-8859-15 code of Euro symbol
    Traceback (most recent call last):
        ...
    UnicodeDecodeError: 'ascii' codec can't decode byte 0xa4 in position 13: ordinal not in range(128)

In this case you have to tell the writer the encoding you use by specifying
the the ``sourceEncoding``:

    >>> import io
    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out, prolog=False, sourceEncoding="iso-8859-15")

Now everything works out again:

    >>> xml.text("The price is \\xa4 100") # ISO-8859-15 code of Euro symbol
    >>> out.getvalue().rstrip("\\r\\n")
    'The price is \\xe2\\x82\\xac 100'

Of course in practice you will not mess around with hex codes to pass your
texts. Instead you just specify the source encoding using the mechanisms
described in PEP 263,
`Defining Python Source Code Encodings <http://www.python.org/dev/peps/pep-0263/>`_.

Pretty printing and indentation
===============================

By default, loxun starts a new line for each ``startTag`` and indents the
content with two spaces. You can change the spaces to any number of spaces and
tabs you like:

    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out, indent="    ") # <-- Indent with 4 spaces.
    >>> xml.startTag("html")
    >>> xml.startTag("body")
    >>> xml.text("Hello world!")
    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()
    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <html>
        <body>
            Hello world!
        </body>
    </html>

You can disable pretty printing all together using ``pretty=False``, resulting
in an output of a single large line:

    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out, pretty=False) # <-- Disable pretty printing.
    >>> xml.startTag("html")
    >>> xml.startTag("body")
    >>> xml.text("Hello world!")
    >>> xml.endTag()
    >>> xml.endTag()
    >>> xml.close()
    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?><html><body>Hello world!</body></html>

Changing the XML prolog
=======================

When you create a writer, it automatically write an XML prolog
processing instruction to the output. This is what the default prolog
looks like:

    >>> import io
    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out)
    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>

You can change the version or encoding:

    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out, encoding=u"ascii", version=u"1.1")
    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.1" encoding="ascii"?>

To completely omit the prolog, set the parameter ``prolog=False``:

    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out, prolog=False)
    >>> out.getvalue()
    ''

Adding other content
====================

Apart from text and tags, XML provides a few more things you can add to
documents. Here's an example that shows how to do it with loxun.

First, create a writer:

    >>> import io
    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out)

Let's add a document type definition:

    >>> xml.raw("<!DOCTYPE html PUBLIC \\"-//W3C//DTD XHTML 1.0 Strict//EN\\" SYSTEM \\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\\">")
    >>> xml.newline()

Notice that loxun uses the generic `XmlWriter.raw()` for that, which allows to
add any content without validation or escaping. You can do all sorts of nasty
things with ``raw()`` that will result in invalid XML, but this is one of its
reasonable uses.

Next, let's add a comment:

    >>> xml.comment("Show case some rarely used XML constructs")

Here is a processing instruction:

    >>> xml.processingInstruction("xml-stylesheet", "href=\\"default.css\\" type=\\"text/css\\"")

And finally a CDATA section:

    >>> xml.cdata(">> this will not be parsed <<")

And the result is:

    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <!-- Show case some rarely used XML constructs -->
    <?xml-stylesheet href="default.css" type="text/css"?>
    <![CDATA[>> this will not be parsed <<]]>


Optimization
============

Loxun automatically optimized pairs of empty start/end tags. For example:

    >>> out = io.BytesIO()
    >>> xml = XmlWriter(out)
    >>> xml.startTag("customers")
    >>> xml.startTag("person", {"id": "12345", "name": "Doe, John"})
    >>> xml.endTag("person") # without optimization, this would add </person>.
    >>> xml.endTag()
    >>> xml.close()
    >>> print out.getvalue().rstrip("\\r\\n")
    <?xml version="1.0" encoding="utf-8"?>
    <customers>
      <person id="12345" name="Doe, John" />
    </customers>

Despite the explicit ``startTag("person")`` and matching ``endtag()``, the
output only contains a simple ``<person ... />`` tag.

Contributing
------------

If you want to help improve loxun, you can access the source code at
<http://github.com/roskakori/loxun>.

Future
======

Currently loxun does what it was built for.

There are is no real plans to improve it in the near future, but here is a list
of features that might be added at some point:

* Add validation of tag and attribute names to ensure that all characters used
  are allowed. For instance, currently loxun does not complain about a tag
  named "a#b*c$d_".
* Raise an `XmlError` when namespaces are added with attributes instead of
  `XmlWriter.addNamespace()`.
* Logging support to simplify debugging of the calling code. Probably
  `XmlWriter` would get a property ``logger`` which is a standard
  ``logging.Logger``. By default it could log original exceptions that
  loxun turns into an `XmlError` and namespaces opened and closed.
  Changing it to ``logging.DEBUG`` would log each tag and XML construct
  written, including additional information about the internal tag stack.
  That way you could dynamically increase or decrease logging output.
* Rethink pretty printing. Instead of a global property that can only be set
  when initializing an `XmlWriter`, it could be a optional parameter for
  `XmlWriter.startTag()` where it could be turned on and off as needed. And
  the property could be named ``literal`` instead of ``pretty`` (with an
  inverse logic).
* Add a ``DomWriter`` that creates a ``xml.dom.minidom.Document``.

Some features other XML libraries support but I never saw any real use for:

* Specify attribute order for tags.

Version history
===============

Version 2.0, 2014-07-28

* Added support for Python 3.2+ while retaining the option to run with
  Python 2.6+ (issue #5; thanks go to `Stefan Schwarzer`_ who offered his
  guidance during a "Python 2 to 3" sprint at EuroPython 2014).
* Dropped support for Python 2.5, keep using loxun 1.3 if you are stuck
  with with this version.

.. _Stefan Schwarzer: http://www.sschwarzer.net

Version 1.3, 2012-01-01

* Added ``endTags()`` to close several or all open tags (issue #3,
  contributed by Anton Kolechkin).
* Added ``ChainXmlWriter`` which is similar to ``XmlWriter`` and allows to
  chain methods for more concise source code (issue #3, contributed by Anton
  Kolechkin).

Version 1.2, 2011-03-12

* Fixed ``AttributeError`` when ``XmlWriter(..., encoding=...)`` was set.

Version 1.1, 08-Jan-2011

* Fixed ``AssertionError`` when ``pretty`` was set to ``False``
  (issue #1; fixed by David Cramer).

Version 1.0, 11-Oct-2010

* Added support for Python's ``with`` so you don not have to manually call
  `XmlWriter.close()` anymore.
* Added Git repository at <http://github.com/roskakori/loxun>.

Version 0.8, 11-Jul-2010

* Added possibility to pass attributes to `XmlWriter.startTag()` and
  `XmlWriter.tag()` with values that have other types than ``str`` or
  ``unicode``. When written to XML, the value is converted using Python's
  built-in ``unicode()`` function.
* Added a couple of files missing from the distribution, most important the
  test suite.

Version 0.7, 03-Jul-2010

* Added optimization of matching start and end tag without any content in
  between. For example, ``x.startTag("some"); x.endTag()`` results in
  ``<some />`` instead of ``<some></some>``.
* Fixed handling of unknown name spaces. They now raise an `XmlError` instead
   of ``ValueError``.

Version 0.6, 03-Jun-2010

* Added option ``indent`` to specify the indentation text each new line starts with.
* Added option ``newline`` to specify how lines written should end.
* Fixed that `XmlWriter.tag()` did not remove namespaces declared immediately
  before it.
* Cleaned up documentation.

Version 0.5, 25-May-2010

* Fixed typo in namespace attribute name.
* Fixed adding of namespaces before calls to `XmlWriter.tag()` which resulted
  in an `XmlError`.

Version 0.4, 21-May-2010

* Added option ``sourceEncoding`` to simplify processing of classic strings.
  The manual section "Working with non ASCII characters" explains how to use
  it.

Version 0.3, 17-May-2010

* Added scoped namespaces which are removed automatically by
  `XmlWriter.endTag()`.
* Changed ``text()`` to normalize newlines and white space if pretty printing
  is enabled.
* Moved writing of XML prolog to the constructor and removed
  ``XmlWriter.prolog()``. To omit the prolog, specify ``prolog=False`` when
  creating the `XmlWriter`. If you later want to write the prolog yourself,
  use `XmlWriter.processingInstruction()`.
* Renamed ``*Element()`` to ``*Tag`` because they really only write tags, not
  whole elements.

Version 0.2, 16-May-2010

* Added `XmlWriter.comment()`, `XmlWriter.cdata()` and
  `XmlWriter.processingInstruction()` to write these specific XML constructs.
* Added indentation and automatic newline to text if pretty printing is
  enabled.
* Removed newline from prolog in case pretty printing is disabled.
* Fixed missing "?" in prolog.

Version 0.1, 15-May-2010

* Initial release.
"""
# Copyright (C) 2010-2012 Thomas Aglassinger
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals

import collections
import io
import os
import re
import sys
import xml.sax.saxutils

__version__ = "2.0"


# Compatibility helpers for Python 2 and 3.
if sys.version_info[0] == 2:
    bytes_type = str
    unicode_type = unicode
else:
    bytes_type = bytes
    unicode_type = str


class XmlError(Exception):
    """
    Error raised when XML can not be generated.
    """
    pass

def _quoted(value):
    _assertIsUnicode("value", value)
    return xml.sax.saxutils.quoteattr(value)

def _validateNotEmpty(name, value):
    """
    Validate that ``value`` is not empty and raise `XmlError` in case it is.
    """
    assert name
    if not value:
        raise XmlError("%s must not be empty" % name)

def _validateNotNone(name, value):
    """
    Validate that ``value`` is not ``None`` and raise `XmlError` in case it is.
    """
    assert name
    if value is None:
        raise XmlError("%s must not be %r" % (name, None))

def _validateNotNoneOrEmpty(name, value):
    """
    Validate that ``value`` is not empty or ``None`` and raise `XmlError` in case it is.
    """
    _validateNotNone(name, value)
    _validateNotEmpty(name, value)

def _assertIsUnicode(name, value):
    assert (value is None) or isinstance(value, unicode_type), \
        "value for %r must be of type %s but is: %r" % (name, unicode_type.__name__, value)

def _splitPossiblyQualifiedName(name, value):
    """
    A pair ``(namespace, name)`` derived from ``name``.

    A fully qualified name:

        >>> _splitPossiblyQualifiedName(u"tag name", u"xhtml:img")
        (u'xhtml', u'img')

    A name in the default namespace:

        >>> _splitPossiblyQualifiedName(u"tag name", u"img")
        (None, u'img')

    Improper names result in an `XmlError`:

        >>> _splitPossiblyQualifiedName(u"x", u"")
        Traceback (most recent call last):
        ...
        XmlError: x must not be empty
    """
    assert name
    _assertIsUnicode("name", name)
    _assertIsUnicode("value", value)

    colonIndex = value.find(":")
    if colonIndex == -1:
        _validateNotEmpty(name, value)
        result = (None, value)
    else:
        namespacePart = value[:colonIndex]
        _validateNotEmpty("namespace part of %s", namespacePart)
        namePart = value[colonIndex+1:]
        _validateNotEmpty("name part of %s", namePart)
        result = (namespacePart, namePart)
    # TODO: validate that all parts are NCNAMEs.
    return result

def _joinPossiblyQualifiedName(namespace, name):
    _assertIsUnicode("namespace", namespace)
    assert name
    _assertIsUnicode("name", name)
    if namespace:
        result = "%s:%s" % (namespace, name)
    else:
        result = name
    return result

class XmlWriter(object):
    """
    Writer for large output in XML optionally supporting Unicode and
    namespaces.
    """
    # Marks to start/end CDATA.
    _CDATA_START = "<![CDATA["
    _CDATA_END = "]]>"

    # Marks to start/end processing instruction.
    _PROCESSING_START = "<?"
    _PROCESSING_END = "?>"

    # Possible value for _possiblyWriteTag()'s ``close`` parameter.
    _CLOSE_NONE = "none"
    _CLOSE_AT_START = "start"
    _CLOSE_AT_END = "end"

    # Build regular expressions to validate tag and attribute names.
    _NAME_START_CHARS = "_a-zA-Z\u00c0-\u00d6\u00d8-\u00f6\00f8-\u02ff\u0370-\u037d\u037f-\u1fff\u200c-\u200d\u2070-\u218f\u2c00-\u2fef\u3001-\ud7ff\uf900-\ufdcf\ufdf0-\ufffd"
    _NAME_CHARS = "\\-\\.0-9" + _NAME_START_CHARS + "\\u00b7\\u0300-\\u036f\\u203f-\\u2040"
    _NAME_START_CHAR_PATTERN = "[" + _NAME_START_CHARS + "]"
    _NAME_CHAR_PATTERN = "[" + _NAME_CHARS + "]"
    _nameStartCharRegEx = re.compile(_NAME_START_CHAR_PATTERN, re.UNICODE)
    _nameCharRegEx = re.compile(_NAME_START_CHAR_PATTERN, re.UNICODE)

    def __init__(self, output, pretty=True, indent="  ", newline=os.linesep, encoding="utf-8", errors="strict", prolog=True, version="1.0", sourceEncoding="ascii"):
        """
        Initialize ``XmlWriter`` writing to ``output``.

        The ``output`` can be anything that has a ``write(data)`` method,
        typically a filelike object. The writer accesses the ``output`` as
        stream, so it does not have to support any methods for random
        access like ``seek()``.

        In case you write to a file, use ``"wb"`` as ``mode`` for ``open()``
        to prevent messed up newlines.

        Set ``pretty`` to ``False`` if you do not want to the writer to pretty
        print. Keep in mind though that this results in the whole output being
        a single line unless you use `newline()` or write text with newline
        characters in it.

        Set ``indent`` to the string that should be used for each indentation
        level.

        Set ``newline`` to the string that should be used at the end of each
        line.

        Set ``encoding`` to the name of the preferred output encoding.

        Set ``errors`` to one of the value possible value for
        ``unicode(..., error=...)`` if you do not want the output to fail with
        a `UnicodeError` in case a character cannot be encoded.

        Set ``prolog`` to ``False`` if you do not want the writer to emit an
        XML prolog processing instruction (like
        ``<?xml version="1.0" encoding="utf-8"?>``).

        Set ``version`` to the value the version attribute in the XML prolog
        should have.

        Set ``sourceEncoding`` to the name of the encoding that plain 8 bit
        strings passed as parameters use.
        """
        assert output is not None
        assert encoding
        assert errors
        assert sourceEncoding
        _validateNotNoneOrEmpty("version", version)
        self._output = output
        self._pretty = pretty
        self._sourceEncoding = sourceEncoding
        self._encoding = self._unicodedFromString(encoding)
        self._errors = self._unicodedFromString(errors)
        self._namespaces = {}
        self._elementStack = collections.deque()
        self._namespacesToAdd = collections.deque()
        self._isOpen = True
        self._contentHasBeenWritten = False
        self._indent = self._unicodedFromString(indent)

        # `None` or a tuple of (indent, qualifiedTagName, attributes).
        # See also: `_possiblyWriteTag()`.
        self._startTagToWrite = None

        indentWithoutWhiteSpace = self._indent.replace(" ", "").replace("\t", "")
        assert not indentWithoutWhiteSpace, \
            "`indent` must contain only blanks or tabs but also has: %r" % indentWithoutWhiteSpace
        self._newline = self._unicodedFromString(newline)
        _VALID_NEWLINES = ["\r", "\n", "\r\n"]
        assert self._newline in _VALID_NEWLINES, \
            "`newline` is %r but must be one of: %s" % (self._newline, _VALID_NEWLINES)
        if prolog:
            self.processingInstruction("xml", "version=%s encoding=%s" % ( \
                _quoted(self._unicodedFromString(version)),
                _quoted(self._encoding))
            )

    def __enter__(self):
        return self

    def __exit__(self, errorType, error, traceback):
        if not error:
            # There's no point in calling `close()` in case of previous errors
            # because it most likely will cause another error and thus discard
            # the original error which holds actually useful information.
            #
            # Not calling `close()` will *not* introduce any resource leaks.
            self.close()

    @property
    def isPretty(self):
        """Pretty print writes to the ``output``?"""
        return self._pretty

    @property
    def encoding(self):
        """The encoding used when writing to the ``output``."""
        return self._encoding

    @property
    def output(self):
        """The stream where the output goes."""
        return self._output

    def _scope(self):
        return len(self._elementStack)

    def _encoded(self, text):
        assert text is not None
        _assertIsUnicode("text", text)
        return text.encode(self._encoding, self._errors)

    def _unicodedFromString(self, text):
        """
        Same value as ``text`` but converted to unicode in case ``text`` is a
        string. ``None`` remains ``None``.
        """
        if text is None:
            result = None
        elif isinstance(text, unicode_type):
            result = text
        else:
            result = unicode_type(text, self._sourceEncoding)
        return result

    def _raiseStrOrUnicodeBroken(self, method, value, error):
        """
        Raise `XmlError` pointing out the ``__str__()`` or ``__unicode__`` of
        of the type of ``value`` must be implemented properly.
        """
        assert method in ("str", "unicode")
        assert error is not None

        someTypeName = type(value).__name__
        message = "%s.__%s()__ must return a value of type %s or %s but failed for value %r with: %s" % (
            someTypeName, method, unicode_type.__name__, bytes_type.__name__, value, error
        )
        raise XmlError(message)

    def _unicoded(self, some):
        """
        Same value as ``some`` but converted to unicode in case ``some`` is
        not already a unicode string. ``None`` remains ``None``.

        Examples:

        >>> import io
        >>> out = io.BytesIO()
        >>> xml = XmlWriter(out)
        >>> xml._unicoded(u"abc")
        u'abc'
        >>> xml._unicoded("abc")
        u'abc'
        >>> xml._unicoded(123)
        u'123'

        >>> import decimal
        >>> xml._unicoded(decimal.Decimal("123.45"))
        u'123.45'

        In order for this to work, the type of ``some`` must have a proper
        implementation of ``__unicode()__`` or ``__str__``.

        Here is an example for a class with a broken ``__unicode__``, which
        already fails if ``unicode()`` is called without loxun:

        >>> class Broken(object):
        ...   def __unicode__(self):
        ...     return 123 # BROKEN: Return type must be str or unicode
        >>> unicode(Broken())
        Traceback (most recent call last):
        ...
        TypeError: coercing to Unicode: need string or buffer, int found

        Consequently, using a value of ``Broken`` as attribute value will fail too:

        >>> xml.tag("someTag", {"someAttribute": Broken()}) #doctest: +ELLIPSIS
        Traceback (most recent call last):
        ...
        XmlError: Broken.__unicode()__ must return a value of type str or unicode but failed for value ... with: coercing to Unicode: need string or buffer, int found
        """
        if some is None:
            result = None
        elif isinstance(some, unicode_type):
            result = some
        else:
            if isinstance(some, bytes_type):
                result = some
            else:
                try:
                    result = unicode_type(some)
                except Exception as error:
                    self._raiseStrOrUnicodeBroken("unicode", some, error)
            # Ensure that the caller implemented __str__ / __unicode__ properly.
            if not isinstance(result, unicode_type):
                try:
                    result = unicode_type(some, self._sourceEncoding)
                except Exception as error:
                    self._raiseStrOrUnicodeBroken("unicode", some, error)
        return result

    def _isNameStartChar(self, some):
        """
        NameStartChar ::= ":" | [A-Z] | "_" | [a-z] | [#xC0-#xD6] | [#xD8-#xF6]
        | [#xF8-#x2FF] | [#x370-#x37D] | [#x37F-#x1FFF] | [#x200C-#x200D]
        | [#x2070-#x218F] | [#x2C00-#x2FEF] | [#x3001-#xD7FF]
        | [#xF900-#xFDCF] | [#xFDF0-#xFFFD] | [#x10000-#xEFFFF]
        """
        assert some
        return True

    def _isNameChar(self, some):
        """
        NameChar ::= NameStartChar | "-" | "." | [0-9] | #xB7
        | [#x0300-#x036F] | [#x203F-#x2040]
        """
        assert some
        return True

    def _elementName(self, name, namespace):
        assert name
        if namespace:
            result = "%s:%s" % (namespace, name)
        else:
            result = name
        return result

    def _validateIsOpen(self):
        if not self._isOpen:
            raise XmlError("operation must be performed before writer is closed")

    def _validateNamespaceItem(self, itemName, namespace, qualifiedName):
        if namespace:
            namespaceFound = False
            scopeIndex = self._scope()
            while not namespaceFound and (scopeIndex >= 0):
                namespacesForScope = self._namespaces.get(scopeIndex)
                if namespacesForScope:
                    if namespace in [namespaceToCompareWith for namespaceToCompareWith, _ in namespacesForScope]:
                        namespaceFound = True
                scopeIndex -= 1
            if not namespaceFound:
                if namespace == "xmlns":
                    # TODO: raise XmlError("namespace '%s' must be added using `addNamespace()`.")
                    pass
                else:
                    raise XmlError("namespace '%s' for %s '%s' must be added before use" % (namespace, itemName, qualifiedName))

    def _write(self, text):
        assert text is not None
        _assertIsUnicode("text", text)
        self._output.write(self._encoded(text))
        if not self._contentHasBeenWritten and text:
            self._contentHasBeenWritten = True

    def _writeIndent(self):
        self._write(self._indent * len(self._elementStack))

    def _writePrettyIndent(self):
        if self._pretty:
            self._writeIndent()

    def _writePrettyNewline(self):
        if self._pretty:
            self.newline()

    def _writeEscaped(self, text):
        assert text is not None
        _assertIsUnicode("text", text)
        self._write(xml.sax.saxutils.escape(text))

    def newline(self):
        self._possiblyFlushTag()
        self._write(self._newline)

    def addNamespace(self, name, uri):
        """
        Add namespace to the following elements by adding a ``xmlns``
        attribute to the next tag that is written using `startTag()` or `tag()`.
        """
        # TODO: Validate that name is NCName.
        _validateNotNoneOrEmpty("name", name)
        _validateNotNoneOrEmpty("uri", uri)
        uniName = self._unicodedFromString(name)
        uniUri = self._unicodedFromString(uri)
        namespacesForScope = self._namespaces.get(self._scope())
        namespaceExists = (uniName in self._namespacesToAdd) or (
            (namespacesForScope != None) and (uniName in namespacesForScope)
        )
        if namespaceExists:
            raise XmlError("namespace %r must added only once for current scope but already is %r" % (uniName, uniUri))
        self._namespacesToAdd.append((uniName, uniUri))

    def _possiblyWriteTag(self, namespace, name, close, attributes={}):
        _assertIsUnicode("namespace", namespace)
        assert name
        _assertIsUnicode("name", name)
        assert close
        assert close in (XmlWriter._CLOSE_NONE, XmlWriter._CLOSE_AT_START, XmlWriter._CLOSE_AT_END)
        assert attributes is not None

        actualAttributes = {}

        # TODO: Validate that no "xmlns" attributes are specified by hand.

        # Process new namespaces to add.
        if close in [XmlWriter._CLOSE_NONE, XmlWriter._CLOSE_AT_END]:
            while self._namespacesToAdd:
                namespaceName, uri = self._namespacesToAdd.pop()
                if namespaceName:
                    actualAttributes["xmlns:%s" % namespaceName] = uri
                else:
                    actualAttributes["xmlns"] = uri
                namespacesForScope = self._namespaces.get(self._scope())
                if namespacesForScope == None:
                    namespacesForScope = []
                    self._namespaces[self._scope()] = namespacesForScope
                assert namespaceName not in [existingName for existingName, _ in namespacesForScope]
                namespacesForScope.append((namespaceName, uri))
                self._namespaces[namespaceName] = uri
        else:
            if self._namespacesToAdd:
                namespaceNames = ", ".join([name for name, _ in self._namespacesToAdd])
                raise XmlError("namespaces must be added before startTag() or tag(): %s" % namespaceNames)

        # Convert attributes to unicode.
        for qualifiedAttributeName, attributeValue in list(attributes.items()):
            uniQualifiedAttributeName = self._unicodedFromString(qualifiedAttributeName)
            attributeNamespace, attributeName = _splitPossiblyQualifiedName("attribute name", uniQualifiedAttributeName)
            self._validateNamespaceItem("attribute", attributeNamespace, attributeName)
            actualAttributes[uniQualifiedAttributeName] = self._unicoded(attributeValue)

        # Prepare indentation and qualified tag name to be written.
        if self.isPretty:
            indent = self._indent * len(self._elementStack)
        else:
            indent = ""
        self._validateNamespaceItem("tag", namespace, name)
        if namespace:
            qualifiedTagName = "%s:%s" % (namespace, name)
        else:
            qualifiedTagName = name

        if close == XmlWriter._CLOSE_NONE:
            self._startTagToWrite = (indent, qualifiedTagName, actualAttributes)
        else:
            self._actuallyWriteTag(indent, qualifiedTagName, actualAttributes, close)

        # Process name spaces to remove
        if close in [XmlWriter._CLOSE_AT_END, XmlWriter._CLOSE_AT_START]:
            scopeToRemove = self._scope()
            if scopeToRemove in self._namespaces:
                del self._namespaces[scopeToRemove]

    def _actuallyWriteTag(self, indent, qualifiedTagName, attributes, close):
        assert self._startTagToWrite is None
        assert indent is not None
        _assertIsUnicode("indent", indent)
        assert qualifiedTagName
        _assertIsUnicode("qualifiedTagName", qualifiedTagName)
        assert close
        assert close in (XmlWriter._CLOSE_NONE, XmlWriter._CLOSE_AT_START, XmlWriter._CLOSE_AT_END)
        assert attributes is not None
        if self._pretty:
            self._write(indent)
        self._write("<")
        if close == XmlWriter._CLOSE_AT_START:
            self._write("/")
        self._write(qualifiedTagName)
        for attributeName in sorted(attributes.keys()):
            _assertIsUnicode("attribute name", attributeName)
            value = attributes[attributeName]
            _assertIsUnicode("value of attribute %r" % attributeName, value)
            self._write(" %s=%s" % (attributeName, _quoted(value)))
        if close == XmlWriter._CLOSE_AT_END:
            if self.isPretty:
                self._write(" ")
            self._write("/")
        self._write(">")
        if self._pretty:
            self.newline()

    def _possiblyFlushTag(self):
        """
        If ``self._startTagToWrite`` is set, it contains a tuple
        ``(indent, qualifiedTagName, attributes)`` describing a start tag that has not
        been written yet. In this case, write the tag now and set
        ``self._startTagToWrite`` to ``None``. This allows to optimize a sequence
        of ``startTag()``/ ``endTag()`` with the same tag to be changed to
        a simple ``tag()``.
        """
        if self._startTagToWrite:
            indent, qualifiedTagName, attributes = self._startTagToWrite;
            self._startTagToWrite = None
            self._actuallyWriteTag(indent, qualifiedTagName, attributes, XmlWriter._CLOSE_NONE)

    def startTag(self, qualifiedName, attributes={}):
        """
        Start tag with name ``qualifiedName``, optionally using a namespace
        prefix separated with a colon (:) and ``attributes``.

        Example names are "img" and "xhtml:img" (assuming the namespace prefix
        "xtml" has been added before using `addNamespace()`).

        Attributes are a dictionary containing the attribute name and value, for
        example::

            {"src": "../some.png", "xhtml:alt": "some image"}
        """
        self._possiblyFlushTag()
        uniQualifiedName = self._unicodedFromString(qualifiedName)
        namespace, name = _splitPossiblyQualifiedName("tag name", uniQualifiedName)
        self._possiblyWriteTag(namespace, name, XmlWriter._CLOSE_NONE, attributes)
        self._elementStack.append((namespace, name))

    def endTag(self, expectedQualifiedName=None):
        """
        End tag that has been started before using `startTag()`,
        optionally checking that the name matches ``expectedQualifiedName``.

        As example, consider the following writer with a namespace:

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out)
            >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml")

        Now start a couple of elements:

            >>> xml.startTag("html")
            >>> xml.startTag("xhtml:body")

        Try to end a mistyped tag:

            >>> xml.endTag("xhtml:doby")
            Traceback (most recent call last):
                ...
            XmlError: tag name must be xhtml:doby but is xhtml:body

        Try again properly:

            >>> xml.endTag("xhtml:body")

        Try to end another mistyped tag, this time without namespace:

            >>> xml.endTag("xml")
            Traceback (most recent call last):
                ...
            XmlError: tag name must be xml but is html

        End the tag properly, this time without an expected name:

            >>> xml.endTag()

        Try to end another tag without any left:

            >>> xml.endTag()
            Traceback (most recent call last):
                ...
            XmlError: tag stack must not be empty
        """
        try:
            (namespace, name) = self._elementStack.pop()
        except IndexError:
            raise XmlError("tag stack must not be empty")
        actualQualifiedName = _joinPossiblyQualifiedName(namespace, name)
        if expectedQualifiedName:
            # Validate that actual tag name matches expected name.
            uniExpectedQualifiedName = self._unicodedFromString(expectedQualifiedName)
            if actualQualifiedName != expectedQualifiedName:
                self._elementStack.append((namespace, name))
                raise XmlError("tag name must be %s but is %s" % (uniExpectedQualifiedName, actualQualifiedName))

        isConsolidatableStartEndTag = False
        if self._startTagToWrite:
            _, qualifiedStartTagName, attributes = self._startTagToWrite
            if actualQualifiedName == qualifiedStartTagName:
                isConsolidatableStartEndTag = True
        if isConsolidatableStartEndTag:
            self._startTagToWrite = None
            self._possiblyWriteTag(namespace, name, XmlWriter._CLOSE_AT_END, attributes)
        else:
            self._possiblyFlushTag()
            self._possiblyWriteTag(namespace, name, XmlWriter._CLOSE_AT_START)


    def endTags(self, count=0):
        """
        End tags is useful if you need to close a couple of tags in one command
        it might be useful when you need to close a few root tags.

        As example, consider the following writer with a namespace:

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out)
            >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml")

        Now start a couple of elements:

            >>> xml.startTag("html")
            >>> xml.startTag("xhtml:body")
            >>> xml.startTag("xhtml:div")
            >>> xml.startTag("xhtml:span")
            >>> xml.startTag("xhtml:b")

        Try to end bad number of tags:

            >>> xml.endTags(7) # actually there are 5 tags, not 7
            Traceback (most recent call last):
                ...
            XmlError: cannot close 7 tags, 5 remaining

        Try to end 2 tags:

            >>> xml.endTags(2)

        And now finally end all started tags:

            >>> xml.endTags()

        But if all the tags closed it will raise the same error as endTag

            >>> xml.endTags()
            Traceback (most recent call last):
                ...
            XmlError: tag stack must not be empty
        """

        stackLen = int(len(self._elementStack))

        if stackLen == 0:
            raise XmlError("tag stack must not be empty")
        if count == 0:
            count = stackLen
        elif stackLen < count:
            raise XmlError("cannot close %d tags,"
                           " %d remaining" % (count, stackLen))

        for _ in range(count):
            self.endTag()

    def tag(self, qualifiedName, attributes={}):
        self._possiblyFlushTag()
        uniQualifiedName = self._unicodedFromString(qualifiedName)
        namespace, name = _splitPossiblyQualifiedName("tag name", uniQualifiedName)
        self._possiblyWriteTag(namespace, name, XmlWriter._CLOSE_AT_END, attributes)

    def text(self, text):
        """
        Write ``text`` using escape sequences if needed.

        Using a writer like

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)

        you can write some text:

            >>> xml.text("<this> & <that>")
            >>> print out.getvalue().rstrip("\\r\\n")
            &lt;this&gt; &amp; &lt;that&gt;

        If ``text`` contains line feeds, the will be normalized to `newline()`:

            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)
            >>> xml.startTag("some")
            >>> xml.text("a text\\nwith multiple lines\\n    and indentation and trailing blanks   ")
            >>> xml.endTag()
            >>> print out.getvalue().rstrip("\\r\\n")
            <some>
              a text
              with multiple lines
              and indentation and trailing blanks
            </some>

        Empty text does not result in any output:

            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)
            >>> xml.startTag("some")
            >>> xml.text("")
            >>> xml.endTag()
            >>> print out.getvalue().rstrip("\\r\\n")
            <some>
            </some>
        """
        self._possiblyFlushTag()
        _validateNotNone("text", text)
        uniText = self._unicodedFromString(text)
        if self._pretty:
            for uniLine in io.StringIO(uniText):
                self._writeIndent()
                uniLine = uniLine.lstrip(" \t").rstrip(" \t\r\n")
                self._writeEscaped(uniLine)
                self.newline()
        else:
            self._writeEscaped(uniText)


    def comment(self, text, embedInBlanks=True):
        """
        Write an XML comment.

        As example set up a writer:

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)

        Now add the comment

            >>> xml.comment("some comment")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <!-- some comment -->

        A comment can spawn multiple lines. If pretty is enabled, the lines
        will be indented. Again, first set up a writer:

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)

        Then add the comment

            >>> xml.comment("some comment\\nspawning mutiple\\nlines")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <!--
            some comment
            spawning mutiple
            lines
            -->
        """
        self._possiblyFlushTag()
        uniText = self._unicodedFromString(text)
        if not embedInBlanks and not uniText:
            raise XmlError("text for comment must not be empty, or option embedInBlanks=True must be set")
        if "--" in uniText:
            raise XmlError("text for comment must not contain \"--\"")
        hasNewline = ("\n" in uniText) or ("\r" in uniText)
        hasStartBlank = uniText and uniText[0].isspace()
        hasEndBlank = (len(uniText) > 1) and uniText[-1].isspace()
        self._writePrettyIndent()
        self._write("<!--");
        if hasNewline:
            if self._pretty:
                self.newline()
            elif embedInBlanks and not hasStartBlank:
                self._write(" ")
            for uniLine in io.StringIO(uniText):
                if self._pretty:
                    self._writeIndent()
                self._writeEscaped(uniLine.rstrip("\n\r"))
                self.newline()
            self._writePrettyIndent()
        else:
            if embedInBlanks and not hasStartBlank:
                self._write(" ")
            self._writeEscaped(uniText)
            if embedInBlanks and not hasEndBlank:
                self._write(" ")
        self._write("-->");
        if self._pretty:
            self.newline()


    def cdata(self, text):
        """
        Write a CDATA section.

        As example set up a writer:

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)

        Now add the CDATA section:

            >>> xml.cdata("some data\\nlines\\n<tag>&&&")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <![CDATA[some data
            lines
            <tag>&&&]]>
        """
        self._possiblyFlushTag()
        self._rawBlock("CDATA section", XmlWriter._CDATA_START, XmlWriter._CDATA_END, text)

    def processingInstruction(self, target, text):
        """
        Write a processing instruction.

        As example set up a writer:

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)

        Now add the processing instruction:

            >>> xml.processingInstruction("xsl-stylesheet", "href=\\"some.xsl\\" type=\\"text/xml\\"")

        And the result is:

            >>> print out.getvalue().rstrip("\\r\\n")
            <?xsl-stylesheet href="some.xsl" type="text/xml"?>
        """
        self._possiblyFlushTag()
        targetName = "target for processing instrution"
        _validateNotNone(targetName, text)
        _validateNotEmpty(targetName, text)
        uniFullText = self._unicodedFromString(target)
        if text:
            uniFullText += " "
            uniFullText += self._unicodedFromString(text)
        self._rawBlock("processing instruction", XmlWriter._PROCESSING_START, XmlWriter._PROCESSING_END, uniFullText)

    def _rawBlock(self, name, start, end, text):
        _assertIsUnicode("name", name)
        _assertIsUnicode("start", start)
        _assertIsUnicode("end", end)
        _validateNotNone("text for %s" % name, text)
        uniText = self._unicodedFromString(text)
        if end in uniText:
            raise XmlError("text for %s must not contain \"%s\"" % (name, end))
        self._writePrettyIndent()
        self._write(start)
        self._write(uniText)
        self._write(end)
        self._writePrettyNewline()

    def raw(self, text):
        """
        Write raw ``text`` without escaping, validation and pretty printing.

        Using a writer like

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)

        you can use ``raw`` for good and add for exmaple a doctype declaration:

            >>> xml.raw("<!DOCTYPE html PUBLIC \\"-//W3C//DTD XHTML 1.0 Transitional//EN\\" \\"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd\\">")
            >>> print out.getvalue().rstrip("\\r\\n")
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

        but you can also do all sorts of evil things which can invalidate the XML document:

            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out, prolog=False)
            >>> xml.raw(">(^_^)<  not particular valid XML &&&")
            >>> print out.getvalue().rstrip("\\r\\n")
            >(^_^)<  not particular valid XML &&&
        """
        self._possiblyFlushTag()
        _validateNotNone("text", text)
        uniText = self._unicodedFromString(text)
        self._write(uniText)

    def close(self):
        """
        Close the writer, validate that all started elements have ended and
        prevent further output.

        Using a writer like

            >>> import io
            >>> out = io.BytesIO()
            >>> xml = XmlWriter(out)

        you can write a tag without closing it:

            >>> xml.startTag("some")

        However, once you try to close the writer, you get:

            >>> xml.close()
            Traceback (most recent call last):
                ...
            XmlError: missing end tags must be added: </some>
        """
        self._possiblyFlushTag()
        remainingElements = ""
        while self._elementStack:
            if remainingElements:
                remainingElements += ", "
            namespace, name = self._elementStack.pop()
            remainingElements += "</%s>" % self._elementName(name, namespace)
        if remainingElements:
            raise XmlError("missing end tags must be added: %s" % remainingElements)


class ChainXmlWriter(XmlWriter):
    """
    XmlWriter-wrapper for method chaining, here is an example:
        >>> import io
        >>> out = io.BytesIO()
        >>> xml = ChainXmlWriter(out)
        >>> xml.addNamespace("xhtml", "http://www.w3.org/1999/xhtml") #doctest: +ELLIPSIS
        <loxun.ChainXmlWriter object at 0x...>
        >>> xml.startTag("xhtml:html").startTag("xhtml:body") #doctest: +ELLIPSIS
        <loxun.ChainXmlWriter object at 0x...>
        >>> xml.text("Hello world!").tag("xhtml:img", {"src": "smile.png", "alt": ":-)"}) #doctest: +ELLIPSIS
        <loxun.ChainXmlWriter object at 0x...>
        >>> xml.endTags().close()

    And the result is:

        >>> print out.getvalue().rstrip("\\r\\n")
        <?xml version="1.0" encoding="utf-8"?>
        <xhtml:html xmlns:xhtml="http://www.w3.org/1999/xhtml">
          <xhtml:body>
            Hello world!
            <xhtml:img alt=":-)" src="smile.png" />
          </xhtml:body>
        </xhtml:html>
    """

    chainableMethods = ('addNamespace', 'cdata', 'comment', 'endTag',
                        'endTags', 'processingInstruction', 'startTag', 'tag',
                        'text',)

    def _chainDecorator(self, func):
        def _wrapper(*args, **kwargs):
            func(*args, **kwargs)
            return self
        return _wrapper

    def __getattribute__(self, name):

        if name in ChainXmlWriter.chainableMethods:
            originalMethod = getattr(super(ChainXmlWriter, self), name)
            return self._chainDecorator(originalMethod)

        return super(ChainXmlWriter, self).__getattribute__(name)

if __name__ == "__main__":
    import doctest
    print("loxun %s: running doctest" % __version__)
    doctest.testmod()

