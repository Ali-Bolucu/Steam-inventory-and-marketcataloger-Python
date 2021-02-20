#!/usr/bin/python
import requests
import json
from bs4 import BeautifulSoup
import re
import random
import time



afraid = {'0': {'game_name': '', '0': {'total_count': '', 'last_count': '0',
                                       'steamLoginSecure': '76561198867785639%7C'
                                                           '%7C9F90AD8A3D07676ACA7685B9779F3440C3E44BEE'}}}
id = "76561198867785639"


## Returns total transaction number and steamLoginSecure cookie
# Checks dictionery for cookie and WRITE over valid COOKIE
def cookie_total_count_getter():
    cookie = {'steamLoginSecure': '{}'.format(afraid['0']['0']['steamLoginSecure'])}
    fresh = afraid['0']['0']['steamLoginSecure']
    while True:
        total_count = requests.get(
            'https://steamcommunity.com/market/myhistory/render/?query=&start=0&count=100',
            cookies=cookie)

        total_count = json.loads(total_count.text)["total_count"]

        if total_count is not None:
            afraid['0']['0']['steamLoginSecure'] = fresh
            break

        elif total_count is None:
            fresh = input("steamLoginSecure cookie is wrong, enter fresh one !! \n")
            cookie = {'steamLoginSecure': fresh}

    print("", end='\n\n')
    print(cookie, end='\n\n')
    print("Cookie is valid\n")

    time.sleep(random.uniform(0.5, 1.5))
    print(str(total_count) + " transactions found !\n")

    return cookie, total_count


###################################
#####   First part
###################################


## Scans the user's market history
def market_transactions():
    cookie, total_count = cookie_total_count_getter()

    last_count = int(afraid['0']['0']['last_count'])
    page_size = 500

    from_start = input("Do you want to update ? (y/n) :")

    if from_start == "n":
        last_count = 0

    # scans all pages
    for curr_pos in range(last_count, total_count, page_size):
        time.sleep(random.uniform(0.5, 2.5))

        history = requests.get(
            'https://steamcommunity.com/market/myhistory/render/?query=&start={}&count=500'.format(curr_pos),
            cookies=cookie)

        soup = BeautifulSoup(json.loads(history.text)["results_html"], "html.parser")
        containers = soup.find_all("div", {"class": "market_listing_row"})

        for container in containers:
            status = container.div.text
            price = container.find_all("div", {"class": "market_listing_right_cell"})[0].text
            name_card = container.find_all("span", {"class": "market_listing_item_name"})[0].text
            name_game = container.find_all("span", {"class": "market_listing_game_name"})[0].text

            status = status.strip()
            price = price.strip()
            name_card = name_card.strip()
            name_game = name_game.strip()

            status = status.replace("\n", "")
            price = price.replace("\n", "").replace(",", ".")
            name_card = name_card.replace("\n", "")
            name_game = name_game.replace("\n", "")

            if name_game[-12:] == "Trading Card":
                name_game = name_game[:-13]
                print(status + " || " + price + " || " + name_game + " || " + name_card)
                print("_________________________-")

                # After getting each games and cards data, send them to classification for dictionary
                classifier_game_card(status, price, name_card, name_game)

    afraid['0']['0']['last_count'] = str(total_count)
    afraid['0']['0']['total_count'] = str(total_count)


## Classifies each card according to its information and adds to dict
# Works under market_transactions
def classifier_game_card(status, price, name_card, name_game):

    tuu_game = -1
    for i_game in afraid:
        tuu_game += 1

    flag_game = 0

    for i_game in afraid:

        if name_game == afraid[i_game]["game_name"]:
            flag_game = 1
            tuu_card = 0

            for i_card in afraid[i_game]:
                tuu_card += 1

            for i_card in range(0, tuu_card - 1):

                if name_card == afraid[i_game][str(i_card)]["card_name"]:
                    card_status_all(status, i_game, i_card, price)
                    break

                elif i_card == tuu_card - 2:
                    i_card += 1

                    game_card_adder(i_game, i_card, name_card)
                    card_status_all(status, i_game, i_card, price)
                    break

    if int(i_game) == tuu_game and flag_game == 0:

        i_game = int(i_game) + 1
        i_game = str(i_game)

        i_card = "0"

        game_adder(i_game, name_game, name_card)

        if name_card == afraid[i_game][str(i_card)]["card_name"]:
            card_status_all(status, i_game, i_card, price)


