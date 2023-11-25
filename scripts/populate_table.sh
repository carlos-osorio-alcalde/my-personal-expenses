#!/bin/bash

# Set the bearer token
export BEARER_TOKEN=""
export URL_API_EXPENSES="http://ec2-23-20-155-185.compute-1.amazonaws.com:5000"
export URL_API_MONITORING="https://monitoring-expenses.orangecliff-ed60441b.eastus.azurecontainerapps.io"

# Run the first curl command to get the new transactions
curl -X 'POST' \
  '$URL_API_EXPENSES/database/populate_table/?timeframe=weekly' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer $BEARER_TOKEN' 

# Run the second curl command to check if there are transactions without labels
result=$(curl -s -X 'GET' \
  '$URL_API_EXPENSES/database/check_if_there_are_trxs_without_labels' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer $BEARER_TOKEN' 
  
# Check if the result is "True"
if "$result"; then
  # If true, run the third curl command
  curl -X 'POST' \
    '$URL_API_MONITORING/label_and_save_transactions' \
    -H 'accept: application/json' \
    -d ''
else
  # If false, print a message or take other actions
  echo "No transactions without labels found."
fi