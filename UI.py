"""
Simple User Interface
"""
from movielens import *
from sklearn.cluster import KMeans

import numpy as np
import pickle
import random
import sys
import time
import os.path

user = []
item = []

d = Dataset()
d.load_users("data/u.user", user)
d.load_items("data/u.item", item)

n_users = len(user)
n_items = len(item)

utility_matrix = pickle.load( open("utility_matrix.pkl", "rb") )

# Find the average rating for each user and stores it in the user's object
for i in range(0, n_users):
    x = utility_matrix[i]
    user[i].avg_r = sum(a for a in x if a > 0) / sum(a > 0 for a in x)

# Find the Pearson Correlation Similarity Measure between two users
def pcs(x, y, ut):
    num = 0
    den1 = 0
    den2 = 0
    A = ut[x - 1]
    B = ut[y - 1]
    num = sum((a - user[x - 1].avg_r) * (b - user[y - 1].avg_r) for a, b in zip(A, B) if a > 0 and b > 0)
    den1 = sum((a - user[x - 1].avg_r) ** 2 for a in A if a > 0)
    den2 = sum((b - user[y - 1].avg_r) ** 2 for b in B if b > 0)
    den = (den1 ** 0.5) * (den2 ** 0.5)
    if den == 0:
        return 0
    else:
        return num / den

# Perform clustering on items
movie_genre = []
for movie in item:
    movie_genre.append([movie.unknown, movie.action, movie.adventure, movie.animation, movie.childrens, movie.comedy,
                        movie.crime, movie.documentary, movie.drama, movie.fantasy, movie.film_noir, movie.horror,
                        movie.musical, movie.mystery, movie.romance, movie.sci_fi, movie.thriller, movie.war, movie.western])
movie_genre = np.array(movie_genre)

with open("cluster.pkl","r") as fp:
    cluster=pickle.load(fp)

ask = random.sample(item, 100)

username=raw_input("Enter username")
if (os.path.exists(username+".pkl")):
    print "Old User"
    flag=True
    o=pickle.load(open(username+".pkl","rb"))
    avg_ratings=o.avg_ratings
    demographics=o.demographics
    pcs_matrix=o.pcs
else:
    print "New User"
    flag=False
    avg_ratings = np.zeros(19)
    demographics= User(944, 21, 'M', 'student', 575025)
    pcs_matrix = np.zeros(n_users)

print "Please rate the following movies (1-5):\nFill in 0 if you have not seen it:"
k=0
for movie in ask:
    print movie.title + ": "
    a = int(input())
    if a==0:
        continue
    if avg_ratings[cluster.labels_[movie.id - 1]] != 0:
        avg_ratings[cluster.labels_[movie.id - 1]] = (avg_ratings[cluster.labels_[movie.id - 1]] + a) / 2
    else:
        avg_ratings[cluster.labels_[movie.id - 1]] = a
    k=k+1
    if k==10:
        break

utility_new = np.vstack((utility_matrix, avg_ratings))

user.append(demographics)

print "Finding users which have similar preferences."
for i in range(0, n_users + 1):
    if i != 943:
        pcs_matrix[i] = pcs(944, i + 1, utility_new)

user_index = []
for i in user:
    user_index.append(i.id - 1)
user_index = user_index[:943]
user_index = np.array(user_index)

top_5 = [x for (y,x) in sorted(zip(pcs_matrix, user_index), key=lambda pair: pair[0], reverse=True)]
top_5 = top_5[:5]

top_5_genre = []

for i in range(0, 5):
    maxi = 0
    maxe = 0
    for j in range(0, 19):
        if maxe < utility_matrix[top_5[i]][j]:
            maxe = utility_matrix[top_5[i]][j]
            maxi = j
    top_5_genre.append(maxi)

# print "Movie genres you'd like:"
# for i in top_5_genre:
#     if i == 0:
#         print "unknown"
#     elif i == 1:
#         print "action"
#     elif i == 2:
#         print "adventure"
#     elif i == 3:
#         print "animation"
#     elif i == 4:
#         print "childrens"
#     elif i == 5:
#         print "comedy"
#     elif i == 6:
#         print "crime"
#     elif i == 7:
#         print "documentary"
#     elif i == 8:
#         print "drama"
#     elif i == 9:
#         print "fantasy"
#     elif i == 10:
#         print "film_noir"
#     elif i == 11:
#         print "horror"
#     elif i == 12:
#         print "musical"
#     elif i == 13:
#         print "mystery"
#     elif i == 14:
#         print "romance"
#     elif i == 15:
#         print "science fiction"
#     elif i == 16:
#         print "thriller"
#     elif i == 17:
#         print "war"
#     else:
#         print "western"

enc=[]
for i in range(20):
    flag=False
    for j in top_5_genre:
        if i==j:
            flag=True
            break
    if flag==True:
        enc.append(1)
    else:
        enc.append(0)

print enc
loc=[]
k=0
for i in movie_genre:
    c=0
    for (a,b) in zip(enc,i):
        if a==b:
            c+=1
    if c>20-len(set(top_5_genre)):
        loc.append(k)
    k=k+1

print "Some recommendations : "
print loc
for i in range(len(loc)):
    print loc[i], item[loc[i]].title, movie_genre[loc[i]]

obj=NewUser(username, avg_ratings, demographics, pcs_matrix)
pickle.dump(obj, open(username+".pkl", "wb"))