## Finds which function will work based on the status
# Works under classifier_game_card
def card_status_all(status, i_game, i_card, price):
    if status == "+":
        card_bought_spend(i_game, i_card, price)

    if status == "-":
        card_sold_earned(i_game, i_card, price)

    if status == "" and price != "":
        card_put_on_sale(i_game, i_card)

    if status == "" and price == "":
        card_canceled_on_sale(i_game, i_card)


## If the game is not in the dictionary, adds it
# Works under classifier_game_card
def game_adder(i_game, name_game, name_card):
    afraid[i_game] = {'game_name': '',
                      '0': {'card_name': '', '#oBought': '0', '#oSelled': '0', 'total_m_spend': '0',
                            'total_m_earned': '0', 'total': '0', '#oIN': '0', '#oON': '0', 'buy_order': '0'}}
    afraid[i_game]['game_name'] = name_game
    afraid[i_game]['0']["card_name"] = name_card


# If the card is not in the dictionary, adds it
# Works under classifier_game_card
def game_card_adder(i_game, i_card, name_card):
    afraid[i_game][str(i_card)] = {'card_name': '', '#oBought': '0', '#oSelled': '0',
                                   'total_m_spend': '0', 'total_m_earned': '0', 'total': '0',
                                   '#oIN': '0', '#oON': '0', 'buy_order': '0'}
    afraid[i_game][str(i_card)]["card_name"] = name_card


## If the card is bought , adds price and quantity to dictionery
# Works under classifier_game_card
# Works under card_status_all
def card_bought_spend(i_game, i_card, price):
    a = afraid[i_game][str(i_card)]["#oBought"]
    a = int(a) + 1
    afraid[i_game][str(i_card)]["#oBought"] = str(a)

    price = price.replace(".", "")
    price = re.findall("\d+", price)
    price = price[0].lstrip("0")

    a = afraid[i_game][str(i_card)]["total_m_spend"]
    a = int(price) + int(a)

    afraid[i_game][str(i_card)]["total_m_spend"] = str(a)


## If the card is sold , adds price and quantity to dictionery
# Works under classifier_game_card
def card_sold_earned(i_game, i_card, price):
    a = afraid[i_game][str(i_card)]["#oSelled"]
    a = int(a) + 1
    afraid[i_game][str(i_card)]["#oSelled"] = str(a)

    price = price.replace(".", "")
    price = re.findall("\d+", price)
    price = price[0].lstrip("0")

    a = afraid[i_game][str(i_card)]["total_m_earned"]
    a = int(price) + int(a)
    afraid[i_game][str(i_card)]["total_m_earned"] = str(a)

    a = afraid[i_game][str(i_card)]['#oON']
    a = int(a) - 1
    afraid[i_game][str(i_card)]['#oON'] = str(a)


## Calculates the number of cards on sale
# Works under classifier_game_card
# Works under card_status_all
def card_put_on_sale(i_game, i_card):
    a = afraid[i_game][str(i_card)]['#oON']
    a = int(a) + 1
    afraid[i_game][str(i_card)]['#oON'] = str(a)


## Calculates the number of cards on sale
# Works under classifier_game_card
# Works under card_status_all
def card_canceled_on_sale(i_game, i_card):
    a = afraid[i_game][str(i_card)]['#oON']
    a = int(a) - 1
    afraid[i_game][str(i_card)]['#oON'] = str(a)


###################################
#####   Second part
###################################


