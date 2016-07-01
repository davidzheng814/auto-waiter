import requests
import json

#https://maps.googleapis.com/maps/api/place/nearbysearch/json?
#location=37.388009,-122.083157&radius=15000&type=restaurant&
#name=houseoffalafel&key=AIzaSyCZshO4gyP5g3brwdmb-4OQ9R3WOK7d2Ng

api_key = 'AIzaSyCZshO4gyP5g3brwdmb-4OQ9R3WOK7d2Ng'
location = '37.388009,-122.083157'
radius = '30000'
'''
with open('../menus.json') as data_file:
    data = json.load(data_file)

# get the restaurant name from the waiter.com menu json
restaurant_name = data[1]['updated']['menus'][0]['name']
'''
def get_restaurant_rate(restaurant_name):
    # use the restaurant name to search nearby pure storage for the restaurant
    r = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={location} \
        &radius={radius}&type=restaurant&name={name}&key={key}' \
        .format(location = location, radius = radius, name = restaurant_name, key = api_key))
    res = r.json()

    # get the place_id
    place_id = res['results'][0]['place_id']
    rating = res['results'][0]['rating']
    print(place_id)
    print(rating)

    # use the place_id to get the reviews
    r = requests.get('https://maps.googleapis.com/maps/api/place/details/json?placeid={place_id}&key={key}' \
        .format(place_id = place_id, key = api_key))
    res = r.json()

    review = res['result']['reviews'][0]['text']
    print(review)
    return rating

#https://maps.googleapis.com/maps/api/place/details/json?placeid=ChIJ50U9hJ-1j4AR47TWB8Q7nOc&key=AIzaSyCZshO4gyP5g3brwdmb-4OQ9R3WOK7d2Ng
