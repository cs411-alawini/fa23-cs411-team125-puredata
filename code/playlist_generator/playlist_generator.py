#!/usr/bin/env python
# coding: utf-8

# imports

import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd
import random
from sklearn.cluster import KMeans
from sqlalchemy import Integer, String, Float
import os
from google.cloud.sql.connector import Connector, IPTypes
import pymysql
import sqlalchemy
 
# connecting with GCP

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of SQL Server.

    Uses the Cloud SQL Python Connector package.
    """
    
    pool = sqlalchemy.create_engine("mysql+pymysql://<user>:<password>@<gcp-sql-instance-ip>/<db>")
    
    return pool
 
# Kmeans helper

def kMeans_init_centroids(X, K):
    rand_idx = np.random.permutation(X.shape[0])
    init_centroids = X[rand_idx[:K]]
    return np.array(init_centroids)
 
# Kmeans helper

def assigning_points_to_centroids(x,centroids):
    m,n = x.shape
    k = centroids.shape[0]
    index = []
    for i in range(m):
        distance = []
        for j in range(k):
            distance.append(np.linalg.norm(x[i]-centroids[j]))
        index.append(np.argmin(distance))
    return np.array(index)
 
# Kmeans helper

def recomputing_centroids(x,index,k):
    n = x.shape[1]
    new_centroids = []
    for j in range(k):
        points_related_to_cluster_j = x[index == j]
        new_centroids.append(np.mean(points_related_to_cluster_j, axis = 0)) 
    return np.array(new_centroids)
 
# Kmeans helper

def run_kMeans(X, initial_centroids, max_iters):
    k = initial_centroids.shape[0]
    z = initial_centroids
    for i in range(max_iters):
        indx = assigning_points_to_centroids(X, z)
        centroids = recomputing_centroids(X,indx,k)
        z = centroids
        if i%5 == 0:
            print('iteration{}/{} ====>{} \n'.format(i,max_iters,list(z)))
    return np.array(centroids),np.array(indx)
 
# GCP connection object 

conn = connect_with_connector()
 
# read song table from GCP

song = pd.read_sql("select * from song", conn)
 
# Grouping data by gener then count track_id in each group
df0 = pd.DataFrame(song.groupby(song["song_genre"]).count()["id"]).reset_index()
#sorting values in
df0 = df0.sort_values(by="id",ascending=False)
 
# Encoding genres numerically

genre_ids = [i for i in range(1,115)]
random.shuffle(genre_ids)

genre_mapping = {}
all_genres = list(data['track_genre'].unique())

for i in range(len(all_genres)):
    genre_mapping[all_genres[i]] = genre_ids[i]

print(genre_mapping)
    
 
# Map song genre to numerical values

song["genre"] = song["song_genre"].str.lower().map(genre_mapping)
 
song.columns
 
df1 = song.drop(columns=['album_name', 'song_genre', 'artist', 'song_name', 'id', 'key', "time_signature"])
df1
 
#data preprocessing 

df1.loc[df1["mode"] == "Major" ,"mode"] = 1
df1.loc[df1["mode"] == "Minor" ,"mode"] = 0
x = np.array(df1)
 
#scaling features 

df1["popularity"] = df1["popularity"] / max(df1["popularity"])
df1["duration_ms"] = df1["duration_ms"] /max(df1["duration_ms"])
df1["tempo"] = df1["tempo"] /max(df1["tempo"])
df1["loudness"] = df1["loudness"] /max(df1["loudness"])
 
# Identify ideal clusters

wcss = []
for i in range(1,16):
    kmeans = KMeans(i)
    kmeans.fit(x)
    wcss.append(kmeans.inertia_)
 
plt.figure(dpi = 200)
plt.plot(np.arange(1,16),wcss,marker = "H",color = "r")
plt.xlabel("No.of_clusters")
plt.ylabel("WCSS")

plt.grid()
plt.show()
 
# Initialise K means centroids

initial_centroids = kMeans_init_centroids(x, 15)
print('initial centroids ====>\n{} \n'.format(initial_centroids))
 
centroids,idx = run_kMeans(x, initial_centroids,15)
 
# Kmeans results

generated_playlists = pd.DataFrame()

for i in range(20):
    x = pd.DataFrame(song.iloc[idx == i ] )
    x.drop_duplicates(keep='first', inplace=True)
    x["playlist_no"] = i
    x = x.nlargest(20, 'popularity')
    generated_playlists = pd.concat((generated_playlists,x))
 
generated_playlists[generated_playlists["playlist_no"] == 0]
 
# Assign dtypes to store data back to MySQL

sql_dtypes = {
   'id': String(200), 'artist': String(200) , 'album_name': String(200), 'song_name': String(200), 'popularity': Integer, 'explicit': Integer,
       'key': Integer, 'mode': Integer, 'time_signature': Integer, 'song_genre': String(200), 'genre': Integer, 'playlist_no': Integer,
    'acousticness': Float,
 'danceability': Float,
 'duration_ms': Integer,
 'energy': Float,
 'instrumentalness': Float,
 'liveness': Float,
 'loudness': Float,
 'speechiness': Float,
 'tempo': Float,
 'valence': Float
}  
 
# Writing data back to MySQL

generated_playlists.to_sql("curated_playlists", conn, dtype = sql_dtypes, index=False, if_exists='replace')

