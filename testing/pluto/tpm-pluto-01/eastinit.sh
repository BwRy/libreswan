: ==== start ====
TESTNAME=tpm-pluto-01
source /testing/pluto/bin/eastlocal.sh

ipsec setup start
/testing/pluto/bin/wait-until-pluto-started

ipsec auto --add westnet-eastnet
#ipsec whack --debug-control --debug-controlmore --debug-crypt
