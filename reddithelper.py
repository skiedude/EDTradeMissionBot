import asyncpraw
import configparser


class RedditBase():
    """
    Create common objects needed for all reddit classes
    """
    def __init__(self):
        self.reddit = asyncpraw.Reddit()
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')


class RedditPost(RedditBase):
    """
    Reddit Post and Crosspost functionality
    Expects a title and body to be passed
    """
    def __init__(self, msg, mission_type) -> None:
        self.msg = {}
        self.msg['reddit_title'] = msg['rt']
        self.msg['reddit_body'] = msg['rb']
        self.mission_type = mission_type
        super().__init__()

    
    async def create_post(self):
        """
        Make a post to reddit with correct flair
        The config.ini should have multiple required values (see README)
        """
        main_subbreddit = await self.reddit.subreddit(self.config['REDDIT']['main_sr'])
        main_sub_flair = self.config['REDDIT']['main_sr_flair_sell'] \
            if self.mission_type.lower() == 'unloading' else self.config['REDDIT']['main_sr_flair_buy']

        
        main_submission = await main_subbreddit.submit(self.msg['reddit_title'], selftext=self.msg['reddit_body'], flair_id=main_sub_flair)
        main_submission = await self.reddit.submission(main_submission)

        return main_submission
    
    async def crosspost(self, main_submission):
        """
        With a submission object, crosspost it to other subreddits with correct flair
        """
        secondary_submissions = []
        if self.config['REDDIT'].get('secondary_srs', None):
            secondary_srs = [x.strip() for x in self.config['REDDIT']['secondary_srs'].split(',')]
            flair_type = self.config['REDDIT']['secondary_flairs_sell'] \
                if self.mission_type.lower() == 'unloading' else self.config['REDDIT']['secondary_flairs_buy']
            secondary_sub_flairs = [x.strip() for x in flair_type.split(',')]
        else:
            return None

        for sr,flair in zip(secondary_srs, secondary_sub_flairs):
            secondary_submission = await main_submission.crosspost(sr, flair_id=flair)
            secondary_submissions.append(await self.reddit.submission(secondary_submission))

        return secondary_submissions


class FlairFinder(RedditBase):
    def __init__(self, subreddit):
        self.subreddit = subreddit
        super().__init__()


    async def find_flairs(self):
        flairs = {}
        subreddit = await self.reddit.subreddit(self.subreddit)
        
        async for fd in subreddit.flair.link_templates.user_selectable():
            flairs[fd['flair_text']] = fd['flair_template_id']
        return flairs



# Process to get the flair IDs from any subreddit
#for template in reddit.subreddit("skiedude").flair.link_templates.user_selectable():
#    print(template)
