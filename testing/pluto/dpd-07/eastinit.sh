: ==== start ====

TESTNAME=dpd-07

source /testing/pluto/bin/eastlocal.sh

ipsec setup start
/testing/pluto/bin/wait-until-pluto-started

ipsec auto --add west-east



