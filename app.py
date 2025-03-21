import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="IMDb 2024 Movie Analysis", layout="wide")

db_path = "imdb_movies.db"
conn = sqlite3.connect(db_path)
query = "SELECT * FROM movies"
df = pd.read_sql(query, conn)

df.rename(columns={
    "Movie Name": "title",
    "Genre": "genre",
    "Ratings": "rating",
    "Voting Counts": "votes",
    "Duration": "duration"
}, inplace=True)


df["genre"] = df["genre"].str.split(",")
df_exploded = df.explode("genre").reset_index(drop=True)

st.sidebar.header("Filter Movies")

all_genres = ["All"] + list(df_exploded["genre"].unique())
selected_genre = st.sidebar.multiselect("Select Genre", all_genres, default="All")

selected_rating = st.sidebar.slider("IMDb Rating", float(df["rating"].min()), 10.0, (7.0, 10.0))

min_duration = int(df["duration"].min())
max_duration = int(df["duration"].max())
selected_duration = st.sidebar.slider("Duration (Minutes)", min_duration, max_duration, (min_duration, max_duration))

selected_votes = st.sidebar.slider("Voting Counts", int(df["votes"].min()), int(df["votes"].max()), (10000, int(df["votes"].max())))

filtered_df = df[
    (df["rating"] >= selected_rating[0]) & (df["rating"] <= selected_rating[1]) &
    (df["votes"] >= selected_votes[0]) & (df["votes"] <= selected_votes[1]) &
    (df["duration"] >= selected_duration[0]) & (df["duration"] <= selected_duration[1])
]

if "All" not in selected_genre:
    filtered_df = filtered_df[
        filtered_df["genre"].apply(lambda x: any(g in x for g in selected_genre))
    ]

st.title("IMDb 2024 Movies - Data Analysis & Visualization")

st.write(f"### Filtered Dataset ({len(filtered_df)} Movies)")
st.dataframe(filtered_df[["title", "genre", "rating", "votes", "duration"]])


st.write("Top 10 Movies by Highest Voting Counts")
top_voted_movies = df.nlargest(10, "votes")

fig1 = px.bar(
    top_voted_movies,
    x="title",
    y="votes",
    color="rating",  
    title="Top 10 Movies by Highest Voting Counts (with Ratings)",
    labels={"votes": "Voting Counts", "rating": "Rating"},
    hover_data=["rating"]
)

fig1.update_layout(
    xaxis_title="Movie",
    yaxis_title="Voting Counts",
    coloraxis_colorbar=dict(title="Rating")
)

st.plotly_chart(fig1, use_container_width=True)

st.write("### Genre Distribution")
genre_counts = df_exploded["genre"].value_counts()
fig2 = px.bar(genre_counts, x=genre_counts.index, y=genre_counts.values, title="Genre Distribution")
st.plotly_chart(fig2, use_container_width=True)

# 3. Average Duration by Genre
st.write("### Average Duration by Genre")
avg_duration = df_exploded.groupby("genre")["duration"].mean().sort_values()
fig3 = px.bar(avg_duration, x=avg_duration.values, y=avg_duration.index, orientation="h", title="Average Duration by Genre")
st.plotly_chart(fig3, use_container_width=True)

# 4. Voting Trends by Genre
st.write("### Voting Trends by Genre")
avg_votes = df_exploded.groupby("genre")["votes"].mean()
fig4 = px.line(avg_votes, x=avg_votes.index, y=avg_votes.values, title="Voting Trends by Genre")
st.plotly_chart(fig4, use_container_width=True)

# 5. Rating Distribution
st.write("### Rating Distribution")
fig5, ax = plt.subplots()
sns.histplot(df["rating"], bins=20, kde=True, ax=ax)
ax.set_title("Rating Distribution")
st.pyplot(fig5)

# 6. Genre-Based Rating Leaders
st.write("### Genre-Based Rating Leaders")
rating_leaders = df_exploded.loc[df_exploded.groupby("genre")["rating"].idxmax()]
st.dataframe(rating_leaders[["genre", "title", "rating"]])

# 7. Top 10 Most Popular Genres by Voting
st.write("### Most Popular Genres by Voting")


top_genre_votes = df_exploded.groupby("genre")["votes"].sum().reset_index()
top_genre_votes = top_genre_votes.sort_values("votes", ascending=False).head(10)  # Top 10


fig7 = px.pie(
    top_genre_votes,
    names="genre",
    values="votes",
    title="Most Popular Genres by Voting",
    hole=0.3
)

fig7.update_traces(
    textinfo='percent+label',
    marker=dict(line=dict(color='#000000', width=1))
)

fig7.update_layout(
    title_font_size=18,
    title_font=dict(family="Arial", size=20, color="darkblue"),
    legend_title_text="Genres",
    legend=dict(x=0.8, y=0.95)
)

st.plotly_chart(fig7, use_container_width=True)



# 8. Duration Extremes
st.write("### Shortest & Longest Movies")
min_duration = df.nsmallest(1, "duration")
max_duration = df.nlargest(1, "duration")
st.dataframe(pd.concat([min_duration, max_duration])[["title", "duration"]])

# 9. Ratings by Genre 
st.write("### Ratings by Genre (Average IMDb Ratings by Genre)")

heatmap_data = df_exploded.pivot_table(index="genre", values="rating", aggfunc="mean").sort_values("rating", ascending=False)

fig9, ax = plt.subplots(figsize=(12, 8))

sns.heatmap(
    heatmap_data,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=heatmap_data.values.mean(),
    linewidths=1,
    linecolor="white",
    cbar_kws={'label': 'Average Rating'},
    ax=ax
)

ax.set_title("Average IMDb Ratings by Genre", fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel("Genre", fontsize=12)
ax.set_ylabel(" ", fontsize=12)  # Removing y-label for cleaner look
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)

st.pyplot(fig9)


# 10. Correlation Analysis
st.write("### Correlation Analysis: Ratings vs Votes")

try:
    import statsmodels.api as sm  

    fig10 = px.scatter(
        df,
        x="rating",
        y="votes",
        title="Correlation: Ratings vs Votes",
        trendline="ols",
        labels={"x": "IMDb Rating", "y": "Voting Counts"}
    )
    st.plotly_chart(fig10, use_container_width=True)

except ModuleNotFoundError:
    st.error("`statsmodels` is not installed. Run `pip install statsmodels` and restart the app.")
