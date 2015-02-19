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
check "en-US phones" tests/phone_en-US-x-arpabet.json ${ARGS} --source-accent=en-US tests/phone_arpabet.upper
check "en-US-x-cmu phones" tests/phone_en-US-x-cmu.json ${ARGS} --source-accent=en-US-x-cmu tests/phone_arpabet.upper
check "en-US-x-festvox phones" tests/phone_en-US-x-festvox.json ${ARGS} --source-accent=en-US-x-festvox tests/phone_arpabet.lower

ARGS="print -Wnone -Winvalid-phonemes -Wmissing-stress --format=json"
check "en-GB phones" tests/phone_en-GB-x-rp-arpabet.json ${ARGS} --source-accent=en-GB tests/phone_arpabet.upper

ARGS="print -Wall -Wno-unsorted --format=json"
check "syllable breaks [en-GB]" tests/phone-syllables.json ${ARGS} --source-accent=en-GB tests/phone-syllables
check "syllable breaks [en-US]" tests/phone-syllables.json ${ARGS} --source-accent=en-US tests/phone-syllables

# Summary #####################################################################

if [[ `grep -P "^testing .* \\.\\.\\. fail$" ${LOG_FILE}` ]] ; then
	exit 1
else
	exit 0
fi
