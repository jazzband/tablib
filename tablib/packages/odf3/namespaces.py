# -*- coding: utf-8 -*-
# Copyright (C) 2006-2010 Søren Roug, European Environment Agency
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#
TOOLSVERSION = "ODFPY/0.9.3"

ANIMNS         = "urn:oasis:names:tc:opendocument:xmlns:animation:1.0"
DBNS           = "urn:oasis:names:tc:opendocument:xmlns:database:1.0"
CHARTNS        = "urn:oasis:names:tc:opendocument:xmlns:chart:1.0"
CONFIGNS       = "urn:oasis:names:tc:opendocument:xmlns:config:1.0"
#DBNS           = u"http://openoffice.org/2004/database"
DCNS           = "http://purl.org/dc/elements/1.1/"
DOMNS          = "http://www.w3.org/2001/xml-events"
DR3DNS         = "urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0"
DRAWNS         = "urn:oasis:names:tc:opendocument:xmlns:drawing:1.0"
FIELDNS        = "urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0"
FONS           = "urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0"
FORMNS         = "urn:oasis:names:tc:opendocument:xmlns:form:1.0"
GRDDLNS        = "http://www.w3.org/2003/g/data-view#"
KOFFICENS      = "http://www.koffice.org/2005/"
MANIFESTNS     = "urn:oasis:names:tc:opendocument:xmlns:manifest:1.0"
MATHNS         = "http://www.w3.org/1998/Math/MathML"
METANS         = "urn:oasis:names:tc:opendocument:xmlns:meta:1.0"
NUMBERNS       = "urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0"
OFFICENS       = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
OFNS           = "urn:oasis:names:tc:opendocument:xmlns:of:1.2"
OOONS          = "http://openoffice.org/2004/office"
OOOWNS         = "http://openoffice.org/2004/writer"
OOOCNS         = "http://openoffice.org/2004/calc"
PRESENTATIONNS = "urn:oasis:names:tc:opendocument:xmlns:presentation:1.0"
RDFANS         = "http://docs.oasis-open.org/opendocument/meta/rdfa#"
RPTNS          = "http://openoffice.org/2005/report"
SCRIPTNS       = "urn:oasis:names:tc:opendocument:xmlns:script:1.0"
SMILNS         = "urn:oasis:names:tc:opendocument:xmlns:smil-compatible:1.0"
STYLENS        = "urn:oasis:names:tc:opendocument:xmlns:style:1.0"
SVGNS          = "urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0"
TABLENS        = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
TEXTNS         = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
XFORMSNS       = "http://www.w3.org/2002/xforms"
XLINKNS        = "http://www.w3.org/1999/xlink"
XMLNS          = "http://www.w3.org/XML/1998/namespace"
XSDNS          = "http://www.w3.org/2001/XMLSchema"
XSINS          = "http://www.w3.org/2001/XMLSchema-instance"

nsdict = {
   ANIMNS: 'anim',
   CHARTNS: 'chart',
   CONFIGNS: 'config',
   DBNS: 'db',
   DCNS: 'dc',
   DOMNS: 'dom',
   DR3DNS: 'dr3d',
   DRAWNS: 'draw',
   FIELDNS: 'field',
   FONS: 'fo',
   FORMNS: 'form',
   GRDDLNS: 'grddl',
   KOFFICENS: 'koffice',
   MANIFESTNS: 'manifest',
   MATHNS: 'math',
   METANS: 'meta',
   NUMBERNS: 'number',
   OFFICENS: 'office',
   OFNS: 'of',
   OOONS: 'ooo',
   OOOWNS: 'ooow',
   OOOCNS: 'oooc',
   PRESENTATIONNS: 'presentation',
   RDFANS: 'rdfa',
   RPTNS:  'rpt',
   SCRIPTNS: 'script',
   SMILNS: 'smil',
   STYLENS: 'style',
   SVGNS: 'svg',
   TABLENS: 'table',
   TEXTNS: 'text',
   XFORMSNS: 'xforms',
   XLINKNS: 'xlink',
   XMLNS: 'xml',
   XSDNS: 'xsd',
   XSINS: 'xsi',
}
