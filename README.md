# ChartParser

ChartParser provides a basic framework and simple user interface for chart parsing sentences as set forth by Kay (1982) and described by Jurafsky (2009). The user can import existing grammars and lexica (an example of each is provided in data/), or create them on the fly.

This limited parser tokenizes words on whitespace and does not strip punctuation from the inputted sentence. Only one parse, if any, is provided to the user.

The format of the grammar and lexicon is very specific. Any deviation from this format will break the parser.

### Grammar
Any imported grammar must use the following format to specify a rule, one rule per line:
```
parent --> child1 child2 ... childn
```
The rule must have one parent on the left side of the arrow '-->'. The rule must have one or more children on the righthand side separated by spaces.

### Lexicon
Any imported lexicon must use the following format to specify a lexical entry, one entry per line:
```
word : part_of_speech
```
The lexical entry must have exactly one word on the left hand side (no compound words unless they are joined by a character other than whitespace, which the user must expect to also provide in the inputted sentence) and one part of speech on the left hand side.

## Prerequisites

* Python3
* tkinter

## Running the tests

Tests can be run by calling pytest from anywhere in the package.

## Versions

ChartParser 0.2.0 - Current parser, upgraded to use object oriented programming, but otherwise same funcationlity as version 0.1.0.
ChartParser 0.1.0 - First GUI chart parser built for CSE 415 class in Spring 2012.

## Author

Kathryn Egan

## License

TBD

## Acknowledgments

Thanks to Maria McKinley and Chris Barker at UW for reviewing version 1.1.0 of this code, and to Professor Tanimoto for reviewing version 0.1.0.

## References

Jurafsky, D. and Martin J (2009). *Speech and Language Processing: An Introduction to Natural Language Processing, Computational Linguistics and Speech Recognition*. 2nd ed. Upper Saddle River, New Jersy: Pearson/Prentice-Hall.

Kay, M. (1982). Algorithm schemata and data structures in syntactic processing. In Allen, S. (Ed.) *Text Processing: Text Analysis and Generation, Text Typology and Attribution*, pp. 327-358. Almqvist and Wiksell, Stockholm.