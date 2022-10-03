#!/usr/bin/env python
# coding: utf-8

# **Netflix - Story telling with data**
# 
# Loading libraries

# In[1]:


# Numpy and Pandas libraries
import numpy as np
import pandas as pd

# Visualization libraries
#import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

import warnings
warnings.filterwarnings('ignore')


# # Loading the dataset and some EDA

# In[2]:


movies = pd.read_csv('../../datasets/netflix_titles.csv')
movies.head()


# Columns `director`, `cast`, `country` and `listed_in` contain nested data.

# In[3]:


movies.info()


# There are some missing values in some columns and `date_added` is an object type but should be datetime

# In[4]:


print("The shape of the dataset is", movies.shape[0], "rows and ", movies.shape[1], "columns.")


# In[5]:


movies.duplicated().sum()


# There are no duplicates

# In[6]:


movies.show_id.nunique()


# In[7]:


movies.description.nunique()


# `show_id` and `description` are both unique or almost unique to each row and so are not useful for visualisation. I will drop them.

# In[8]:


movies = movies.drop(['show_id', 'description'], axis=1)


# Dealing with missing values

# In[9]:


movies.isnull().sum() #missing values in numbers


# In[10]:


round(movies.isnull().sum() / movies.shape[0],4) * 100 #missing values as a percentage


# `director`, `cast`, `country` have a lot of null data.
# 
# We are going to fill them with "Unknown" for now in order to retain the records but will filter them out when necessary afterwards.
# 
# `date_added`, `rating`, `duration` all have less than 1% of missing data. We are going to fill them with the mode.

# In[11]:


movies["director"] = movies["director"].fillna("Unknown")
movies["cast"] = movies["cast"].fillna("Unknown")
movies["country"] = movies["country"].fillna("Unknown")


# In[12]:


columns_mode = ['date_added', 'rating', 'duration']
for i in columns_mode:
    mode = movies[i].mode()
    print(f"{i} mode is : {mode}%")
    print('---------------------------')


# In[13]:


movies.date_added = movies.date_added.fillna(movies.date_added.mode()[0])
movies.rating = movies.rating.fillna(movies.rating.mode()[0])
movies.duration = movies.duration.fillna(movies.duration.mode()[0])


# In[14]:


movies.isnull().sum()


# In[15]:


movies.rating.unique()


# In[16]:


movies.groupby(['type', 'rating']).count()['title']


# Some of the values in rating column look like they belong to the duration column. I will move them over.

# In[17]:


movies.loc[movies.rating.str.contains('min'),'rating']


# In[18]:


movies.loc[5541,:]


# In[19]:


movies.loc[movies.rating.str.contains('min'),'duration'] = movies.loc[movies.rating.str.contains('min'),'rating']
movies.loc[movies.rating.str.contains('min'), 'rating'] = movies.rating.mode()[0]


# In[20]:


movies.loc[5541,:]


# In[21]:


movies.isnull().sum()


# We have no more missing values.

# In[22]:


movies.date_added.dtype


# `date_added` is currently an object, changing its type to dataframe will give more flexibility to this variable.

# In[23]:


movies["date_added"] = pd.to_datetime(movies['date_added'])


# In[24]:


movies.info()


# I am extracting some more variables from the datetime, to allow more flexibility when visualising the data.

# In[25]:


movies['year_added'] = movies['date_added'].dt.year
movies['month_added'] = movies['date_added'].dt.month_name()
movies['day_added'] = movies['date_added'].dt.day_name()


# In[26]:


movies.head(3)


# In[27]:


print("The final shape of the dataset is", movies.shape[0], "rows and ", movies.shape[1], "columns.")


# In[28]:


movies.columns


# With the data cleaned up, let's ask some questions and find out the answers.

# # What type of content does Netflix have?

# In[29]:


movies.type.unique()


# We have two types: Movies and TV Shows
# 
# How many of each do we have? Are they evenly distributed?

# In[30]:


movies.type.value_counts()


# In[31]:


round(movies.type.value_counts(normalize=True)*100, 2)


# I will save this information in a separate variable for easier visualisation.

# In[32]:


