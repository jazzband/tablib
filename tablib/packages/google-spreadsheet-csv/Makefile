
PREFIX=/usr/local
BINDIR=$(PREFIX)/bin
MANDIR=$(PREFIX)/share/man

CFLAGS=-Wall -Werror


all: google-spreadsheet-csv.1

.PHONY: all install clean

google-spreadsheet-csv.1: manual.t2t
	txt2tags -t man -i $^ -o $@

README.textile: manual.t2t
	txt2tags -t html -H -i $^ -o $@
	sed -i -e 's@<B>@**@g' -e 's@</B>@**@g' $@

clean:
	rm -f google-spreadsheet-csv.1

install: google-spreadsheet-csv.1
	mkdir -p $(BINDIR)
	install google-spreadsheet-csv $(BINDIR)/google-spreadsheet-csv
	mkdir -p $(MANDIR)/man1
	install google-spreadsheet-csv.1 $(MANDIR)/man1/google-spreadsheet-csv.1

