LIBRESWANSRCDIR?=$(shell cd ../..; pwd)
srcdir?=${LIBRESWANSRCDIR}/initsystems/systemd/

UPSTARTFILE=ipsec.conf
DEFAULTFILE=default.pluto
SUBDIRS=
UPSTARTDIR=$(DESTDIR)/etc/init
DEFAULTDIR=$(CONFDIR)/default

include ${LIBRESWANSRCDIR}/Makefile.inc
include ${LIBRESWANSRCDIR}/Makefile.top

programs:     upstartfiles defaultfiles
upstartfiles: $(UPSTARTFILE)
defaultfiles: $(DEFAULTFILE)
install:      programs doinstall

doinstall: programs installupstartconf installdefault

installupstartconf:
	@mkdir -p $(UPSTARTDIR)
	$(INSTALL) $(UPSTARTFILE) $(UPSTARTDIR);

installdefault:
	mkdir -p $(DEFAULTDIR)
	if test ! -f $(DEFAULTDIR)/pluto ; then \
		$(INSTALL) $(DEFAULTFILE) $(DEFAULTDIR)/pluto ; \
	fi

%: ${srcdir}%.in ${LIBRESWANSRCDIR}/Makefile.inc ${LIBRESWANSRCDIR}/Makefile.ver ${LIBRESWANSRCDIR}/Makefile.top
	@echo  'IN' $< '->' $@
	${TRANSFORM_VARIABLES} < $< > $@
	@if [ -x $< ]; then chmod +x $@; fi
	@if [ "${PROGRAM}.in" = $< ]; then chmod +x $@; fi