## Finds all inventory data
## With small function at the end, saves them to the dict
def inv_getter():
    name1 = 'game__name'
    name2 = 'card__name'
    dates = list()

    cookie = {'steamLoginSecure': '{}'.format(afraid['0']['0']['steamLoginSecure'])}

    r = requests.get('https://steamcommunity.com/profiles/{}/inventory/json/753/6'.format(id), cookies=cookie)
    inv_data = r.json()["rgDescriptions"]
    inv_inv = r.json()["rgInventory"]

    for item in inv_data:
        for item_cls in inv_data[item]["tags"]:
            if 'item_class_2' in item_cls["internal_name"]:

                if name1 != inv_data[item]["type"][:-13]:
                    name1 = inv_data[item]["type"][:-13]
                    print(inv_data[item]["type"][:-13])

                if name2 != inv_data[item]["name"]:
                    name2 = inv_data[item]["name"]

                    if inv_data[item]["marketable"] == 0:
                        count_dates = 0
                        for dat in inv_data:
                            if inv_data[dat]["market_hash_name"] == inv_data[item]["market_hash_name"]:
                                if inv_data[dat]["marketable"] == 0:

                                    classid = inv_data[dat]["classid"]
                                    instanceid = inv_data[dat]["instanceid"]

                                    for inst in inv_inv:
                                        if inv_inv[inst]["classid"] == classid and inv_inv[inst]["instanceid"] == instanceid:
                                            count_dates += 1

                                    dates.append(inv_data[dat]["cache_expiration"][:-10] + " : " + str(count_dates))

                                    count_dates = 0

                    classid = inv_data[item]["classid"]

                    count_num = 0
                    count_data = 0
                    for i in inv_inv:
                        if inv_inv[i]["classid"] == classid:
                            count_num += 1
                            if inv_inv[i]["instanceid"] == '0':
                                count_data += 1

                    for x in range(len(dates)):
                        q1 = dates[x][:10]

                        for y in range(x, len(dates)):
                            q2 = dates[y][:10]
                            if q1 > q2:
                                a, b = dates.index(dates[x]), dates.index(dates[y])
                                dates[b], dates[a] = dates[a], dates[b]
                                q1 = q2

                    inv_game_name = inv_data[item]["type"][:-13]
                    inv_card_name = inv_data[item]["name"]
                    inv_in_inv = str(count_num)
                    inv_off_sale = str(count_data)

                    print("        ||" +
                          inv_data[item]["name"] +
                          " " * (30 - len(inv_data[item]["name"])) +
                          "|| N:" + str(count_num) +
                          " || Sale:" + str(count_data) +
                          " || " + str(dates)[1:-1])
                    dates.clear()

                    for i_game in afraid:
                        if inv_game_name == afraid[i_game]["game_name"]:

                            i_i = -1

                            for i in afraid[i_game]:
                                i_i += 1

                            for i_card in range(i_i):

                                if inv_card_name == afraid[i_game][str(i_card)]["card_name"]:
                                    afraid[i_game][str(i_card)]['#oIN'] = inv_in_inv + "/" + inv_off_sale


# Requests steam/market and finds buy orders quantity and price data
def buy_order_adder():
    cookie = {'steamLoginSecure': '{}'.format(afraid['0']['0']['steamLoginSecure'])}

    buy_orders = requests.get('https://steamcommunity.com/market/{}'.format(id), cookies=cookie)
    soup = BeautifulSoup(buy_orders.text, "html.parser")
    containers = soup.find_all("div", {"class": "market_listing_row market_recent_listing_row"})

    for container in containers:
        quantity_price = container.find_all("div", {"class": "market_listing_right_cell market_listing_my_price"})
        quantity_price = quantity_price[0].span.span.text
        quantity_price = quantity_price.strip()
        quantity_price = quantity_price.replace("@\r\n\t\t\t\t", "")

        game_name = container.find_all("span", {"class": "market_listing_game_name"})[0].text

        card_name = container.find_all("a", {"class": "market_listing_item_name_link"})[0].text

        quantity_price = re.findall("\d+", quantity_price)

        quantity = quantity_price[0]
        price = int(quantity_price[1] * 100) + int(quantity_price[2])

    for i_game in afraid:
        if afraid[i_game]['game_name'] == game_name:

            i_i = -1

            for i in afraid[i_game]:
                i_i += 1

            for i_card in range(i_i):
                if afraid[i_game][str(i_card)]["card_name"] == card_name:
                    afraid[i_game][str(i_card)]["buy_order"] = quantity


## In dict, prices are like 27, turn them into 0.27
## Must be exacute after changes saved to file
def total_fixer():
    for i_game in afraid:
        if afraid[i_game]['game_name'] != "":

            i_i = -1

            for i in afraid[i_game]:
                i_i += 1

            for i_card in range(i_i):

                earned = afraid[i_game][str(i_card)]['total_m_earned']
                spend = afraid[i_game][str(i_card)]['total_m_spend']

                afraid[i_game][str(i_card)]['total_m_earned'] = str(int(earned)/100)
                afraid[i_game][str(i_card)]['total_m_spend'] = str(int(spend)/100)

                afraid[i_game][str(i_card)]['total'] = str((int(earned) - int(spend))/100)





market_transactions()  # Creates and fill all the game and their cards, the dictionary ready for after operation

inv_getter()  # Enters inventory data

buy_order_adder()  # Adds buy orders number, not price !

total_fixer()  # Don't call it before save, fix decimal points

print(afraid)
