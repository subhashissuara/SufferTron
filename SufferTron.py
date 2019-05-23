# ------------------------------------------
# Writtern by u/QuantumBrute
# ------------------------------------------

from psaw import PushshiftAPI
import praw
import sqlite3
import time
import re

# --------------------------------------------------------------------------------

subreddit_name = ' ' # Mention the subreddit that bot should work on
limitno = 30000 # Set the maximum number of posts to get in the given timeframe
end_epoch=int(time.time()) # Current time
x = 1 #int(input("Enter the number of days you want to search for:"))
start_epoch=int(end_epoch - (60*60*24*x)) # Current time - the amount you mention in seconds

#---------------------------------------------------------------------------------

print("Starting Bot...")

reddit = praw.Reddit(client_id= ' ',         
					 client_secret= ' ',
					 username= ' ',
					 password= ' ',
					 user_agent= 'Created by u/QuantumBrute') # Login to reddit API

api = PushshiftAPI() # Variable to use the PushShiftAPI
subreddit = reddit.subreddit(subreddit_name)

print("From: "+ str(start_epoch))
print("Till: "+ str(end_epoch))

print("Opening SQL databases...")
conn1 = sqlite3.connect('usernames_list.db') # Creates a connection object that represents usernames_list.db
conn2 = sqlite3.connect('nsfw_usernames_list.db') # Creates a connection object that represents nsfw_usernames_list.db
c1 = conn1.cursor()  # Creates first cursor object to perform SQL commands
c2 = conn2.cursor()  # Creates second cursor object to perform SQL commands
c1.execute('CREATE TABLE IF NOT EXISTS RemovedPostsUsernames(Usernames text)') # DB to store usernames; Creates a table 
conn1.commit() # Saves changes to database
c2.execute('CREATE TABLE IF NOT EXISTS RemovedPostsUsernames(Usernames text)') # DB to store nsfw_usernames; Creates a table 
conn2.commit() # Saves changes to database

print("Going through posts...\n")

def removed():
    result = list(api.search_submissions(after=start_epoch, 
                                        before=end_epoch,
                                        subreddit=subreddit,
                                        filter=['author','selftext', 'id'],
                                        limit=limitno)) # Gets the data with the parameters mentioned from PushShift and makes it into a list


    print("Total number of posts in given timeframe: " + str(len(result)))
    count = 0 # To count the number of removed posts; intitalized with 0
    count_nsfw = 0 # To count the number of removed nsfw posts; intitalized with 0
    post_ids = []

    for a in range(len(result)):
        post_ids.append(result[a].id) # Gathers the ids of all posts in given time frame

    post_ids_size = len(post_ids)
    mods = subreddit.moderator()
    
    print("\nAdding punishable users to databases...")
    print("\n")
    print("Searching for users in databases for punishment..\n")

    for b in range(post_ids_size):
        
        submission = reddit.submission(post_ids[b]) # Gets post using the post ID
        submission.comments.replace_more(limit=None)
        author = submission.author

        if submission.saved or author == None: # Skip read posts and innocent redditors
            continue

        flag = 0

        if submission.banned_by != None: # Post is banned by mods
            for comment in submission.comments.list():
                keyword = re.search("!NSFW", comment.body) # Special case of ban due to NSFW post
                if keyword and comment.author in mods:
                    submission.save()
                    print("Removed NSFW post found! Made by u/" + str(author))
                    print("Moderator responsible: u/" + submission.banned_by)
                    c2.execute('INSERT INTO RemovedPostsUsernames VALUES (?)', (str(author),)) # Inserts the usernames into the table 
                    conn2.commit() # Dont forget to save
                    count_nsfw += 1
                    flag = 1
                    database_nsfw = c2.execute('SELECT Usernames, COUNT(*) FROM RemovedPostsUsernames GROUP BY Usernames') # Get the table as we progress
                    for data_nsfw in database_nsfw: # To check the punishment of user in database
                        if data_nsfw[1] == 1:
                            subreddit.banned.add(author, duration = 3)
                            message = ("Banning u/" + data_nsfw[0] + " for 3 days") 
                            print(message)
                            print("\n")
                        if data_nsfw[1] == 2:
                            subreddit.banned.add(author, duration = 7)
                            message = ("Banning u/" + data_nsfw[0] + " for 7 days") 
                            print(message)
                            print("\n")
                        if data_nsfw[1] >= 3:
                            subreddit.banned.add(author)
                            message = ("Banning u/" + data_nsfw[0] + " permanently") 
                            print(message)
                            print("\n")
                    break
            if flag == 0:
                submission.save()
                print("Removed post found! Made by u/" + str(author))
                print("Moderator responsible: u/" + submission.banned_by)
                c1.execute('INSERT INTO RemovedPostsUsernames VALUES (?)', (str(author),)) # Inserts the usernames into the table 
                conn1.commit() # Dont forget to save
                count += 1
                database = c1.execute('SELECT Usernames, COUNT(*) FROM RemovedPostsUsernames GROUP BY Usernames') # Get the table as we progress
                for data in database: # To check the punishment of user in database
                    if data[1] == 1:
                        subreddit.banned.add(author, duration = 1)
                        message = ("Banning u/" + data[0] + " for 1 days") 
                        print(message)
                        print("\n")
                    if data[1] == 2:
                        subreddit.banned.add(author, duration = 3)
                        message = ("Banning u/" + data[0] + " for 3 days") 
                        print(message)
                        print("\n")
                    if data[1] == 3:
                        subreddit.banned.add(author, duration = 5)
                        message = ("Banning u/" + data[0] + " for 5 days") 
                        print(message)
                        print("\n")
                    if data[1] == 4:
                        subreddit.banned.add(author, duration = 7)
                        message = ("Banning u/" + data[0] + " for 7 days") 
                        print(message)
                        print("\n")
                    if data[1] >= 5:
                        subreddit.banned.add(author)
                        message = ("Banning u/" + data[0] + " permanently") 
                        print(message)
                        print("\n")
    
    print("Total number of removed posts added to database: " + str(count))
    print("Total number of removed nsfw posts added to database: " + str(count_nsfw))

    input("\nOperation completed succesfully! Press Enter to exit...")
    conn1.close()
    conn2.close()

if __name__ == "__main__": 
    removed() # To execute the function removed()
