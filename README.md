# Crypto_Price_Tracker

1. '/' or '/minmax' API allows you to set the min and max values for the thresholds along with the email Id which will get the alerts if the threshold was breached.
2. '/setminmax': The form submitted from /minmax will be a post request on '/setminmax'. This will then configure the values in .env file and os.environ.
3. '/showminmax': This api is used to display the current values of min and max.
4. '/api/prices/<coin>' : This api is used to get the price of a coin for a given day. The 'coin' here, is configurable. The offsets and limits are applied here on the result of the query and accordingly the result is returned
  
  
***** Wasnt able to dockerize this as was not able to spare much time for it. Also, the experience that I have on docker was not enough to dockerize the project easily.***********
  