count_types = movies.type.value_counts().reset_index()
count_types.columns = ['Type', 'Count']
count_types["% Count"] = round(count_types.Count/count_types.Count.sum()*100,2)
count_types


# Let's visualise the results.

# In[33]:


fig = px.bar(count_types, x = 'Type', y = 'Count',
            color= 'Type', title = 'Netflix content by type')
fig.show()


# In[34]:


fig = px.pie(count_types, values = 'Count', names='Type',
                  color= 'Type', title = 'Netflix content by type in percentages')

fig.show()


# **Conclusion:**
# 
# Just under 70% of all Netflix shows are movies, the remaining ones are TV Shows.

# # Where was the content produced?

# In[35]:


movies.country.nunique()


# We have 555 unique countries in the dataset, that's more than there are in reality. Let's look at them.

# In[36]:


movies.country.value_counts()


# In[37]:


round(movies.country.value_counts(normalize=True)*100, 1)


# The third most frequent country is "Unknown" which are the missing values we filled earlier. Let's filter them out now.

# In[38]:


countries_count = movies[movies.country != "Unknown"].country.value_counts()
countries_count


# Some movies were produced in more than one country. Let's zoom into the top 20 to see how much of the total dataset they are.

# In[39]:


tot = sum(countries_count)
top15 = sum(countries_count[:15]) 

print(f'All movies : {tot}')
print(f'Movies produced in top 15 countries : {top15}')
print(f'Percentage of movies produced in top 15 countries: {top15}/{tot} = {round(100 * top15/tot,2)} %')


# Top 15 countries constitute just over 70% of all movies. Let's create a new variable with the top 15 countries

# In[40]:


top15_country = countries_count.head(15)
top15_country


# In[41]:


top15_country = top15_country.reset_index()
top15_country.columns = ['Country', 'Count']
top15_country


# In[42]:


fig_bar = px.bar(top15_country, y = 'Count', 
                 x= 'Country', color= 'Country')
fig_bar.update_layout(title= 'Distribution of top 20 producer countries')
fig_bar.show()


# In[43]:


fig_pie = px.pie(top15_country, values = 'Count', names= 'Country')
fig_pie.update_layout(title= 'Distribution of top 20 producer countries')
fig_pie.show()


# **Conclusion:**
# 
# The United States produced the most movies followed by India. When zooming into top 15 producing countries The United States produced almost 50% of movies and India produced just under 17%. However, we need to remember that this set contains only 72.29 % of all data and that when the whole set was considered those percantages were lower, 32.6% and 12.5% respectivaly. We also need to remember that 7.6% were missing values.

# # How old is the content on Netflix?

# In[44]:


top15_list = top15_country.Country.tolist()
top15_list


# In[45]:


top15_df = movies.loc[movies.country.isin(top15_list)]
top15_df.head(3)


# In[46]:


fig = px.treemap(top15_df, path=['country', 'release_year'], title="Release year of content added to Netflix by top 15 countries")
fig.show()


# **Conclusion:**
# 
# Looking at the release years of movies produced by the top 15 countries it is clear that most of the content is very recent. Let's have a look at the data overall.

# In[47]:


fig = px.treemap(movies, path=['release_year'], title="Release year of Netflix content")
fig.show()


# **Conclusion:**
# 
# Overall, the vast majority of the content are recent productions (around 60% of the content was release in the last 6 years). We can also see a steady increase of content added year by year with a decline in 2021.

# # How much content was added each year?

# Movies

# In[48]:


all_movie = movies[movies["type"] == "Movie"]
all_movie.head(2)


# In[49]:


content_movie = all_movie['year_added'].value_counts().reset_index()
content_movie.columns = ['year_added', 'count_movies']
content_movie.head(2)


# In[50]:


content_movie = content_movie.sort_values(by= 'year_added')
content_movie


# In[51]:


fig = px.scatter(content_movie, x='year_added', y='count_movies')
fig.update_traces(mode="markers+lines")

fig.update_layout(title="[Movies] - Content added over the different years")
fig.show()


# TV Shows

# In[52]:


all_tvshow = movies[movies["type"] == "TV Show"]
all_tvshow.head(2)


