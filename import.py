#!/usr/bin/env python3

import csv, json, datetime, subprocess, random, requests, time, urllib.parse

settings_file = open('settings.json')
settings = json.load(settings_file)
settings_file.close()

categories_file = open('categories.json')
category_ids = json.load(categories_file)
categories_file.close()
category_names = dict([(value, key) for key, value in category_ids.items()])

"""
#################################
Settings
#################################
"""

# General Settings
csv_name = settings['csv_name']
verbose_output = settings['verbose_output']
min_wait = settings['min_wait']
max_wait = settings['max_wait']

# Mint Client Credentials
# You will need the tags, cookie, and token to simulate a UI form submission. You can get these by opening developer tools > network analysis tab and doing a test submission in mint.com. From there look for the post request to "updateTransaction.xevent" and grab the credentials from the header and body
account = settings['account']
tag1 = settings['tag1']
tag2 = settings['tag2']
tag3 = settings['tag3']
cookie = settings['cookie']
referrer = settings['referrer']
token = settings['token']
"""
#################################
Import CSV using the pythons csv reader
#################################
"""
csv_object = csv.reader(open(csv_name,'r'))
next(csv_object)

for row in csv_object:

	# Initialize Variables
	date = (row[0])
	postDate = (row[1])
	merchant = (row[2])
	catID = (row[3])
	typeID = (row[4])
	amount = (float(row[5]))
	expense = 'true'
	curl_input = 'Error: Did not Generate'
	curl_output = 'Error: Did not run'

	"""
	#################################
	Process Date for HTTP Encode
	#################################
	"""

	# Require "/" for date delimiter and HTTP Encode Character, supports "/", ".", "-"
	# We are not using url encode library here because we custom map other delimiters
	dateoutput = date.replace("/", "%2F")
	dateoutput = date.replace(".", "%2F")
	dateoutput = date.replace("-", "%2F")

	"""
	#################################
	Process Merchant with HTTP Encode
	#################################
	"""
	merchant = urllib.parse.quote(merchant)

	"""
	#################################
	Process Categories
	#################################
	"""

	# Get the mint category ID from the map
	def category_id_switch(import_category):
		return category_ids.get(import_category,20)

	# Get the mint category NAME from the map
	def category_name_switch(mint_id):
		return category_names.get(mint_id,'Uncategorized')

	# typeID payment overrides all categories
	if typeID == "Payment":
		catID = '2101' # Since I was importing credit cards I have mine set to credit card payment. If you are doing bank accounts you many want to change this to payment general

	# if type is NOT payment then do a category check
	else:

		# if there IS no cat it is uncategorized
		if len(catID) == 0:
			catID = '20' # mint's uncategorized category

		# If there is a category check it against mapping
		else :
			# Use a switch since there may be MANY category maps
			catID = str(category_id_switch(catID))


	# Set mint category name by looking up name in ID map
	category = category_name_switch(catID)
	category = urllib.parse.quote(category)

	"""
	#################################
	Process Amount seeing if transaction is an expense or income.
	#################################
	"""
	if amount < 0:
		expense = 'true' # when amount is less than 0 this is an expense, ie money left your account, ex like buying a sandwich.
	else:
		expense = 'false' # when amount is greater than 0 this is income, ie money went INTO your account, ex like a paycheck.
	amount = str(amount) # convert amount to string so it can be concatenated in POST request

	"""
	#################################
	Build CURL POST Request
	TODO: Swap command string generation for parametized curl class
	#################################
	"""

	# Break curl lines
	curl_line = " "

	# fragment curl command
	curl_command = "curl -i -s -k -X POST 'https://mint.intuit.com/updateTransaction.xevent'" + curl_line
	curl_host = "-H 'Host: mint.intuit.com'" + curl_line
	curl_user_agent = "-H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'" + curl_line
	curl_accept = "-H 'Accept: */*'" + curl_line
	curl_accept_language = "-H 'Accept-Language: en-US,en;q=0.5'" + curl_line
	curl_compressed = "--compressed" + curl_line
	curl_x_requested_with = "-H 'X-Requested-With: XMLHttpRequest'" + curl_line
	curl_content_type = "-H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8'" + curl_line
	curl_referer = "-H 'Referer: https://mint.intuit.com/transaction.event?accountId=" + referrer + "'" + curl_line
	curl_cookie = "-H 'Cookie: " + cookie + "'" + curl_line
	curl_connection = "-H 'Connection: close' " + curl_line
	curl_data =  "--data" + curl_line

	# Fragment the curl form data
	form_p1 = "'cashTxnType=on&mtCheckNo=&" + tag1 + "=0&" + tag2 + "=0&" + tag3 + "=0&"
	form_p2 = "task=txnadd&txnId=%3A0&mtType=cash&mtAccount=" + account + "&symbol=&note=&isInvestment=false&"
	form_p3 = "catId="+catID+"&category="+category+"&merchant="+merchant+"&date="+dateoutput+"&amount="+amount+"&mtIsExpense="+expense+"&mtCashSplitPref=2&"
	form_p4 = "token=" + token + "'"

	# Piece together curl form data
	curl_form = form_p1 + form_p2 + form_p3 + form_p4

	# Combine all curl fragments together into an entire curl command
	curl_input = curl_command + curl_host + curl_user_agent + curl_accept + curl_accept_language + curl_compressed + curl_x_requested_with + curl_content_type + curl_referer + curl_cookie + curl_connection + curl_data + curl_form

	"""
	#################################
	Submit CURL POST Request
	#################################
	"""
	curl_output = subprocess.check_output(curl_input, shell=True).decode()

	"""
	#################################
	Verbose Output for Debug
	#################################
	"""

	if verbose_output == 1:
		print('Transaction Date:', dateoutput) # date of transaction
		print('Merchant:', merchant) # merchant Description
		print('Category ID:', catID) # category of transaction
		print('Category Name:', category) # category of transaction
		print('Amount:', amount) # amount being processed
		print('Expense:', expense) # in amount expense
		print('CURL Request:', curl_input) # what was sent to mint
		print('CURL Response:', curl_output) # what was returned from mint OR curl ERROR
		print('\n\n==============\n') # new line break

	if "Session has expired" in curl_output:
		print("Exiting Script: Session has expired")
		print('Transaction Date:', dateoutput)
		print('Merchant:', merchant)
		print('Amount:', amount)
		exit()

	"""
	#################################
	Force a random wait between 2 and 5 seconds per requests to simulate UI and avoid rate limiting
	#################################
	"""
	time.sleep(random.randint(min_wait, max_wait))
