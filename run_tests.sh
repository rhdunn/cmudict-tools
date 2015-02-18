#!/bin/bash

LOG_FILE=run_tests.log
rm -rf ${LOG_FILE}

check() {
	MESSAGE=$1
	OUT_FILE=$2
	shift
	shift

	RES_FILE=/tmp/cmudict_tools_test.out

	echo "-------------------------------------------------------------------------------" >> ${LOG_FILE}
	echo "command  : ./cmudict-tools $@" >> ${LOG_FILE}
	echo "expected : ${OUT_FILE}" >> ${LOG_FILE}
	echo >> ${LOG_FILE}

	echo -n "testing ${MESSAGE} ... " | tee -a ${LOG_FILE}
	./cmudict-tools $@ > ${RES_FILE}
	diff ${OUT_FILE} ${RES_FILE} > /dev/null
	if [[ $? -eq 0 ]] ; then
		echo "pass" | tee -a ${LOG_FILE}
	else
		echo "fail" | tee -a ${LOG_FILE}
		echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> ${LOG_FILE}
		diff -U0 ${OUT_FILE} ${RES_FILE} >> ${LOG_FILE}
		echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" >> ${LOG_FILE}
	fi
}

# Parser Tests ################################################################
#
# NOTE: These tests also include validation check errors relating to parsing
# the specific file formats (i.e. formatting errors). They do not test other
# validation checks.

ARGS="print -Wall -Wno-unsorted --format=json"
check "cmudict format parsing"       tests/cmudict.json     ${ARGS} tests/cmudict
check "cmudict-weide format parsing" tests/cmudict.json     ${ARGS} tests/cmudict-weide
check "cmudict-new format parsing"   tests/cmudict-new.json ${ARGS} tests/cmudict-new
check "festlex format parsing"       tests/festlex.json     ${ARGS} tests/festlex.scm

# Summary #####################################################################

if [[ `grep -P "^testing .* \\.\\.\\. fail$" ${LOG_FILE}` ]] ; then
	exit 1
else
	exit 0
fi
