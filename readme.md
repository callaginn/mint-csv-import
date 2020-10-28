# Mint CSV Importer
Simulates bulk manual transaction adds to mint.com. Mint manual transactions are submitted as "cash transactions" which will mean it shows in your cash / all accounts transaction list. You cannot submit manual transactions against credit cards or other integrated bank accounts (even in Mint's UI this is not possible and ends up as cash transaction).

Simulating manual transactions from UI is based on Nate H's proof of concept from https://www.youtube.com/watch?v=8AJ3g5JGmdU

Credit to https://github.com/ukjimbow for his work on Mint imports for UK users in https://github.com/ukjimbow/mint-transactions

## Usage:
Run the code by typing the following from the directory the code is located in
```
./import.py
```

## Pre-requisites needed
- csv
- json
- datetime
- os
- random
- requests
- time
- urllib.parse

## Virtual Env Setup (from repo root)
1. Make sure you have venv on your system, using the following command based on your python version
```shell
pip3 install virtualenv
```
2. Make sure you are in repo root
	- (where import.py and requirements.txt are)
3. Create a virtual environment
```shell
virtualenv venv
```
4. Turn on the virtual environment (these should work on both but depends on your version you may need to explicitly run the sh or bat file)
	- Mac / Linux in terminal or bash: venv/Scripts/activate
    - Windows in powershell: venv\Scripts\activate
5. Install Requirements
```shell
pip3 install -r requirements.txt
```

if you do not want to use venv you can manually install any dependencies with the following:

	pip3 install $name
	Example: pip3 install csv

## Process
1. Import CSV
2. Process date for correct format and HTTP encode result
3. Process merchant for HTTP encode
4. Process categories change your banks category name into a mint category ID (limited in scope based on the categories I needed when I wrote this)
5. Process amount for positive or negative value indicating income or expense
6. Send POST Request to mint as new transaction.
7. Force Randomized Wait Time before starting next request

## Process Categories
Support is limited to the categories I needed at the time, if you need to map more you can. To get category ids:
1. Go to mint
2. Add a transactions
3. Right click "inspect-element" on the category you want
4. The ID is in the <li> item that encapsulates the a href
5. Add mapping here based on string match from your CSV to the catID you got from mint (following existing examples)

## Future Development
1. Replace curl command string generation with parameterized curl class constructor
2. Add support for the rest of the manual transaction items
