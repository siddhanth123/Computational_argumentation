import scrapy
from urllib.parse import urljoin

class QuotesSpider(scrapy.Spider):
	name = "debates" #should be unique


	def start_requests(self): #returns a list of requests
		urls = ['https://www.debate.org/opinions/?sort=popular']

		for url in urls:
			yield scrapy.Request(url = url, callback = self.parse) #here the callback function will be called by scrapy.Request method automatically

	def parse(self,response):
		hrefs = response.css('ul#opinions-list span.image-frame a.a-image-contain::attr(href)').getall()
		popular_hrefs = hrefs[0:5] #extracting the top 5 most popular debates

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

			print("here")
			print(debate_title_pro)
			# print("\n")
			# print("loop end\n")

		print(len(pro_arg_list))

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

		print(len(con_arg_list))
			# print(debate_title_con)
			# print("\n")
			# print("loop end\n")

		yield{
			'topic':topic,
			'category':category,
			'pro_arguments': pro_arg_list,
			'con_arguments': con_arg_list		
		}