# In[53]:


content_tvshow = all_tvshow['year_added'].value_counts().reset_index()
content_tvshow.columns = ['year_added', 'count_tvshows']
content_tvshow.head(2)


# In[54]:


content_tvshow = content_tvshow.sort_values(by= 'year_added')
content_tvshow


# In[55]:


fig = px.scatter(content_tvshow, x='year_added', y='count_tvshows') #, text='year_added' to be used for other variable not on the scale already
fig.update_traces(mode="markers+lines")
#fig.update_traces(textposition="bottom right") with the other above

fig.update_layout(title="[TV Shows] - Content added over the different years")
fig.show()


# Let's combine the two graphs in one to better see the difference.

# In[56]:


#content_all = pd.concat([content_movie, content_tvshow], on= 'year_added', axis=1)
content_all = content_movie.merge(content_tvshow, how= 'left', on= ['year_added'])
content_all.head(3)


# In[57]:


content_all['count_tvshows'] = content_all['count_tvshows'].fillna(0).astype('int64')
content_all


# In[58]:


fig = px.scatter(content_all, x='year_added', y=['count_movies', 'count_tvshows'])
fig.update_traces(mode="markers+lines")

fig.update_layout(title="[Movies] - Content added over the different years")
fig.show()


# **Conclusion:**
# 
#     From 2015 till 2019 there has been a significant increase in new content addition
#     The content addition has decreased in 2020 due to Covid but more drastically for movies than for TV shows
#     Movies were added in much larger pace than TV shows

# # In which month most content was added?

# In[59]:


fig, ax = plt.subplots(figsize=(14, 5))

ax = sns.countplot(x='month_added',
                   data=movies, hue='type', 
                   order=movies.month_added.value_counts().index, 
                  palette=["#B00710","#000000"])

ax.set_xlabel('Month', labelpad=14)
ax.set_ylabel('Number of Content', labelpad=14)
ax.set_title('Content added per month', pad=14)
plt.show()


# In[60]:


year_month_count = (
                    movies
                    .loc[:,['year_added', 'month_added']]
                    .value_counts()
                    .reset_index()
                    .rename(columns={0:'count'})
                    .pivot("month_added", "year_added", "count")
                    .fillna(0)
                    .apply(lambda x: x.astype('int'))
                )


# In[61]:


plt.figure(figsize=(18,8), dpi=200)
ax = sns.heatmap(year_month_count, annot=True, fmt="d", cmap='Reds')
ax.set_xlabel('Year', labelpad=14)
ax.set_ylabel('Month')
ax.set_title('Content added on Netflix monthly', pad=14)
plt.show()


# **Conclusion:**
#     
#     As per the bar chart July and December were the months in which most content was added.
#     However, the heatmap suggests that November could also be a month when most content was added but the result is skewed  by missing data for Nov 2021.
#     We do not have all the data for year 2021 as the last quarter is missing.

# # On which weekday most content was added?

# In[62]:


plt.figure(figsize=(12, 7))
ax = sns.countplot(x='day_added',data=movies, 
                   hue='type', 
                   order=movies.day_added.value_counts().sort_values().index, 
                   palette=["#B00710","#000000"])

ax.set_title('Content added per week day')
ax.set_xlabel('Day', labelpad=14)
ax.set_ylabel('Number of Content', labelpad=14)
ax.set_title('Content added on Netflix per week day', pad=14)
plt.show()


# **Conclusion:**
#     
#     Most content for both movies and TV shows was added on Fridays.

# # What is the most common duration of movies?

# In[63]:


movies[movies['duration'].str.contains('min')]['duration']


# In[64]:


movie_durations = movies[movies['duration'].str.contains('min')]['duration'].apply(lambda x: x.split()[0]).astype('int')


# In[65]:


movie_durations


# In[66]:


movie_durations.mean()


# In[67]:


movie_durations.median()


# In[68]:


movie_durations.mode()


# In[69]:


# Hist plot with KDE
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(25,9))
g = sns.histplot(movie_durations, kde=True, color="#7aa4c4", bins=50, ax = ax1)
ax1.set_title('Hist plot with KDE for Movie Duration')
g.set(xticks=np.arange(0, 350, 25))
g.axvline(x=movie_durations.mean(), color='red')

