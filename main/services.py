from googlemaps import googlemaps
from instagram.client import InstagramAPI
import tweepy
import os

def get_photos(search_term):
    # alter search term to include the word 'university'
    # this needs to be more robust; pass to a function that generates a list of terms: 'x university', 'x college', 'university of x' and goes through them all
    if 'university' not in search_term and 'college' not in search_term:
        original_search_term = search_term
        search_term += ' university'

    # get lat-long from google maps
    try:
        gmaps = googlemaps.Client(key=os.environ['EDUC8_GMAPS'])
        geocode_result = gmaps.geocode(search_term)
        lat = geocode_result[0]['geometry']['location']['lat']
        lng = geocode_result[0]['geometry']['location']['lng']
    except (IndexError, googlemaps.exceptions.TransportError):
        message = "Sorry, I couldn't find %s." % original_search_term
        error_result = {'hasError': True, 'message': message}
        return error_result

    # connect to Instagram API
    api = InstagramAPI(client_id=os.environ['EDUC8_IG_CLIENT_ID'], client_secret=os.environ['EDUC8_IG_CLIENT_SECRET'])

    # get a list of locations for the school's lat-long
    locations = api.location_search(lat=lat, lng=lng)

    # for each location, get the URLs of media recently taken there
    success_results = []
    for location in locations:
        results = api.location_recent_media(location_id = location.id)
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
            result['ig_shortcode'] = get_ig_shortcode(media.link)
            success_results.append(result)

    # get photos from Twitter
    auth = tweepy.OAuthHandler(os.environ['EDUC8_TWITTER_CONSUMER_KEY'], os.environ['EDUC8_TWITTER_CONSUMER_SECRET'])
    auth.set_access_token(os.environ['EDUC8_TWITTER_ACCESS_TOKEN'], os.environ['EDUC8_TWITTER_ACCESS_TOKEN_SECRET'])
    twitter_api = tweepy.API(auth)

    geocode = "{0},{1},1km".format(lat,lng)
    tweets = twitter_api.search(geocode=geocode, rpp=100, show_user=True)

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
            link_url = tweet.entities['urls'][0]['display_url']
            result['ig_shortcode'] = get_ig_shortcode(link_url)
        else:
            result['ig_shortcode'] = None    
        if result['ig_shortcode'] not in [status['ig_shortcode'] for status in success_results]:
            # do something: either go to IG API for the image url and add it to this object -- or -- ditch this object, save the new shortcodes to a list, and then search IG for each shortcode and create all new objects
            success_results.append(result)

    sorted_results = sorted(success_results, key=lambda r: r['created'], reverse=True)
    return sorted_results
    # import ipdb; ipdb.set_trace();

def get_ig_shortcode(link_url):
    start = link_url.index('/p')
    shortcode = link_url[start + 3: -1]
    return shortcode
