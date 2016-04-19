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

check_metadata() {
	PROGRAM=$1
	MESSAGE=$2
	OUT_FILE=$3
	SRC_FILE=$4

	case "${PROGRAM}" in
		-)
			PRESENT=yes
			;;
		*)
			if type ${PROGRAM} >/dev/null 2>&1 ; then
				PRESENT=yes
			else
				PRESENT=no
			fi
			;;
	esac

	RES_FILE=/tmp/cmudict_tools_test.out

	echo "-------------------------------------------------------------------------------" >> ${LOG_FILE}
	echo "command  : ./metadata ${SRC_FILE}" >> ${LOG_FILE}
	echo "expected : ${OUT_FILE}" >> ${LOG_FILE}
	echo >> ${LOG_FILE}

	echo -n "testing ${MESSAGE} ... " | tee -a ${LOG_FILE}
	if [[ x${PRESENT} == xyes ]] ; then
		${PYTHON} ./metadata ${SRC_FILE} 2>&1 | tee > ${RES_FILE}
		diff ${OUT_FILE} ${RES_FILE} > /dev/null
		if [[ $? -eq 0 ]] ; then
			echo "pass" | tee -a ${LOG_FILE}
		else
			echo "fail" | tee -a ${LOG_FILE}
			echo "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<" >> ${LOG_FILE}
			diff -U0 ${OUT_FILE} ${RES_FILE} >> ${LOG_FILE}
			echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>" >> ${LOG_FILE}
		fi
	else
		echo "skip" | tee -a ${LOG_FILE}
	fi
}

# Metadata Description Parser Tests ###########################################

check_metadata - "csv metadata parsing" tests/metadata.json tests/metadata.csv
check_metadata rapper "rdf turtle metadata parsing using rapper" tests/metadata.json tests/metadata-turtle
check_metadata rapper "rdf/xml metadata parsing using rapper" tests/metadata.json tests/metadata-rdfxml
check_metadata - "n-triples metadata parsing using rapper" tests/metadata.json tests/metadata-ntriples

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

check "cmudict format parsing; Windows line endings"       tests/cmudict.json       ${ARGS} tests/cmudict-crlf
check "cmudict-weide format parsing; Windows line endings" tests/cmudict-weide.json ${ARGS} tests/cmudict-weide-crlf
check "cmudict-new format parsing; Windows line endings"   tests/cmudict-new.json   ${ARGS} tests/cmudict-new-crlf
check "festlex format parsing; Windows line endings"       tests/festlex.json       ${ARGS} tests/festlex-crlf.scm

ARGS="print -Wall -Wno-unsorted --format=cmudict"
check "cmudict format parsing; utf-8 in, utf-8 out" tests/encoding.utf-8 ${ARGS} --input-encoding=utf-8 --output-encoding=utf-8 tests/encoding.utf-8
check "cmudict format parsing; utf-8 in, latin1 out" tests/encoding.latin1 ${ARGS} --input-encoding=utf-8 --output-encoding=latin1 tests/encoding.utf-8
check "cmudict format parsing; utf-8 in, default out" tests/encoding.utf-8 ${ARGS} --input-encoding=utf-8 tests/encoding.utf-8
check "cmudict format parsing; latin1 in, utf-8 out" tests/encoding.utf-8 ${ARGS} --input-encoding=latin1 --output-encoding=utf-8 tests/encoding.latin1
check "cmudict format parsing; latin1 in, latin1 out" tests/encoding.latin1 ${ARGS} --input-encoding=latin1 --output-encoding=latin1 tests/encoding.latin1
check "cmudict format parsing; latin1 in, default out" tests/encoding.latin1 ${ARGS} --input-encoding=latin1 tests/encoding.latin1

check "cmudict format parsing; encoding=utf-8 metadata" tests/encoding.utf-8.metadata ${ARGS} tests/encoding.utf-8.metadata
check "cmudict format parsing; encoding=latin1 metadata" tests/encoding.latin1.metadata ${ARGS} tests/encoding.latin1.metadata

# File-Based Metadata #########################################################

ARGS="print -Wall -Wno-unsorted --format=json"
check "file metadata format key" tests/filemeta-format.json ${ARGS} tests/filemeta-format

# Formatter Tests #############################################################

