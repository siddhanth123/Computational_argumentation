import scrapy
from urllib.parse import urljoin
import urllib

class QuotesSpider(scrapy.Spider):
	name = "debates" #should be unique


	def start_requests(self): #returns a list of requests
		urls = ['https://www.debate.org/opinions/?sort=popular']

		for url in urls:
			yield scrapy.Request(url = url, callback = self.parse) #here the callback function will be called by scrapy.Request method automatically

	def parse(self,response):
		hrefs = response.css('ul#opinions-list span.image-frame a.a-image-contain::attr(href)').getall()
		popular_hrefs = hrefs[0:1] #extracting the top 5 most popular debates

		for link in popular_hrefs:
			url = urljoin('https://www.debate.org',link)
			yield scrapy.Request(url = url, callback = self.parse_debate)


	def parse_debate(self,response):

		topic = response.css('span.q-title::text').get() #extract the topic name for the page
		category = response.css('div#breadcrumb a::text').getall()[2] #extract the category name. it is the 3rd element in the list returned by this code, hence [2]  

		print("here")
		print("topic:" + topic)
		print("\n")
		print("category:" + category)
		pro_arg_list = []
		con_arg_list = []

		for args in response.css('div#debate div#yes-arguments li.hasData'):
			# print("loop start\n")
			text_list_pro = args.css('p::text').getall() #returns a list of pro-text where each element is a part of the paragraph seperated by </br>
			debate_text_pro = "".join(text_list_pro)
			# print(debate_text_pro)

			title_list_pro = args.css('h2::text').getall()

			if not title_list_pro:
				title_list_pro = args.css('h2 a::text').getall()
			
			debate_title_pro = "".join(title_list_pro)

			pro_arg = dict()
			pro_arg['title'] = debate_title_pro
			pro_arg['body'] = debate_text_pro
			pro_arg_list.append(pro_arg)

			# print("here")
			# print(debate_title_pro)
			# print("\n")
			# print("loop end\n")

		# print(len(pro_arg_list))

		for args in response.css('div#debate div#no-arguments li.hasData'):
			# print("loop start\n")
			text_list_con = args.css('p::text').getall() #returns a list of con-text where each element is a part of the paragraph seperated by </br>
			debate_text_con = "".join(text_list_con)
			# print(debate_text_con)
			# print("\n")

			title_list_con = args.css('h2::text').getall()

			if not title_list_con:
				title_list_con = args.css('h2 a::text').getall()


			debate_title_con = "".join(title_list_con)

			con_arg = dict()
			con_arg['title'] = debate_title_con
			con_arg['body'] = debate_text_con
			con_arg_list.append(con_arg)

		# print(len(con_arg_list))

		url = 'https://www.debate.org/opinions/~services/opinions.asmx/GetDebateArgumentPage'

		headers = {
		    # "Connection": "keep-alive",
		    # "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"",
		    "Accept": "application/json, text/javascript, */*; q=0.01",
		    "X-Requested-With": "XMLHttpRequest",
		    # "sec-ch-ua-mobile": "?0",
		    # "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
		    "Content-Type": "application/json; charset=UTF-8",
		    "Origin": "https://www.debate.org",
		    # "Sec-Fetch-Site": "same-origin",
		    # "Sec-Fetch-Mode": "cors",
		    # "Sec-Fetch-Dest": "empty",
		    "Referer": "https://www.debate.org/opinions/kirk-will-always-be-better-than-picard",
		    # "Accept-Language": "en-US,en-IN;q=0.9,en;q=0.8,de-DE;q=0.7,de;q=0.6"
		}


		body = '{"debateId":"155D90B8-23AF-4AB5-889D-3D6AEC074752","pageNumber":99,"itemsPerPage":10,"ysort":5,"nsort":5}'


		yield scrapy.Request(url=url, method='POST', dont_filter=True, headers=headers, body=body, callback = self.parse_extra)
			# print(debate_title_con)
			# print("\n")
			# print("loop end\n")

		# yield{
		# 	'topic':topic,
		# 	'category':category,
		# 	'pro_arguments': pro_arg_list,
		# 	'con_arguments': con_arg_list		
		# }

	def parse_extra(self,response):
		print("here in extra parse")
		print("\n")
		print(response.body)
