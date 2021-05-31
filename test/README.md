# Tests

These can be run using: ./test/runtests.sh

## success/1

Success test 1 - comma separated, uuid does not exist
1.1 Header
1.2 No Header

## success/2

Success test 2 - tab separated

## success/3

Success test 3 - comma separated, uuid exists 
3.1 Generate uuid, Header
3.2 Generate uuid, No Header
3.3 Do not generate uuid, Header 
3.4 Do not generate uuid, No Header 

## success/4

Success test 4 - Non-fatal errors  
4.1 Invalid smiles after first row - skips missing record 
4.2 Invalid uuid / Do not generate uuid - skips missing record
4.3 Invalid uuid / Generate uuid - does not skip record. 

## failure/1

Failure test 1 - comma separated - fail due to invalid smiles first row
Failure test 2 - comma separated - fail due to invalid uuid first row