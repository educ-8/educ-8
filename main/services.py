from googlemaps import googlemaps
from instagram.client import InstagramAPI
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
            success_results.append(result)

    sorted_results = sorted(success_results, key=lambda r: r['created'], reverse=True)
    return sorted_results