# Box plot
sns.boxplot(x=movie_durations, color="#7aa4c4", ax = ax2)
ax2.set_xticks(np.arange(0,350, 25))
ax2.set_xlabel('Duration', labelpad=14)
ax2.set_title('Box plot for Movies Durations', pad=14)
plt.show()


# **Conclusion:**
#     
#     The average duration is around 100 min.
#     The meadian and mode are slightly lover than average which means that more movies are shorter rather than longer than     average.

# # What are the most common genres?
# 
# The variable listed_in contains the genre of each movie or TV show. Let's have a look what they are.

# In[70]:


movies['listed_in'].value_counts()


# Some movies are listed in more than one category, we are going to split them to create a list.

# In[71]:


movies_listed = ", ".join(movies['listed_in']).split(", ") #this create a long list of categories, I will print only top 5
movies_listed[:5]


# Let's transform this list into a DataFrame.

# In[72]:


movies_listed = pd.DataFrame(movies_listed, columns= ['genre'])
movies_listed


# In[73]:


genre_counts_ = movies_listed.value_counts().reset_index()
genre_counts_.columns= ['genre', 'count']
genre_counts_


# Now we can see which categories have the most content. Let's visialise the results.

# In[74]:


fig_bar = px.bar(genre_counts_, x = 'count', y= 'genre', color= 'genre',
                 orientation='h')
fig_bar.update_layout(title= 'Distribution of the most frequent genres')

fig_bar.show()


# The plot is difficult to read. Let's zoom into top 5 and bottom 5 to see the most and least numerous categories.

# In[75]:


fig_bar = px.bar(genre_counts_.head(5), x = 'count', y= 'genre', color= 'genre', orientation='h')
fig_bar.update_layout(title= 'Distribution of the 5 most frequent genres')

fig_bar.show()


# In[76]:


fig_bar = px.bar(genre_counts_.tail(5), x = 'count', y= 'genre', color= 'genre', orientation='h')
fig_bar.update_layout(title= 'Distribution of the 5 most frequent genres')

fig_bar.show()


# **Conclusion:**
#     
#     The most common genres are International Movies followed by Dramas and Comedies.
#     The least common are TV Shows.

# # Who are the most popular directors?

# In[77]:


all_movie = movies[movies["type"] == "Movie"]


# In[78]:


director_count = all_movie.director.value_counts()
director_count


# Let's remove the "Unknown"

# In[79]:


director_count = all_movie[all_movie.director != "Unknown"].director.value_counts()
director_count


# In[80]:


director_count = director_count.reset_index()
director_count.columns = ['director', 'count']
director_count


# In[81]:


fig_bar = px.bar(director_count.iloc[:20,:], x = 'director', y= 'count',
                color= 'director')
fig_bar.update_layout(title= 'Distribution of the top directors')

fig_bar.show()


# **Conclusion**
# 
#     The most popular director is Rajiv Chilaka who is an Indian cartoon creator.
#     The second most popular pair of directors Raul Campos & Jan Suter followed by Suhas Kadav.
#     

# # Who is the most popular actor?

# In[82]:


movies_ = movies[movies.cast != "Unknown"]


# In[83]:


movies_.cast.unique()


# In[84]:


actors_listed = ", ".join(movies_['cast']).split(", ") #this creates a long list of all actors


# In[85]:


actors_listed = pd.DataFrame(actors_listed, columns= ['actor'])
actors_listed


# In[86]:


actors_listed = actors_listed.value_counts().reset_index()
actors_listed.columns= ['actor', 'count']
actors_listed


# In[87]:


fig_bar = px.bar(actors_listed.head(20), x = 'count', y= 'actor', color= 'actor', orientation='h')
fig_bar.update_layout(title= 'Distribution of the 20 popular actors')

fig_bar.show()


# **Conclusion**
# 
#     The most popular actor is Anupam Kher, followed by Shah Rukh Khan, both of them are indian actors
#     The third most popular is Julie Tejwani who is an Indian voice over artist.
