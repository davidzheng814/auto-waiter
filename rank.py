import json
import operator
'''
cuisine={ "indian":5, "mediterranean":3, "italian":5, "american":7, "mexican":1, "chinese":6, "japanese":5, "vietnamese":5, "thai":8, "korean":6}
meat={"beef":6, "pork":4, "chicken":3, "duck":4, "lamb":20, "seafood":5, "vegetables":4}
vegetable={"tomato" : 3, "broccoli" : 7, "onion" : 5}
allergy=["lamb"]
'''
cuisine_weight = 5
meat_weight = 3
veg_weight = 2


def calculate_score_for_item(item, meat, vegetable, allergy):
    item = item.lower()
    for key in allergy:
        if key.lower() in item:
            return -100000
    score_m = 0
    for key, val in meat.iteritems():
        if key.lower() in item and score_m < val * meat_weight:
            score_m = val * meat_weight
    score_v = 0
    for key, val in vegetable.iteritems():
        if key.lower() in item and score_v < val * veg_weight:
            score_v = val * veg_weight
    return score_m + score_v


def parse_json(json_string):
    return json.loads(json_string)


def parse_preference (preference_json, cuisine, meat, vegetable, allergy):
    result = json.loads(preference_json)
    allergy.extend( result["restrictions"])
    meat.update(result["scores"]["meats"])
    vegetable.update(result["scores"]["vegetable"])
    cuisine.update(result["scores"]["cuisine"])


def pick_food(menu_json, preference_json):
    result = parse_json(menu_json)
    cuisine={}
    meat={}
    vegetable={}
    allergy=[]
    parse_perference(preference_json, cuisine, meat, vegetable, allergy)
    num_restaurant = len(result)
    print num_restaurant
    # every restaurant
    highest=0
    name=""
    des={}
    final_options={}
    for restaurant in result:
        sections = restaurant['updated']["menus"][0]["sections"]
        base_score = 0
        restaurant_des = " ".join(restaurant['cuisine_types']).lower()
        for key, val in cuisine.iteritems():
            if key in restaurant_des and base_score < val * cuisine_weight:
                base_score = val * cuisine_weight
        for section in sections:
            if "items" in section:
                foods = section["items"]
                for food in foods:
                    if "inventory" in food:
                        if food["inventory"] == 0:
                            continue
                    score = 0
                    if "description" in food:
                        score=calculate_score_for_item(food["description"]+" "+food["name"], meat, vegetable, allergy) + base_score
                    else:
                        score=calculate_score_for_item(food["name"], meat, vegetable, allergy)+base_score

                    final_options[food["name"]]=(score, food)
                    if score > highest:
                        highest = score
                        name = food["name"]
                        des = food["description"]

    print highest
    print name
    print des

    b = final_options.items()
    b.sort(key = lambda x : x[1][0], reverse=True)

    for i in range(0,5):
        print b[i][0]
        print b[i][1][0]
        if "description" in b[i][1][1]:
            print b[i][1][1]["description"]
        print



f=open('examples/menus.json','r')
x = f.read()
pick_food(x, )







