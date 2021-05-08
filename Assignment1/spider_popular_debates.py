import scrapy
from urllib.parse import urljoin
import urllib
import json
from inline_requests import inline_requests

class QuotesSpider(scrapy.Spider):
	name = "debate_crawler" #should be unique and is the name of the crawler


	def start_requests(self): #returns a list of requests
		urls = ['https://www.debate.org/opinions/?sort=popular'] #start url - url where the parsing starts

		for url in urls:
			yield scrapy.Request(url = url, callback = self.parse) #here the callback function will be called by scrapy.Request method automatically

	def parse(self,response):
		hrefs = response.css('ul#opinions-list span.image-frame a.a-image-contain::attr(href)').getall() #extracting the top 5 most popular debates
		popular_hrefs = hrefs[0:5]

		debate_id = response.css('li').xpath('@did').getall() # extracting debate IDs of the 5 most popular debates
		popular_debate_id = debate_id[0:5]

		for i in range(len(popular_hrefs)):
			url = urljoin('https://www.debate.org',popular_hrefs[i])
			request = scrapy.Request(url = url, callback = self.parse_debate, cb_kwargs = dict()) #scrape request and callback to parse_debate()
			request.cb_kwargs['debate_id'] = str(popular_debate_id[i]) #pass debateID to the parse_debate() method
			yield request


	@inline_requests
	def parse_debate(self,response,debate_id):

		debate_id = debate_id #capture the debateID of the debate

		topic = response.css('span.q-title::text').get() #extract the topic name for the page
		category = response.css('div#breadcrumb a::text').getall()[2] #extract the category name. it is the 3rd element in the list returned by this code, hence [2]  

		# generating two empty lists to store pro and con arguements
		pro_arg_list = [] 
		con_arg_list = []

		# loop through each Pro arguement
		for args in response.css('div#debate div#yes-arguments li.hasData'):
			
			text_list_pro = args.css('p::text').getall() #returns a list of pro-text where each element is a part of the paragraph seperated by </br>
			debate_text_pro = "".join(text_list_pro) #generate a string from the list

			title_list_pro = args.css('h2::text').getall() #capture the title of the arguement from <h2> tag when title is in text format

			if not title_list_pro: #if the title is a hyperlink, capture it from <a> tag
				title_list_pro = args.css('h2 a::text').getall()
			
			debate_title_pro = "".join(title_list_pro)

			# generate a dictionary object for pro arguement and keep appending the dict object to the pro_arg_list declared at Line40
			pro_arg = dict()
			pro_arg['title'] = debate_title_pro
			pro_arg['body'] = debate_text_pro
			pro_arg_list.append(pro_arg)


		# loop through each Con arguement
		for args in response.css('div#debate div#no-arguments li.hasData'):

			text_list_con = args.css('p::text').getall() #returns a list of con-text where each element is a part of the paragraph seperated by </br>
			debate_text_con = "".join(text_list_con) # generate a string from the list

			title_list_con = args.css('h2::text').getall() #capture title in text format from <h2>

			if not title_list_con: #capture title in hyperlink format from <a>

				title_list_con = args.css('h2 a::text').getall()

			debate_title_con = "".join(title_list_con)

			# generate a dictionary object for con arguement and keep appending the dict object to the con_arg_list declared at Line41
			con_arg = dict()
			con_arg['title'] = debate_title_con
			con_arg['body'] = debate_text_con
			con_arg_list.append(con_arg)

		
		# URL for the POST request for Page2 onwards until end of pages, obtained after clicking "Load More Arguements" in the front end

		url = 'https://www.debate.org/opinions/~services/opinions.asmx/GetDebateArgumentPage'

		# Headers for POST request for Page2 onwards until end of pages
		headers = {
		    "Accept": "application/json, text/javascript, */*; q=0.01",
		    "X-Requested-With": "XMLHttpRequest",
		    "Content-Type": "application/json; charset=UTF-8",
		    "Origin": "https://www.debate.org",
		    "Referer": "https://www.debate.org/opinions/kirk-will-always-be-better-than-picard",
		    "Accept-Language": "en-US,en-IN;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6"
		}

		headers["Referer"] = response.url #replace the Referer key value with the current debate URL

		# Body for POST request for Page2 onwards

		body_dict = {"debateId":"","pageNumber":2,"itemsPerPage":10,"ysort":5,"nsort":5}
		body_dict["debateId"] = debate_id #replace debateID key value with the current debateID

		page = 2 #initalise page number for "Load More Arguements"

		while(page != 0): #Loop to scrape all pages until there are pages

			body_dict["pageNumber"] = page #pass the current page number to body of the POST request
			body = str(body_dict)

			# inline POST request for scraping the further pages of a debate. Response captured  in JSON format.
			response_loadmore = yield scrapy.Request(url=url, method='POST', dont_filter=True, headers=headers, body=body)
			
			response_loadmore_json = json.loads(response_loadmore.text)
			response_loadmore_html = scrapy.Selector(text=response_loadmore_json['d'], type="html")  #creating a html object for scrapy

			response_yes_no = response_loadmore_json['d'] #fetch the html text containing pro and con args from response

			#split the string into 2 with {ddo.split} as the seperator. First half gives PRO args and second half gives CON args
			response_yes_no_list = response_yes_no.split(sep = '{ddo.split}', maxsplit = 1)

			# generate HTML objects from the string object for easy parsing
			response_yes_html = scrapy.Selector(text=response_yes_no_list[0], type="html") 
			response_no_html = scrapy.Selector(text=response_yes_no_list[1], type="html")


			if not response_loadmore_html.css('li.hasData').getall(): #check if the response page has data or not

				page = 0 #assign page to 0 in case there's no data since last page is reached. This will lead to termination of the while loop.

			else: # if page has data
							
				# check if yes arguements are present

				if response_yes_html.css('li.hasData').getall():

					for args in response_yes_html.css('li.hasData'): #iterate through all the PRO args
						
						text_list_pro_load = args.css('p::text').getall() #returns a list of pro-text where each element is a part of the paragraph seperated by </br>
						debate_text_pro_load = "".join(text_list_pro_load)

						title_list_pro_load = args.css('h2::text').getall() #extract title of the arguement in text format

						if not title_list_pro_load:
							title_list_pro_load = args.css('h2 a::text').getall() #extract title in hyperlink format
						
						debate_title_pro_load = "".join(title_list_pro_load)

						# create a dict object of each arguement and keep appending it to the pro_arg_list already created
						pro_arg_load = dict()
						pro_arg_load['title'] = debate_title_pro_load
						pro_arg_load['body'] = debate_text_pro_load
						pro_arg_list.append(pro_arg_load)

				# check if no arguements are present

				if response_no_html.css('li.hasData').getall():

					for args in response_no_html.css('li.hasData'): #iterate through all the CON args
						
						text_list_con_load = args.css('p::text').getall() #returns a list of pro-text where each element is a part of the paragraph seperated by </br>
						debate_text_con_load = "".join(text_list_con_load)

						title_list_con_load = args.css('h2::text').getall() # extract titles of the args in text format

						if not title_list_con_load:
							title_list_con_load = args.css('h2 a::text').getall() #extract titles of the args in hyperlink format
						
						debate_title_con_load = "".join(title_list_con_load)

						# create a dict object of each arguement and keep appending it to the con_arg_list already created
						con_arg_load = dict()
						con_arg_load['title'] = debate_title_con_load
						con_arg_load['body'] = debate_text_con_load
						con_arg_list.append(con_arg_load)									

				page = page + 1 #increment page number

		# yield the data in following JSON format
		yield{
			'topic':topic,
			'category':category,
			'pro_arguments': pro_arg_list,
			'con_arguments': con_arg_list		
		}
