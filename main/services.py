from googlemaps import googlemaps
from instagram.client import InstagramAPI
import tweepy
import facebook
import os
import ipdb

# TODO: Break each class definition into a separate file and update import statements as needed
class FBSearcher:
    """Creates a Facebook client and returns search results"""
    def __init__(self):
        self.client = facebook.GraphAPI(os.environ['EDUC8_FB_APP_ACCESS_TOKEN'])
    def get_lat_long(self, search_term):
        search_result = {}
        args = {'q': search_term, 'type':'place', 'category':'university'}
        places = self.client.request('search', args)
        for place in places['data']:
            if place['name'].lower() == search_term.lower():
                search_result['lat'] = place['location']['latitude']
                search_result['lng'] = place['location']['longitude']
                search_result['place_id'] = place['id']
                break
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
        self.ig_shortcodes = []
    def get_ig_locations(self, lat, lng):
        return self.client.location_search(lat=lat, lng=lng)
    def search_all_locations(self, locations):
        for location in locations:
            results = self.client.location_recent_media(location_id = location.id)
            for media in results[0]:
                result = {}
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
                self.ig_shortcodes.append(result['ig_shortcode'])
                self.search_results.append(result)

class TwitterSearcher:
    """Creates a Twitter API client and returns search results"""
    def __init__(self, old_ig_shortcodes = []):
        self.client = self.open_client()
        self.search_results = []
        self.old_ig_shortcodes = old_ig_shortcodes
        self.new_ig_shortcodes = []

    def open_client(self):
        auth = tweepy.OAuthHandler(os.environ['EDUC8_TWITTER_CONSUMER_KEY'], os.environ['EDUC8_TWITTER_CONSUMER_SECRET'])
        auth.set_access_token(os.environ['EDUC8_TWITTER_ACCESS_TOKEN'], os.environ['EDUC8_TWITTER_ACCESS_TOKEN_SECRET'])
        return tweepy.API(auth)

    def search_by_geocode(self, geocode):
        tweets = self.client.search(geocode=geocode, rpp=100, show_user=True)
        for tweet in tweets:
            result = {}
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
                result['ig_shortcode'] = None
            elif tweet.source == "Instagram":
                link_url = [url['expanded_url'] for url in tweet.entities['urls'] if 'instagram' in url['expanded_url']][0]
                result['ig_shortcode'] = get_ig_shortcode(link_url)    
                if result['ig_shortcode'] not in self.old_ig_shortcodes and not len(result['ig_shortcode']) > 10:                    
                    # shortcodes > 10 characters are for private accounts; IG won't return them
                    # go to Instagram for the url
                    try:
                        ig_result = InstagramSearcher().client.media_shortcode(result['ig_shortcode'])
                        result['url'] = ig_result.images['standard_resolution'].url
                    except:
                        # catch any other IG errors
                        result['exclude'] = True
                else:
                    result['exclude'] = True        
            else:
                result['ig_shortcode'] = None
                result['exclude'] = True
            if not 'exclude' in result.keys():
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
    if lat_lng_result.get('lat') == None:
        message = "Sorry, I couldn't find any results for %s." % original_search_term
        error_result = {'hasError': True, 'message': message}
        return error_result

    success_results = []
    ig_shortcodes = []

    ig_api = InstagramSearcher()
    locations = ig_api.get_ig_locations(lat=lat, lng=lng)
    ig_api.search_all_locations(locations=locations)
    success_results += ig_api.search_results
    ig_shortcodes += ig_api.ig_shortcodes

    tw_api = TwitterSearcher(ig_shortcodes)
    geocode = "{0},{1},1km".format(lat,lng)
    tw_api.search_by_geocode(geocode=geocode)
    success_results += tw_api.search_results

    sorted_results = sorted(success_results, key=lambda r: r['created'], reverse=True)
    return sorted_results

def get_ig_shortcode(link_url):
    start = link_url.index('/p')
    shortcode = link_url[start + 3: -1]
    return shortcode

def translate_short_name(search_term):
    # just a start; eventually this will be a separate file (much larger) loaded into memory
    short_names = {
        'nyu': 'new york university',
        'risd': 'rhode island school of design',
        'berkeley': 'university of california, berkeley',
        'madison': 'university of wisconsin-madison',
        'wisconsin': 'university of wisconsin-madison',
        'umass': 'university of massachusetts amherst',
        'illinois': 'university of illinois at urbana-champaign',
        'university of illinois': 'university of illinois at urbana-champaign',
        'pratt': 'pratt institute',
        'colorado': 'university of colorado boulder',
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
