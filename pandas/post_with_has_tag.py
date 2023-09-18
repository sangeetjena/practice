# Learning: group, filter, row update, loc, transform

# * Members can share their thoughts on LinkedIn through posts.
# * Posts may contain text, image, video, hashtag etc.
# * Posts can receive engagement through like and comment.
# * We like to understand if adding a hashtag to a post increases its likelihood of receiving more like/comments.
# * Hypothesis is posts with hashtag, results in more engagement.
# * How could we provide evidence to support or refute this hypothesis?

# postDataFrame:
# +--------+------+--------+-------+--------+-------------------+
# | date | postId | authorId | hasText | hasImage | hashtag |
# +--------+------+--------+-------+--------+-------------------+
# | 20190102 | 8533 | 1763 | true | true | [  # ecommerce, #data]|
#   | 20190105 | 5896 | 6957 | false | true | [] |
#   | 20190211 | 6941 | 2189 | true | false | [] |
#   | 20190212 | 3694 | 1763 | true | true | [  # dataScience]|
#       +--------+------+--------+-------+--------+-------------------+
#
#       engagementDataFrame:
# +--------+--------------+--------+--------------+
# | date | originalPostId | viewerId | engagementType |
# +--------+--------------+--------+--------------+
# | 20190103 | 8533 | 5846 | Like |
# | 20190103 | 8533 | 7841 | Comment |
# | 20190105 | 8533 | 4562 | Like |
# | 20190215 | 3694 | 1562 | Like |
# | 20190213 | 6941 | 5846 | Like |
# +--------+--------------+--------+--------------+

import pandas as pd

engagement_df = pd.DataFrame({"date": [20190103,
                                       20190103,
                                       20190105,
                                       20190215,
                                       20190213],
                              "orginalPostId": [8533,
                                                8533,
                                                8533,
                                                3694,
                                                6941],
                              "viewerId": [5846,
                                           7841,
                                           4562,
                                           1562,
                                           5846],
                              "engagementType": ["Like",
                                                 "Comment",
                                                 "Like",
                                                 "Like",
                                                 "Like"]})

post_df = pd.DataFrame({"date": [20190102,
                                 20190105,
                                 20190211,
                                 20190212],
                        "postId": [8533,
                                   5896,
                                   6941,
                                   3694],
                        "authorId": [1763,
                                     6957,
                                     2189,
                                     1763],
                        "hasText": [True,
                                    False,
                                    True,
                                    True],
                        "hasImage": [True,
                                     True,
                                     False,
                                     True],
                        "hashtag": [["# ecommerce", "#data"], [], [], ["# dataScience"]]})
post_df["hasTag"] = post_df.apply(lambda x: True if len(x["hashtag"]) > 0 else False, axis=1)
post_eng_df = post_df.merge(engagement_df, left_on="postId", right_on="orginalPostId", how="inner")
post_eng_df["hasTag"].fillna(False, inplace=True)
total_non_hash_post_cnt = post_df[post_df["hasTag"] == False].__len__()
total_hash_post_cnt = post_df[post_df["hasTag"] == True].__len__()
grp_posts_df = post_eng_df.groupby(["hasTag"]).aggregate({"hasTag": ["count"]}).reset_index()
grp_posts_df.columns = ["hasTag","count"]
print(post_eng_df)
grp_posts_df.loc[grp_posts_df["hasTag"] == False, "percent"] = grp_posts_df[grp_posts_df["hasTag"] == False].apply(lambda x: x["count"]/total_non_hash_post_cnt *100, axis=1)
grp_posts_df.loc[grp_posts_df["hasTag"] == True,"percent"] = grp_posts_df[grp_posts_df["hasTag"] == True].apply(lambda x: x["count"]/total_hash_post_cnt *100, axis=1)
print(grp_posts_df)
