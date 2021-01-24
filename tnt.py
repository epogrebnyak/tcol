import nest_asyncio
nest_asyncio.apply()

import twint

# Configure
c = twint.Config()
c.Username = "PogrebnyakE"
c.Search = "CI"
c.Store_object = True

# Run
twint.run.Search(c)
#df = twint.storage.panda.Tweets_df
tweets = twint.output.tweets_list