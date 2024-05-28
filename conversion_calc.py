import requests
import bs4
import os


class ConversionCalc:
	def __init__(self, time, event):
		self.time = time
		self.event = event


	def __repr__(self):
		return f"ConversionCalc({self.time}, {self.event})"


	def get_conversions(self):
		html = requests.get("https://www.milesplit.com/calc?time={}&event={}".format(self.time, self.event)).text
		soup = bs4.BeautifulSoup(html, "html.parser")

		result = soup.find("section", class_="conversion result")

		conversion_label = result.find("p")

		conversions = result.find_all("ul")
		conversion_arr = []

		for conversion in conversions:
			conversion_arr.append(conversion.li.text)


		return conversion_arr


	def console_interface(self):

		while True:
			print()
			print("{} for {} converts to...".format(self.time, self.event))
			print()

			for conversion in self.get_conversions():
				print(conversion)

			print()
			self.time = input("Input Time: ")
			self.event = input("Input Event: ")

			os.system("cls")