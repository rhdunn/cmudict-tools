#!/bin/bash
#
# Copyright (C) 2015 Reece H. Dunn
#
# This file is part of cmudict-tools.
#
# cmudict-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cmudict-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with cmudict-tools.  If not, see <http://www.gnu.org/licenses/>.

PYTHON=${PYTHON:-python}
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
	${PYTHON} ./cmudict-tools $@ 2>&1 | tee > ${RES_FILE}
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
check "cmudict format parsing"       tests/cmudict.json       ${ARGS} tests/cmudict
check "cmudict-weide format parsing" tests/cmudict-weide.json ${ARGS} tests/cmudict-weide
check "cmudict-new format parsing"   tests/cmudict-new.json   ${ARGS} tests/cmudict-new
check "festlex format parsing"       tests/festlex.json       ${ARGS} tests/festlex.scm

# File-Based Metadata #########################################################

ARGS="print -Wall -Wno-unsorted --format=json"
check "file metadata format key" tests/filemeta-format.json ${ARGS} tests/filemeta-format

# Formatter Tests #############################################################

ARGS="print -Wall -Wno-unsorted"
check "cmudict formatting" tests/format-cmudict ${ARGS} --format=cmudict tests/format-cmudict
check "cmudict-weide formatting" tests/format-cmudict-weide ${ARGS} --format=cmudict-weide tests/format-cmudict
check "cmudict-new formatting" tests/format-cmudict-new ${ARGS} --format=cmudict-new tests/format-cmudict
check "festlex formatting" tests/format-festlex.scm ${ARGS} --format=festlex tests/format-cmudict

# Phone Tests #################################################################

ARGS="print -Wnone -Winvalid-phonemes -Wmissing-stress --format=json"
check "default accent and phoneset" tests/phone_en-US-x-cmu.json ${ARGS} tests/phone_arpabet.upper
check "default accent, arpabet phones" tests/phone_en-US-x-arpabet.json ${ARGS} --source-phoneset=arpabet tests/phone_arpabet.upper

ARGS="print -Wnone -Winvalid-phonemes -Wmissing-stress --format=json --source-accent=en-US"
check "en-US accent, arpabet phones" tests/phone_en-US-x-arpabet.json ${ARGS} --source-phoneset=arpabet tests/phone_arpabet.upper
check "en-US accent, cmu phones" tests/phone_en-US-x-cmu.json ${ARGS} --source-phoneset=cmu tests/phone_arpabet.upper
check "en-US accent, cepstral phones" tests/phone_en-US-x-cepstral.json ${ARGS} --source-phoneset=cepstral tests/phone_arpabet.lower
check "en-US accent, festvox phones" tests/phone_en-US-x-festvox.json ${ARGS} --source-phoneset=festvox tests/phone_arpabet.lower
check "en-US accent, timit phones" tests/phone_en-US-x-timit.json ${ARGS} --source-phoneset=timit tests/phone_arpabet.lower

ARGS="print -Wnone -Winvalid-phonemes -Wmissing-stress --format=json --source-accent=en-GB-x-rp"
check "en-GB-x-rp accent, arpabet phones" tests/phone_en-GB-x-rp-arpabet.json ${ARGS} --source-phoneset=arpabet tests/phone_arpabet.upper
check "en-GB-x-rp accent, cepstral phones" tests/phone_en-GB-x-rp-cepstral.json ${ARGS} --source-phoneset=cepstral tests/phone_arpabet.lower

ARGS="print -Wnone -Winvalid-phonemes -Wmissing-stress --format=json --source-accent=en-US"
check "cmu phones in other case" tests/phone_en-US-x-cmu_othercase.json ${ARGS} --source-phoneset=cmu tests/phone_arpabet.lower
check "festvox phones in other case" tests/phone_en-US-x-festvox_othercase.json ${ARGS} --source-phoneset=festvox tests/phone_arpabet.upper

ARGS="print -Wnone -Winvalid-phonemes -Wmissing-stress --format=json --source-phoneset=arpabet"
check "accents/en-US.csv accent, arpabet phones" tests/phone_en-US-x-arpabet.json ${ARGS} --source-accent=accents/en-US.csv tests/phone_arpabet.upper
check "accents/en-GB-x-rp.csv accent, arpabet phones" tests/phone_en-GB-x-rp-arpabet.json ${ARGS} --source-accent=accents/en-GB-x-rp.csv tests/phone_arpabet.upper

# Validate Tests ##############################################################

ARGS="print -Wnone --format=json"
check "-Wnone" tests/phone_en-US-x-cmu_Wnone.json ${ARGS} tests/phone_arpabet.upper

# Print Tests #################################################################

ARGS="print -Wnone --source-phoneset=arpabet --accent=en-US"
check "printing en-US accent, arpabet phones" tests/phone_arpabet.upper ${ARGS} --phoneset=arpabet tests/phone_arpabet.upper
check "printing en-US accent, festvox phones" tests/phone_arpabet.lower ${ARGS} --phoneset=festvox tests/phone_arpabet.upper

ARGS="print -Wnone --source-phoneset=arpabet"
check "printing default accent, arpabet phones" tests/phone_arpabet.upper ${ARGS} --phoneset=arpabet tests/phone_arpabet.upper
check "printing default accent, festvox phones" tests/phone_arpabet.lower ${ARGS} --phoneset=festvox tests/phone_arpabet.upper

# Summary #####################################################################

if [[ `grep -P "^testing .* \\.\\.\\. fail$" ${LOG_FILE}` ]] ; then
	exit 1
else
	exit 0
fi