ARGS="print -Wall -Wno-unsorted"
check "cmudict formatting" tests/format-cmudict ${ARGS} --format=cmudict tests/format-cmudict
check "cmudict-weide formatting" tests/format-cmudict-weide ${ARGS} --format=cmudict-weide tests/format-cmudict
check "cmudict-new formatting" tests/format-cmudict-new ${ARGS} --format=cmudict-new tests/format-cmudict
check "sphinx formatting" tests/format-sphinx ${ARGS} --format=sphinx tests/format-cmudict
check "festlex formatting" tests/format-festlex.scm ${ARGS} --format=festlex tests/format-cmudict

# Sorting Tests ###############################################################

ARGS="print -Wnone"
check "sorting: default" tests/sorting-none ${ARGS} tests/sorting-none
check "sorting: air" tests/sorting-air ${ARGS} --sort=air tests/sorting-none
check "sorting: none" tests/sorting-none ${ARGS} --sort=none tests/sorting-none
check "sorting: weide" tests/sorting-weide ${ARGS} --sort=weide tests/sorting-none

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
check "accents/en-US.csv accent, arpabet phones" tests/phone_en-US-x-arpabet.json ${ARGS} --source-accent=cmudicttools/accents/en-US.csv tests/phone_arpabet.upper
check "accents/en-GB-x-rp.csv accent, arpabet phones" tests/phone_en-GB-x-rp-arpabet.json ${ARGS} --source-accent=cmudicttools/accents/en-GB-x-rp.csv tests/phone_arpabet.upper

# Validate Tests ##############################################################

ARGS="print -Wnone --format=json"
check "-Wnone" tests/phone_en-US-x-cmu_Wnone.json ${ARGS} tests/phone_arpabet.upper

# Manipulation Tests ##########################################################

ARGS="print -Wnone --source-phoneset=arpabet"
check "--remove-context-entries" tests/no_context ${ARGS} --format=sphinx --remove-context-entries tests/format-cmudict
check "--remove-syllable-breaks" tests/phone_arpabet.no_syllable_breaks ${ARGS} --remove-syllable-breaks tests/phone_arpabet.upper
check "--remove-stress" tests/no_stress ${ARGS} --remove-stress tests/no_stress.dict

# Print Tests #################################################################

ARGS="print -Wnone --source-phoneset=arpabet --accent=en-US"
check "printing en-US accent, arpabet phones" tests/phone_arpabet.upper ${ARGS} --phoneset=arpabet tests/phone_arpabet.upper
check "printing en-US accent, festvox phones" tests/phone_festvox.lower ${ARGS} --phoneset=festvox tests/phone_arpabet.upper
check "printing en-US accent, cepstral phones" tests/phone_en-US-x-cepstral.cmudict ${ARGS} --phoneset=cepstral tests/phone_arpabet.upper

ARGS="print -Wnone --source-phoneset=arpabet --accent=en-GB-x-rp"
check "printing en-GB-x-rp accent, cepstral phones" tests/phone_en-GB-x-rp-cepstral.cmudict ${ARGS} --phoneset=cepstral tests/phone_arpabet.upper

ARGS="print -Wnone --source-phoneset=arpabet"
check "printing default accent, arpabet phones" tests/phone_arpabet.upper ${ARGS} --phoneset=arpabet tests/phone_arpabet.upper
check "printing default accent, festvox phones" tests/phone_festvox.lower ${ARGS} --phoneset=festvox tests/phone_arpabet.upper
check "printing default accent, cepstral phones" tests/phone_en-US-x-cepstral.cmudict ${ARGS} --phoneset=cepstral tests/phone_arpabet.upper

ARGS="print -Wnone --source-phoneset=arpabet --phoneset=ipa --output-encoding=utf-8"
check "printing ipa phones, utf-8 encoding, default accent" tests/phone_en-US.ipa ${ARGS} tests/phone_arpabet.upper
check "printing ipa phones, utf-8 encoding, en-US accent" tests/phone_en-US.ipa ${ARGS} --accent=en-US tests/phone_arpabet.upper
check "printing ipa phones, utf-8 encoding, en-GB-x-rp accent" tests/phone_en-GB-x-rp.ipa ${ARGS} --accent=en-GB-x-rp tests/phone_arpabet.upper

ARGS="print -Wnone --source-phoneset=arpabet --phoneset=ipa"
check "printing ipa phones, default encoding" tests/phone_en-US.ipa ${ARGS} tests/phone_arpabet.upper
check "printing ipa phones, ascii encoding" tests/phone_en-US.ipa ${ARGS} --output-encoding=ascii tests/phone_arpabet.upper

# Summary #####################################################################

if [[ `grep -P "^testing .* \\.\\.\\. fail$" ${LOG_FILE}` ]] ; then
	exit 1
else
	exit 0
fi
