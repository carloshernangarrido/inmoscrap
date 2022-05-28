# inmoscrap
Web application that scraps 'inmoclick.com.ar' and find low-price opportunities.

This is a Python script that identifies the most profitable lot purchase opportunities.
For this, the script does web scraping of the website inmoclick.com.ar. It searches for all the lots for sale in the province of Mendoza (Argentina), clusters them geographically and then segments them according to relative price (US$ / m^2). This generates groups where the lots are comparable. 
Then, it performs a statistical analysis within each group among lots of similar surface. The main statistics are the minimum price and its median. The expected rent of a purchase transaction can be estimated as the difference between them. This is used to rank them in order to identify the most profitable buying opportunities.
Finally, it shows the lots in the group where the best opportunities are on Google Maps with markers of size proportional to the relative price.
