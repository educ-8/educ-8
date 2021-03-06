from googlemaps import googlemaps
from instagram.client import InstagramAPI
from instagram.bind import InstagramAPIError
import tweepy
import facebook
import os
import ipdb

"""TODO:
6. create db objects for school, hashtag, post, school_hashtag join
"""

# TODO: Break each class definition into a separate file and update import statements as needed
class FBSearcher:
    """Creates a Facebook client and returns search results"""
    def __init__(self):
        self.client = facebook.GraphAPI(os.environ['EDUC8_FB_APP_ACCESS_TOKEN'])
    def get_lat_long(self, search_term):
        search_result = {}
        args = {'q': search_term, 'type':'place', 'category':'university'}
        places = self.client.request('search', args)

        result = places['data'][0]
        search_result['lat'] = result['location']['latitude']
        search_result['lng'] = result['location']['longitude']
        search_result['place_id'] = result['id']

        return search_result

class GMapsSearcher:
    """Creates a Gmaps client and returns search results"""
    def __init__(self):
        self.client = googlemaps.Client(key=os.environ['EDUC8_GMAPS'])
        self.search_results = []
    def get_lat_long(self, search_term):
        search_result = {}
        geocode_result = self.client.geocode(search_term)
        search_result['lat'] = geocode_result[0]['geometry']['location']['lat']
        search_result['lng'] = geocode_result[0]['geometry']['location']['lng']
        return search_result

class InstagramSearcher:
    """Creates an Instagram API client and returns search results"""
    def __init__(self):
        self.client = InstagramAPI(client_id=os.environ['EDUC8_IG_CLIENT_ID'], client_secret=os.environ['EDUC8_IG_CLIENT_SECRET'])
        self.search_results = []

    def get_ig_locations(self, lat, lng):
        return self.client.location_search(lat=lat, lng=lng)

    def search_all_locations(self, locations):
        for location in locations:
            try:
                results = self.client.location_recent_media(location_id = location.id)
                for media in results[0]:
                    result = {'source': 'Instagram'}
                    result['location_name'] = location.name
                    result['created'] = media.created_time
                    result['username'] = media.user.username
                    result['avatar'] = media.user.profile_picture
                    if media.caption:
                        result['caption'] = media.caption.text
                    else:
                        result['caption'] = ""
                    result['url'] = media.images['standard_resolution'].url
                    result['ig_shortcode'] = get_ig_shortcode(media.link) # TODO: this helper method is used by both IG and TwitterSearcher objects, how to make this work?
                    self.search_results.append(result)
            except InstagramAPIError as e:
                print e
            except Exception as ex:
                print ex

    def get_photo_url_from_shortcode(self, shortcode):
        ig_result = self.client.media_shortcode(shortcode)
        return ig_result.images['standard_resolution'].url

class TwitterSearcher:
    """Creates a Twitter API client and returns search results"""
    def __init__(self):
        self.client = self.open_client()
        self.search_results = []

    def open_client(self):
        auth = tweepy.OAuthHandler(os.environ['EDUC8_TWITTER_CONSUMER_KEY'], os.environ['EDUC8_TWITTER_CONSUMER_SECRET'])
        auth.set_access_token(os.environ['EDUC8_TWITTER_ACCESS_TOKEN'], os.environ['EDUC8_TWITTER_ACCESS_TOKEN_SECRET'])
        return tweepy.API(auth)

    def search_by_geocode(self, geocode):
        tweets = self.client.search(geocode=geocode, rpp=100, show_user=True)
        for tweet in tweets:
            result = {'source': 'Twitter'}
            result['post_id'] = tweet.id_str
            if hasattr(tweet, 'location'):
                result['location_name'] = tweet.location
            else:
                result['location_name'] = ""
            result['created'] = tweet.created_at
            result['username'] = tweet.user.screen_name
            result['avatar'] = tweet.user.profile_image_url_https
            result['caption'] = tweet.text
            if 'media' in tweet.entities:
                result['url'] = tweet.entities['media'][0]['media_url_https']
            if 'hashtags' in tweet.entities and len(tweet.entities['hashtags']) > 0:
                result['hashtags'] = [tag['text'] for tag in tweet.entities['hashtags']]
            # filter out spam job / career tweets
            if 'jobs' not in tweet.user.name.lower() and \
            'careers' not in tweet.user.name.lower():
                self.search_results.append(result)


# TODO: Create a SchoolSearchManager object that handles the entire search and returns the result to the front end
def get_photos(search_term):
    # create list of terms to try in case user didn't enter full name of school
    original_search_term = search_term
    search_term = search_term.lower()
    search_terms_to_try = resolve_search_term(search_term)

    # get lat-long from facebook search api -- we can get school address, city town etc. too
    fb_api = FBSearcher()
    for current_search_term in search_terms_to_try:
        lat_lng_result = fb_api.get_lat_long(search_term = current_search_term)
        if lat_lng_result.get('lat') != None and lat_lng_result.get('lng') != None:
            lat = lat_lng_result['lat']
            lng = lat_lng_result['lng']
            break

    #error checking -- lat_lng_result would only be empty if we exhausted all options
    if lat_lng_result.get('lat') == None or lat_lng_result.get('lng') == None:
        message = "Sorry, I couldn't find any results for %s." % original_search_term
        error_result = {'hasError': True, 'message': message}
        return error_result

    success_results = []

    ig_api = InstagramSearcher()
    locations = ig_api.get_ig_locations(lat=lat, lng=lng)
    ig_api.search_all_locations(locations=locations)
    success_results += ig_api.search_results

    tw_api = TwitterSearcher()
    geocode = "{0},{1},1km".format(lat,lng)
    tw_api.search_by_geocode(geocode=geocode)
    success_results += tw_api.search_results

    sorted_results = sorted(success_results, key=lambda r: r['created'], reverse=True)
    payload = {"location": {"lat": lat, "lng": lng}, "posts": sorted_results}
    return payload

def get_ig_shortcode(link_url):
    start = link_url.index('/p')
    shortcode = link_url[start + 3: -1]
    return shortcode

def translate_short_name(search_term):
    # just a start; eventually this will be a separate file (much larger) loaded into memory
    short_names = {
        'berkeley': 'university of california, berkeley',
        'madison': 'university of wisconsin-madison',
        'wisconsin': 'university of wisconsin-madison',
        'university of wisconsin': 'university of wisconsin-madison',
        'umass': 'university of massachusetts amherst',
        'illinois': 'university of illinois at urbana-champaign',
        'university of illinois': 'university of illinois at urbana-champaign',
        'pratt': 'pratt institute',
        'colorado': 'university of colorado boulder',
        'julliard': 'the julliard school of performing arts and dance'
    }
    if search_term in short_names.keys():
        return short_names[search_term]
    else:
        return search_term

# TODO: Method that translates abbreviations like UC Davis = University of California at Davis
def resolve_search_term(search_term):
    translated_short_name = translate_short_name(search_term)
    match_words = ['university', 'college', 'institute', 'school']

    if search_term != translated_short_name:
        # use the translated value if there is one
        search_terms_to_try = [translated_short_name]
    elif len([word for word in match_words if word in search_term]) > 0:
        search_terms_to_try = [search_term]
    else:
        search_terms_to_try = [
            'university of ' + search_term,
            search_term + ' university',
            search_term + ' college',
            ]
    return search_terms_to_try
