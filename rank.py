import json
import operator
import sys
from random import randint
cuisine_weight = 5
meat_weight = 3
veg_weight = 2


expand= { "seafood":["fish", "shrimp", "salmon", "tuna", "cod", "lobster", "crab", "scallops", "octopus", "haddock"],
          "asian":["chinese", "japanese", "korean", "vietnamese", "thai"],
          "beans":["pea"],
          "flowers":["cauliflower","broccoli"],
          "leaves":["kale","chard","spinach","lettuce","cabbage"],
          "milk":["cheese", "mozzarella", "paneer"],
          "cheese":["mozzarella", "paneer"],
          "poultry":["chicken"]
          }


def calculate_score_for_item(item, meat, vegetable, allergy, favorite):
    item = item.lower()

    for key in allergy:
        if key.lower() in item:
            return -100000

    score_f = 0
    for key in favorite:
        if key.lower() in item:
            score_f = 1000
    score_m = 0
    for key, val in meat.iteritems():
        if key.lower() in item and score_m < val * meat_weight:
            score_m = val * meat_weight
    score_v = 0
    for key, val in vegetable.iteritems():
        if key.lower() in item and score_v < val * veg_weight:
            score_v = val * veg_weight
    return score_m + score_v + score_f

def weight_decay(food, cuisine, meat, vegetable):
    for item in cuisine:
        if item in food:
            cuisine[item] = float(cuisine[item]) * 0.7
    for item in meat:
        if item in food:
            meat[item] = float(meat[item]) * 0.7
    for item in vegetable:
        if item in food:
            vegetable[item] = float(vegetable[item]) * 0.7


def parse_preference (preference_json, cuisine, meat, vegetable, allergy, favorites):
    allergy.extend( preference_json["restrictions"])
    for key, val in expand.iteritems():
        if key in allergy:
            allergy.extend(val)

    for key in allergy:
        print key

    favorites.extend(preference_json["favorites"])
    for key, val in expand.iteritems():
        if key in favorites:
            favorites.extend(val)

    meat.update(preference_json["scores"]["meats"])
    for key, val in expand.iteritems():
        if key in meat:
            meat.update( { k:meat[key] for k in expand[key] } )

    vegetable.update(preference_json["scores"]["vegetables"])
    for key, val in expand.iteritems():
        if key in vegetable:
            vegetable.update( { k:vegetable[key] for k in expand[key] } )

    cuisine.update(preference_json["scores"]["cuisines"])
    for key, val in expand.iteritems():
        if key in cuisine:
            cuisine.update( { k:cuisine[key] for k in expand[key] } )

def pick_food(menu_json, preference_json):
    final_result = []
    id_list= []
    cuisine={}
    meat={}
    vegetable={}
    allergy=[]
    favorites=[]
    parse_preference(preference_json, cuisine, meat, vegetable, allergy, favorites)
    for menu in menu_json:
        if final_result:
            weight_decay(final_result[-1], cuisine, meat, vegetable)
        final_options={}
        for restaurant in menu:
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
                        '''
                        if "inventory" in food:
                            if food["inventory"] == 0:
                                continue
                     '''
                        if "price" in food:
                            if food["price"] <= 8:
                                continue
                        score = 0
                        if "description" in food:
                            score=calculate_score_for_item(food["description"]+" "+food["name"], meat, vegetable, allergy, favorites) + base_score
                        else:
                            score=calculate_score_for_item(food["name"], meat, vegetable, allergy, favorites)+base_score

                        final_options[food["name"]]=(score, food)

        b = final_options.items()
        b.sort(key = lambda x : x[1][0], reverse=True)
        highest = b[0][1][0]
        top = [ x for x in b if x[1][0] == highest ]

        index = top[randint(0, len(top)-1)]
        r={}
        if "options" in index[1][1]:
            r = { "id": index[1][1]["id"], "option_id" : ','.join([item["choices"][0]["id"] for item in index[1][1]["options"]]) }
        else:
            r={"id":index[1][1]["id"], "option_id" : ""}
        id_list.append(r)
        final_result.append(index[1][1]["name"]+" "+index[1][1]["description"])

    print (final_result)
    return id_list

if __name__ == '__main__':
    f=open('examples/menus.json','r')
    x = f.read()
    #file = open(sys.argv[1],"r")
    file = open("data/preferences/dshao@purestorage.com.json","r")
    y=file.read()
    x_ = [json.loads(x)]
    y_ = json.loads(y)['preferences']
    return_id = pick_food(x_, y_)

    print "return id is "+str(return_id)





