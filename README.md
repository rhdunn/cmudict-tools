# CMU Pronunciation Dictionary Tools

This is a collection of tools for working with the CMU Pronunciation
Dictionary.

## Metadata Descriptions

The valid `(key,value)` pairs for entry-based metadata is defined in a metadata
description file.

To test the `(key,value)` extraction, you can run:

	python metadata.py <metadata-description-file>

This will output JSON text, for example:

	{"key1": ["value1", "value2"], "key2": ["value3"]}

### CSV Metadata Description File

This is a CSV document with the following minimal structure:

	Key,Value
	key1,value1
	...
	keyN,valueN

Additional fields are ignored, but must have a unique title label.

### RDF Metadata Description File

This is an RDF document (turtle, RDF/XML or N-Triples) using the SKOS ontology.
In order to parse these documents, the `rapper` tool is needed.

A `key` is defined as a `skos:ConceptScheme` and a `value` as a `skos:Concept`.
The labels are defined using `skos:prefLabel` predicates. A `value` is
associated with a `key` using the `skos:inScheme` predicate. All other metadata
triples are ignored.

For example, to support `key=value` a minimal RDF Turtle file is:

	@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

	<#> a skos:ConceptScheme ; skos:prefLabel "key" .

	<#val> a skos:Concept ; skos:prefLabel "value" ; skos:inScheme <#> .

## License

The CMU Pronunciation Dictionary Tools are released under the GPL version 3 or
later license.

Copyright (C) 2015 Reece H. Dunn
