# Copyright (c) 2001-2011 Python Software Foundation
#
# License: PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2
#          See http://www.opensource.org/licenses/Python-2.0 for full terms

import sys
from xml.sax.saxutils import XMLGenerator as _XMLGenerator, quoteattr

if sys.version_info < (2, 5):

    try:
        from codecs import xmlcharrefreplace_errors
        _error_handling = "xmlcharrefreplace"
        del xmlcharrefreplace_errors
    except ImportError:
        _error_handling = "strict"

    class XMLGenerator(_XMLGenerator):

        def _qname(self, name):
            """Builds a qualified name from a (ns_url, localname) pair"""
            if name[0]:
                # The name is in a non-empty namespace
                prefix = self._current_context[name[0]]
                if prefix:
                    # If it is not the default namespace, prepend the prefix
                    return prefix + ":" + name[1]
            # Return the unqualified name
            return name[1]

        def startElementNS(self, name, qname, attrs):
            self._write('<' + self._qname(name))

            for prefix, uri in self._undeclared_ns_maps:
                if prefix:
                    self._out.write(' xmlns:%s="%s"' % (prefix, uri))
                else:
                    self._out.write(' xmlns="%s"' % uri)
            self._undeclared_ns_maps = []

            for (name, value) in attrs.items():
                self._write(' %s=%s' % (self._qname(name), quoteattr(value)))
            self._write('>')

        def endElementNS(self, name, qname):
            self._write('</%s>' % self._qname(name))

        def _write(self, text):
            if isinstance(text, str):
                self._out.write(text)
            else:
                self._out.write(text.encode(self._encoding, _error_handling))
else:
    XMLGenerator = _XMLGenerator
