"""
https://leetcode.com/problems/design-twitter/description/?envType=company&envId=google&favoriteSlug=google-thirty-days

Design a simplified version of Twitter where users can post tweets, follow/unfollow another user, and is able to see the 10 most recent tweets in the user's news feed.

Implement the Twitter class:

Twitter() Initializes your twitter object.
void postTweet(int userId, int tweetId) Composes a new tweet with ID tweetId by the user userId. Each call to this function will be made with a unique tweetId.
List<Integer> getNewsFeed(int userId) Retrieves the 10 most recent tweet IDs in the user's news feed. Each item in the news feed must be posted by users who the user followed or by the user themself. Tweets must be ordered from most recent to least recent.
void follow(int followerId, int followeeId) The user with ID followerId started following the user with ID followeeId.
void unfollow(int followerId, int followeeId) The user with ID followerId started unfollowing the user with ID followeeId.
 

Example 1:

Input
["Twitter", "postTweet", "getNewsFeed", "follow", "postTweet", "getNewsFeed", "unfollow", "getNewsFeed"]
[[], [1, 5], [1], [1, 2], [2, 6], [1], [1, 2], [1]]
Output
[null, null, [5], null, null, [6, 5], null, [5]]

Note: add dictionary to search in O(1)
      add sequenc number to sort the tweets based on its arrival time / tweet time.
      to fetch recent tweets i can use a doubled linkedlist but using a list also will works because list last element is the most recently posted tweet.( also we are using 
      sequence number whihch we can use to sort the tweets based on arrival time)

"""
class Twitter:
    # we need one dictionary to track follower 
    # and need an other dictionary of list to track feeds peruser.
    # while retrieving feeds we can take all follwer list and extract all feeds for individual id from feed dictionary.

    def __init__(self):
        self.feeds = DefaultDict(list)
        self.follower = DefaultDict(set)
        self.sequence = 1
        

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.feeds[userId].append((tweetId,self.sequence))
        self.sequence+=1

    def getNewsFeed(self, userId: int) -> List[int]:
        # get all follower list along with user id and extract last feeds from the feeds dictionary.
        all_follower = self.follower[userId]
        all_follower.add(userId)
        all_tweets = []
        for id in all_follower:
            print("all feeeds per id {} = {}".format(id, self.feeds[id]))
            all_tweets = self.feeds[id][max(0,len(self.feeds[id])-10):][::-1] + all_tweets
        all_tweets = [x[0] for x in sorted(all_tweets, key=lambda y: y[1],  reverse=True)]
        print(all_tweets[:10])
        return all_tweets[:10]
        

    def follow(self, followerId: int, followeeId: int) -> None:
        if followeeId not in self.follower[followerId]:
            self.follower[followerId].add(followeeId)
        

    def unfollow(self, followerId: int, followeeId: int) -> None:
        if followeeId in self.follower[followerId]:
            self.follower[followerId].remove(followeeId)
        


# Your Twitter object will be instantiated and called as such:
# obj = Twitter()
# obj.postTweet(userId,tweetId)
# param_2 = obj.getNewsFeed(userId)
# obj.follow(followerId,followeeId)
# obj.unfollow(followerId,followeeId)
