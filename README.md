# Web_Crawler

Implemented a web crawler that gathers data from a fake social networking website - http://cs5700sp16.ccs.neu.edu/
The software will first download the fake website, then it will parse the HTML and locate all hyperlinks (i.e. anchor tags) embedded in the page. 
The crawler then downloads all the HTML pages specified by the URLs on the homepage, and parses them looking for more hyperlinks. This process continues until all of the pages on website are downloaded and parsed.
