# oeis-search
This is a script to perform complex searches on the OEIS database. 

# Instructions

* Download each of the two compressed files given [here](https://oeis.org/wiki/Welcome#Compressed_Versions) at the OEIS.
* Decompress the files, which should have default filenames of `names.txt` and `stripped.txt`.
* Put these two files in the same folder as the `oeis.py` file.
* Run `oeis.py`, at which point you will be prompted to enter a search. 

# Syntax

Some progressively more complicated searches, and the conditions they impose on a sequence: 

* `1, 2, 3, 4`: Sequence must start with those four terms in that order.
* `0?, 1, 2, 3, 4`: Sequence must start with either `0, 1, 2, 3, 4` or `1, 2, 3, 4` (i.e., the 0 is optional).
* `1, 3, 5, 7|8, 10`: Fourth term is either 7 or 8 (along with the other specified terms).
* `even, even, odd, prime`: First term is even, second term is even, third term is odd, fourth term is prime. 
* `1, 2, 3, (4 | prime)`: Fourth term is either 4 or a prime.
* `1, 1, 2, 5, 10-15, >, >=,`: Fifth term is between 10 and 15 inclusive, the sixth term is strictly greater than the fifth, and the seventh term is greater than or equal to the sixth. 
* `2, 4, 2, prime*`: All terms after the third term are prime.
* `3%4, 5%7, (3%5 & <=)*`: First term is congruent to 3 mod 4, second term is congruent to 5 mod 7, all subsequent terms are congruent to 3 mod 5 and less than or equal to the previous term.
* `3*, 5, 7*`: Sequence consists of some nonnegative number of 3s, followed by a 5, followed by some nonnegative number of 7s. 
* `*, 10, 3, 4`: Sequence contains the terms 10, 3, 4 in order consecutively, but not necessarily at the start. 
* `*, 10, *, 3, *, 4`: Sequence contains the terms 10, 3, 4 in order, but not necessarily consecutively.
* `1, 3, 8, _, 11`: There is a fourth term between 8 and 11, but it could be anything.
* `1, 3, 8, (!=3)?, 11`: There might or might not be a term between 8 and 11, but if there is, it isn't 3.
* `_, (!prime & >1)*`: All terms after the first are composite.

The parser supports nested parentheses, if you want to use more complex logic.

