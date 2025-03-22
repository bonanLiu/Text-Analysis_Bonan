pip install -r requirements.txt

# Run the file in the following sequence
Part 1:

First, run Part01a_Comparision.py.
Then, run Part01b_bs.py.

Part 2:

Run Part02a_TF-IDF.py.
Next, run Part02b_TF-IDF_visual.py.
Finally, run Part02c_LDA.py.

# Part01

BeautifulSoup is faster and more efficient in terms of resource usage (CPU and RAM) compared to Selenium. Although both methods scraped the same number of articles with a 100% success rate, BeautifulSoup completed the task in less time and with lower system resource consumption. Selenium, while effective, takes significantly more time and uses more CPU and RAM.


# Part02
The LDA topic modeling analysis revealed 5 distinct topics across the 120 coffee articles, each with its own set of dominant words and phrases. Here is a summary of the findings:

Topic #1 focuses on the coffee industry, highlighting words related to packaging, brands, and supply chains. Key phrases such as coffee roaster, coffee review, and espresso blend suggest a strong emphasis on the broader coffee production and review process, especially within the Kona coffee region.

Topic #2 is centered around coffee farms and varieties, with a particular focus on Kona and processing methods. This topic emphasizes different coffee varieties, with phrases like coffee roaster, top coffee, and specialty coffee, indicating a strong connection to high-quality coffee types and roasting practices.

Topic #3 relates to coffee processing, particularly the natural processing method. The most prominent terms include fruit, method, and sample, reflecting a deeper look at the processing stages. Phrases such as green coffee and coffee review suggest a focus on specialty coffee and fair trade practices.

Topic #4 is focused on coffee blends and specialty coffees, with an emphasis on Ethiopian coffee and geisha varieties. The presence of terms like dark roast, green coffee, and processing methods suggests this topic is about high-end coffee blends and origins, specifically from Central America and Ethiopia.

Topic #5 revolves around espresso blends, roasting, and cold brew coffee. It highlights terms like espresso, dark roast, and cold brew, indicating a focus on various brewing methods. Phrases such as fair trade, black coffee, and rtd coffee emphasize the commercial and ethical aspects of coffee, particularly in the US market.

Distribution:
Topic #4 is the most dominant, covering 35% of the articles, reflecting its broad relevance across various coffee-related themes.

Topic #3 follows with 25%, focusing on coffee processing and methods.

Topic #5 is 15%, emphasizing specific brewing methods like espresso and cold brew.

Topic #1 and Topic #2 each account for 12.5%, with a focus on industry practices and farming.


