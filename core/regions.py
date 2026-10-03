from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from config import settings

logger = logging.getLogger(__name__)

POPULAR_REGIONS: list[tuple[str, str]] = [
    ("moskva", "Москва и МО"),
    ("spb", "Санкт-Петербург и ЛО"),
    ("yakutsk", "Якутск (Саха)"),
    ("novosibirsk", "Новосибирск"),
    ("ekaterinburg", "Екатеринбург"),
    ("krasnodar", "Краснодар"),
    ("kazan", "Казань"),
    ("omsk", "Омск"),
    ("krasnoyarsk", "Красноярск"),
    ("rostov", "Ростов-на-Дону"),
    ("nn", "Нижний Новгород"),
    ("samara", "Самара"),
    ("ufa", "Уфа"),
    ("chelyabinsk", "Челябинск"),
    ("perm", "Пермь"),
    ("volgograd", "Волгоград"),
    ("voronezh", "Воронеж"),
    ("vladivostok", "Владивосток"),
    ("khabarovsk", "Хабаровск"),
    ("irkutsk", "Иркутск"),
    ("ulan_ude", "Улан-Удэ"),
    ("chita", "Чита"),
    ("tyumen", "Тюмень"),
    ("surgut", "Сургут"),
    ("sochi", "Сочи"),
    ("all_russia", "🇷🇺 Вся Россия"),
]

CITY_DATABASE: dict[str, dict[str, str]] = {
    # Крупнейшие мегаполисы
    "moskva": {"name": "Москва", "avito_id": "637640", "youla_id": "576d06124994ee94589d8194", "youla_slug": "moskva"},
    "spb": {"name": "Санкт-Петербург", "avito_id": "653240", "youla_id": "576d06124994ee94589d8195", "youla_slug": "sankt-peterburg"},
    "krasnodar": {"name": "Краснодар", "avito_id": "635290", "youla_id": "576d06134994ee94589d81a4", "youla_slug": "krasnodar"},
    "ekaterinburg": {"name": "Екатеринбург", "avito_id": "652000", "youla_id": "576d06124994ee94589d8198", "youla_slug": "ekaterinburg"},
    "kazan": {"name": "Казань", "avito_id": "632660", "youla_id": "576d06134994ee94589d81a0", "youla_slug": "kazan"},
    "novosibirsk": {"name": "Новосибирск", "avito_id": "645470", "youla_id": "576d06124994ee94589d8196", "youla_slug": "novosibirsk"},
    "rostov": {"name": "Ростов-на-Дону", "avito_id": "649930", "youla_id": "576d06134994ee94589d81a2", "youla_slug": "rostov-na-donu"},
    "nn": {"name": "Нижний Новгород", "avito_id": "642460", "youla_id": "576d06124994ee94589d8197", "youla_slug": "nizhniy-novgorod"},
    "samara": {"name": "Самара", "avito_id": "651080", "youla_id": "576d06134994ee94589d8199", "youla_slug": "samara"},
    "sochi": {"name": "Сочи", "avito_id": "635840", "youla_id": "576d06134994ee94589d81af", "youla_slug": "sochi"},
    "ufa": {"name": "Уфа", "avito_id": "623950", "youla_id": "576d06134994ee94589d81a1", "youla_slug": "ufa"},
    "voronezh": {"name": "Воронеж", "avito_id": "628860", "youla_id": "576d06134994ee94589d81a6", "youla_slug": "voronezh"},
    "chelyabinsk": {"name": "Челябинск", "avito_id": "657410", "youla_id": "576d06124994ee94589d819b", "youla_slug": "chelyabinsk"},
    "krasnoyarsk": {"name": "Красноярск", "avito_id": "636400", "youla_id": "576d06134994ee94589d81a3", "youla_slug": "krasnoyarsk"},
    "perm": {"name": "Пермь", "avito_id": "647000", "youla_id": "576d06134994ee94589d81a5", "youla_slug": "perm"},
    "volgograd": {"name": "Волгоград", "avito_id": "627340", "youla_id": "576d06134994ee94589d81a7", "youla_slug": "volgograd"},
    "saratov": {"name": "Саратов", "avito_id": "651870", "youla_id": "576d06134994ee94589d81a8", "youla_slug": "saratov"},
    "tyumen": {"name": "Тюмень", "avito_id": "655930", "youla_id": "576d06134994ee94589d81a9", "youla_slug": "tyumen"},
    "tolyatti": {"name": "Тольятти", "avito_id": "651470", "youla_id": "576d06134994ee94589d81aa", "youla_slug": "tolyatti"},
    "izhevsk": {"name": "Ижевск", "avito_id": "654520", "youla_id": "576d06134994ee94589d81ab", "youla_slug": "izhevsk"},
    "barnaul": {"name": "Барнаул", "avito_id": "621860", "youla_id": "576d06134994ee94589d81ac", "youla_slug": "barnaul"},
    "irkutsk": {"name": "Иркутск", "avito_id": "631620", "youla_id": "576d06134994ee94589d81ae", "youla_slug": "irkutsk"},
    "khabarovsk": {"name": "Хабаровск", "avito_id": "656640", "youla_id": "576d06134994ee94589d81b0", "youla_slug": "khabarovsk"},
    "yaroslavl": {"name": "Ярославль", "avito_id": "660230", "youla_id": "576d06134994ee94589d81b1", "youla_slug": "yaroslavl"},
    "vladivostok": {"name": "Владивосток", "avito_id": "648140", "youla_id": "576d06134994ee94589d81b2", "youla_slug": "vladivostok"},
    "tomsk": {"name": "Томск", "avito_id": "655290", "youla_id": "576d06134994ee94589d81b4", "youla_slug": "tomsk"},
    "orenburg": {"name": "Оренбург", "avito_id": "646090", "youla_id": "576d06134994ee94589d81b5", "youla_slug": "orenburg"},
    "kemerovo": {"name": "Кемерово", "avito_id": "633460", "youla_id": "576d06134994ee94589d81b6", "youla_slug": "kemerovo"},
    "ryazan": {"name": "Рязань", "avito_id": "650630", "youla_id": "576d06134994ee94589d81b8", "youla_slug": "ryazan"},
    "naberezhnye_chelny": {"name": "Набережные Челны", "avito_id": "632890", "youla_id": "576d06134994ee94589d81b9", "youla_slug": "naberezhnye-chelny"},
    "astrakhan": {"name": "Астрахань", "avito_id": "623340", "youla_id": "576d06134994ee94589d81ba", "youla_slug": "astrakhan"},
    "penza": {"name": "Пенза", "avito_id": "646690", "youla_id": "576d06134994ee94589d81bb", "youla_slug": "penza"},
    "kirov": {"name": "Киров", "avito_id": "634030", "youla_id": "576d06134994ee94589d81bc", "youla_slug": "kirov"},
    "lipetsk": {"name": "Липецк", "avito_id": "637040", "youla_id": "576d06134994ee94589d81bd", "youla_slug": "lipetsk"},
    "cheboksary": {"name": "Чебоксары", "avito_id": "658930", "youla_id": "576d06134994ee94589d81be", "youla_slug": "cheboksary"},
    "kaliningrad": {"name": "Калининград", "avito_id": "633030", "youla_id": "576d06134994ee94589d81bf", "youla_slug": "kaliningrad"},
    "tula": {"name": "Тула", "avito_id": "655680", "youla_id": "576d06134994ee94589d81c0", "youla_slug": "tula"},
    "kursk": {"name": "Курск", "avito_id": "636730", "youla_id": "576d06134994ee94589d81c1", "youla_slug": "kursk"},
    "stavropol": {"name": "Ставрополь", "avito_id": "653990", "youla_id": "576d06134994ee94589d81c2", "youla_slug": "stavropol"},
    "ulyanovsk": {"name": "Ульяновск", "avito_id": "656240", "youla_id": "576d06134994ee94589d81ad", "youla_slug": "ulyanovsk"},
    "tver": {"name": "Тверь", "avito_id": "654920", "youla_id": "576d06134994ee94589d81c4", "youla_slug": "tver"},
    "magnitogorsk": {"name": "Магнитогорск", "avito_id": "657660", "youla_id": "576d06134994ee94589d81c5", "youla_slug": "magnitogorsk"},
    "ivanovo": {"name": "Иваново", "avito_id": "630800", "youla_id": "576d06134994ee94589d81c6", "youla_slug": "ivanovo"},
    "bryansk": {"name": "Брянск", "avito_id": "624410", "youla_id": "576d06134994ee94589d81c7", "youla_slug": "bryansk"},
    "belgorod": {"name": "Белгород", "avito_id": "624140", "youla_id": "576d06134994ee94589d81c8", "youla_slug": "belgorod"},
    "surgut": {"name": "Сургут", "avito_id": "658090", "youla_id": "576d06134994ee94589d81c9", "youla_slug": "surgut"},
    "vladimir": {"name": "Владимир", "avito_id": "626780", "youla_id": "576d06134994ee94589d81ca", "youla_slug": "vladimir"},

    # Сибирь и Дальний Восток (включая Якутск)
    "yakutsk": {"name": "Якутск", "avito_id": "655840", "youla_id": "576d06134994ee94589d81cd", "youla_slug": "yakutsk"},
    "omsk": {"name": "Омск", "avito_id": "645830", "youla_id": "576d06124994ee94589d819a", "youla_slug": "omsk"},
    "ulan_ude": {"name": "Улан-Удэ", "avito_id": "625600", "youla_id": "576d06134994ee94589d81ce", "youla_slug": "ulan-ude"},
    "chita": {"name": "Чита", "avito_id": "661950", "youla_id": "576d06134994ee94589d81cf", "youla_slug": "chita"},
    "blagoveshchensk": {"name": "Благовещенск", "avito_id": "622260", "youla_id": "576d06134994ee94589d81d0", "youla_slug": "blagoveshchensk"},
    "yuzhno_sakhalinsk": {"name": "Южно-Сахалинск", "avito_id": "652430", "youla_id": "576d06134994ee94589d81d1", "youla_slug": "yuzhno-sahalinsk"},
    "petropavlovsk_kamchatsky": {"name": "Петропавловск-Камчатский", "avito_id": "633630", "youla_id": "576d06134994ee94589d81d2", "youla_slug": "petropavlovsk-kamchatskiy"},
    "magadan": {"name": "Магадан", "avito_id": "638970", "youla_id": "576d06134994ee94589d81d3", "youla_slug": "magadan"},
    "norilsk": {"name": "Норильск", "avito_id": "636540", "youla_id": "576d06134994ee94589d81d4", "youla_slug": "norilsk"},
    "novy_urengoy": {"name": "Новый Уренгой", "avito_id": "659550", "youla_id": "576d06134994ee94589d81d5", "youla_slug": "novyy-urengoy"},
    "nizhnevartovsk": {"name": "Нижневартовск", "avito_id": "657960", "youla_id": "576d06134994ee94589d81d6", "youla_slug": "nizhnevartovsk"},
    "khanty_mansiysk": {"name": "Ханты-Мансийск", "avito_id": "658120", "youla_id": "576d06134994ee94589d81d7", "youla_slug": "hanty-mansiysk"},
    "noyabrsk": {"name": "Ноябрьск", "avito_id": "659610", "youla_id": "576d06134994ee94589d81d8", "youla_slug": "noyabrsk"},
    "abakan": {"name": "Абакан", "avito_id": "656850", "youla_id": "576d06134994ee94589d81d9", "youla_slug": "abakan"},
    "kyzyl": {"name": "Кызыл", "avito_id": "654270", "youla_id": "576d06134994ee94589d81da", "youla_slug": "kyzyl"},
    "gorno_altaysk": {"name": "Горно-Алтайск", "avito_id": "621670", "youla_id": "576d06134994ee94589d81db", "youla_slug": "gorno-altaysk"},
    "biysk": {"name": "Бийск", "avito_id": "621940", "youla_id": "576d06134994ee94589d81dc", "youla_slug": "biysk"},
    "bratsk": {"name": "Братск", "avito_id": "631690", "youla_id": "576d06134994ee94589d81dd", "youla_slug": "bratsk"},
    "angarsk": {"name": "Ангарск", "avito_id": "631630", "youla_id": "576d06134994ee94589d81de", "youla_slug": "angarsk"},
    "komsomolsk_na_amure": {"name": "Комсомольск-на-Амуре", "avito_id": "656680", "youla_id": "576d06134994ee94589d81df", "youla_slug": "komsomolsk-na-amure"},
    "nakhodka": {"name": "Находка", "avito_id": "648230", "youla_id": "576d06134994ee94589d81e0", "youla_slug": "nahodka"},
    "ussuriysk": {"name": "Уссурийск", "avito_id": "648350", "youla_id": "576d06134994ee94589d81e1", "youla_slug": "ussuriysk"},
    "novokuznetsk": {"name": "Новокузнецк", "avito_id": "633540", "youla_id": "576d06134994ee94589d81f7", "youla_slug": "novokuznetsk"},
    "prokopyevsk": {"name": "Прокопьевск", "avito_id": "633600", "youla_id": "576d06134994ee94589d81f8", "youla_slug": "prokopevsk"},

    # Север, Северо-Запад и Центр
    "arkhangelsk": {"name": "Архангельск", "avito_id": "622780", "youla_id": "576d06134994ee94589d81e2", "youla_slug": "arhangelsk"},
    "murmansk": {"name": "Мурманск", "avito_id": "641320", "youla_id": "576d06134994ee94589d81e3", "youla_slug": "murmansk"},
    "petrozavodsk": {"name": "Петрозаводск", "avito_id": "633800", "youla_id": "576d06134994ee94589d81e4", "youla_slug": "petrozavodsk"},
    "syktyvkar": {"name": "Сыктывкар", "avito_id": "634730", "youla_id": "576d06134994ee94589d81e5", "youla_slug": "syktyvkar"},
    "vologda": {"name": "Вологда", "avito_id": "628290", "youla_id": "576d06134994ee94589d81e6", "youla_slug": "vologda"},
    "cherepovets": {"name": "Череповец", "avito_id": "628580", "youla_id": "576d06134994ee94589d81e7", "youla_slug": "cherepovets"},
    "pskov": {"name": "Псков", "avito_id": "648750", "youla_id": "576d06134994ee94589d81e8", "youla_slug": "pskov"},
    "veliky_novgorod": {"name": "Великий Новгород", "avito_id": "643770", "youla_id": "576d06134994ee94589d81e9", "youla_slug": "velikiy-novgorod"},
    "smolensk": {"name": "Смоленск", "avito_id": "652970", "youla_id": "576d06134994ee94589d81ea", "youla_slug": "smolensk"},
    "kaluga": {"name": "Калуга", "avito_id": "633250", "youla_id": "576d06134994ee94589d81eb", "youla_slug": "kaluga"},
    "orel": {"name": "Орел", "avito_id": "646390", "youla_id": "576d06134994ee94589d81ec", "youla_slug": "orel"},
    "tambov": {"name": "Тамбов", "avito_id": "654710", "youla_id": "576d06134994ee94589d81ed", "youla_slug": "tambov"},
    "kostroma": {"name": "Кострома", "avito_id": "635030", "youla_id": "576d06134994ee94589d81ee", "youla_slug": "kostroma"},
    "saransk": {"name": "Саранск", "avito_id": "640700", "youla_id": "576d06134994ee94589d81ef", "youla_slug": "saransk"},
    "yoshkar_ola": {"name": "Йошкар-Ола", "avito_id": "639860", "youla_id": "576d06134994ee94589d81f0", "youla_slug": "yoshkar-ola"},
    "kurgan": {"name": "Курган", "avito_id": "636180", "youla_id": "576d06134994ee94589d81f1", "youla_slug": "kurgan"},

    # Урал и Поволжье
    "sterlitamak": {"name": "Стерлитамак", "avito_id": "624020", "youla_id": "576d06134994ee94589d81f2", "youla_slug": "sterlitamak"},
    "nizhny_tagil": {"name": "Нижний Тагил", "avito_id": "652150", "youla_id": "576d06134994ee94589d81f3", "youla_slug": "nizhniy-tagil"},
    "kamensk_uralsky": {"name": "Каменск-Уральский", "avito_id": "652070", "youla_id": "576d06134994ee94589d81f4", "youla_slug": "kamensk-uralskiy"},
    "zlatoust": {"name": "Златоуст", "avito_id": "657480", "youla_id": "576d06134994ee94589d81f5", "youla_slug": "zlatoust"},
    "miass": {"name": "Миасс", "avito_id": "657680", "youla_id": "576d06134994ee94589d81f6", "youla_slug": "miass"},

    # Юг, Кавказ и Крым
    "makhachkala": {"name": "Махачкала", "avito_id": "629550", "youla_id": "576d06134994ee94589d81f9", "youla_slug": "mahachkala"},
    "grozny": {"name": "Грозный", "avito_id": "659170", "youla_id": "576d06134994ee94589d81fa", "youla_slug": "groznyy"},
    "vladikavkaz": {"name": "Владикавказ", "avito_id": "652670", "youla_id": "576d06134994ee94589d81fb", "youla_slug": "vladikavkaz"},
    "nalchik": {"name": "Нальчик", "avito_id": "632340", "youla_id": "576d06134994ee94589d81fc", "youla_slug": "nalchik"},
    "cherkessk": {"name": "Черкесск", "avito_id": "633360", "youla_id": "576d06134994ee94589d81fd", "youla_slug": "cherkessk"},
    "maykop": {"name": "Майкоп", "avito_id": "621450", "youla_id": "576d06134994ee94589d81fe", "youla_slug": "maykop"},
    "elista": {"name": "Элиста", "avito_id": "633190", "youla_id": "576d06134994ee94589d81ff", "youla_slug": "elista"},
    "novorossiysk": {"name": "Новороссийск", "avito_id": "635600", "youla_id": "576d06134994ee94589d8200", "youla_slug": "novorossiysk"},
    "armavir": {"name": "Армавир", "avito_id": "635390", "youla_id": "576d06134994ee94589d8201", "youla_slug": "armavir"},
    "taganrog": {"name": "Таганрог", "avito_id": "650170", "youla_id": "576d06134994ee94589d8202", "youla_slug": "taganrog"},
    "shakhty": {"name": "Шахты", "avito_id": "650320", "youla_id": "576d06134994ee94589d8203", "youla_slug": "shahty"},
    "volzhsky": {"name": "Волжский", "avito_id": "627440", "youla_id": "576d06134994ee94589d8204", "youla_slug": "volzhskiy"},
    "sevastopol": {"name": "Севастополь", "avito_id": "652550", "youla_id": "576d06134994ee94589d8205", "youla_slug": "sevastopol"},
    "simferopol": {"name": "Симферополь", "avito_id": "652570", "youla_id": "576d06134994ee94589d8206", "youla_slug": "simferopol"},
    "kerch": {"name": "Керчь", "avito_id": "652510", "youla_id": "576d06134994ee94589d8207", "youla_slug": "kerch"},

    # Вся Россия
    "all_russia": {"name": "Вся Россия", "avito_id": "621540", "youla_id": "", "youla_slug": "rossiya"},
}

# Пользовательские синонимы и сокращения для быстрого распознавания
CITY_ALIASES: dict[str, str] = {
    # Москва и МО
    "мск": "moskva",
    "москва": "moskva",
    "мо": "moskva",
    "московская": "moskva",

    # СПб и ЛО
    "спб": "spb",
    "питер": "spb",
    "петербург": "spb",
    "санкт-петербург": "spb",
    "санкт петербург": "spb",
    "sankt-peterburg": "spb",
    "sankt_peterburg": "spb",
    "saint-petersburg": "spb",
    "ленинград": "spb",

    # Якутск (Саха)
    "якутск": "yakutsk",
    "якт": "yakutsk",
    "саха": "yakutsk",
    "якутия": "yakutsk",

    # Сибирь и Дальний Восток
    "омск": "omsk",
    "омская": "omsk",
    "улан-удэ": "ulan_ude",
    "улан удэ": "ulan_ude",
    "уланудэ": "ulan_ude",
    "бурятия": "ulan_ude",
    "чита": "chita",
    "забайкалье": "chita",
    "благовещенск": "blagoveshchensk",
    "благ": "blagoveshchensk",
    "амур": "blagoveshchensk",
    "южно-сахалинск": "yuzhno_sakhalinsk",
    "южно сахалинск": "yuzhno_sakhalinsk",
    "южносахалинск": "yuzhno_sakhalinsk",
    "сахалин": "yuzhno_sakhalinsk",
    "петропавловск-камчатский": "petropavlovsk_kamchatsky",
    "петропавловск камчатский": "petropavlovsk_kamchatsky",
    "петропавловск": "petropavlovsk_kamchatsky",
    "камчатка": "petropavlovsk_kamchatsky",
    "пк": "petropavlovsk_kamchatsky",
    "магадан": "magadan",
    "колыма": "magadan",
    "норильск": "norilsk",
    "новый уренгой": "novy_urengoy",
    "уренгой": "novy_urengoy",
    "нур": "novy_urengoy",
    "нижневартовск": "nizhnevartovsk",
    "вартовск": "nizhnevartovsk",
    "нв": "nizhnevartovsk",
    "ханты-мансийск": "khanty_mansiysk",
    "ханты": "khanty_mansiysk",
    "хмао": "khanty_mansiysk",
    "ноябрьск": "noyabrsk",
    "абакан": "abakan",
    "хакасия": "abakan",
    "кызыл": "kyzyl",
    "тыва": "kyzyl",
    "горно-алтайск": "gorno_altaysk",
    "бийск": "biysk",
    "братск": "bratsk",
    "ангарск": "angarsk",
    "комсомольск-на-амуре": "komsomolsk_na_amure",
    "комсомольск": "komsomolsk_na_amure",
    "находка": "nakhodka",
    "уссурийск": "ussuriysk",
    "новокузнецк": "novokuznetsk",
    "кузня": "novokuznetsk",
    "прокопьевск": "prokopyevsk",

    # Северо-Запад и Север
    "архангельск": "arkhangelsk",
    "арх": "arkhangelsk",
    "мурманск": "murmansk",
    "мурманская": "murmansk",
    "петрозаводск": "petrozavodsk",
    "карелия": "petrozavodsk",
    "птз": "petrozavodsk",
    "сыктывкар": "syktyvkar",
    "коми": "syktyvkar",
    "вологда": "vologda",
    "череповец": "cherepovets",
    "псков": "pskov",
    "великий новгород": "veliky_novgorod",
    "новгород": "veliky_novgorod",

    # Центр и Черноземье
    "смоленск": "smolensk",
    "калуга": "kaluga",
    "орел": "orel",
    "орёл": "orel",
    "тамбов": "tambov",
    "кострома": "kostroma",
    "саранск": "saransk",
    "мордовия": "saransk",
    "йошкар-ола": "yoshkar_ola",
    "йошкарола": "yoshkar_ola",
    "йошка": "yoshkar_ola",
    "курган": "kurgan",

    # Урал и Поволжье
    "екб": "ekaterinburg",
    "екатеринбург": "ekaterinburg",
    "свердловск": "ekaterinburg",
    "нн": "nn",
    "нижний": "nn",
    "нижний новгород": "nn",
    "нижний тагил": "nizhny_tagil",
    "тагил": "nizhny_tagil",
    "стерлитамак": "sterlitamak",
    "златоуст": "zlatoust",
    "миасс": "miass",

    # Юг, Кавказ и Крым
    "ростов": "rostov",
    "ростов-на-дону": "rostov",
    "ростов на дону": "rostov",
    "рнд": "rostov",
    "краснодар": "krasnodar",
    "крд": "krasnodar",
    "сочи": "sochi",
    "новосиб": "novosibirsk",
    "новосибирск": "novosibirsk",
    "махачкала": "makhachkala",
    "дагестан": "makhachkala",
    "грозный": "grozny",
    "чечня": "grozny",
    "владикавказ": "vladikavkaz",
    "осетия": "vladikavkaz",
    "нальчик": "nalchik",
    "черкесск": "cherkessk",
    "майкоп": "maykop",
    "элиста": "elista",
    "новороссийск": "novorossiysk",
    "новоросс": "novorossiysk",
    "армавир": "armavir",
    "таганрог": "taganrog",
    "шахты": "shakhty",
    "волжский": "volzhsky",
    "севастополь": "sevastopol",
    "сев": "sevastopol",
    "симферополь": "simferopol",
    "симф": "simferopol",
    "крым": "simferopol",
    "керчь": "kerch",

    # Россия в целом
    "россия": "all_russia",
    "вся россия": "all_russia",
    "рф": "all_russia",
}


class RegionManager:
    """
    Менеджер переключения региона поиска на Авито и Юле.
    Позволяет изменять целевой город прямо через интерфейс Telegram-бота.
    """

    def __init__(self, config_file: Optional[Path | str] = None):
        self.config_file = Path(config_file) if config_file else (settings.BASE_DIR / "region_settings.json")
        self._listeners: list[Callable[[dict[str, str]], None]] = []
        self._current_region: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        """Загрузка сохраненного региона из файла или fallback на .env."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "name" in data and "avito_id" in data:
                        return data
            except Exception as e:
                logger.warning("Не удалось прочитать %s: %s", self.config_file, e)

        # Дефолт из настроек (Москва)
        return {
            "key": "moskva",
            "name": "Москва",
            "avito_id": settings.AVITO_LOCATION_ID,
            "youla_id": settings.YOULA_CITY_ID,
            "youla_slug": "moskva",
        }

    def _save(self) -> None:
        """Сохранение региона на диск."""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._current_region, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error("Ошибка сохранения региона в %s: %s", self.config_file, e)

    @property
    def current(self) -> dict[str, str]:
        """Текущий активный регион."""
        return self._current_region

    def add_listener(self, callback: Callable[[dict[str, str]], None]) -> None:
        """Регистрация слушателя (например, воркера) для мгновенного обновления локации."""
        self._listeners.append(callback)

    def set_region(self, city_key_or_name: str) -> Optional[dict[str, str]]:
        """
        Устанавливает новый регион поиска по ключу или названию.
        Мгновенно уведомляет всех зарегистрированных воркеров.
        """
        normalized_query = city_key_or_name.lower().strip()

        # 1. Проверка по алиасам (мск, спб, питер, якт...)
        if normalized_query in CITY_ALIASES:
            key = CITY_ALIASES[normalized_query]
            city_data = CITY_DATABASE[key]
        # 2. Прямой ключ
        elif normalized_query in CITY_DATABASE:
            key = normalized_query
            city_data = CITY_DATABASE[key]
        else:
            # 3. Поиск по имени города
            matches = self.find_cities(normalized_query)
            if not matches:
                return None
            key, city_data = matches[0]

        self._current_region = {
            "key": key,
            "name": city_data["name"],
            "avito_id": city_data["avito_id"],
            "youla_id": city_data["youla_id"],
            "youla_slug": city_data.get("youla_slug", "moskva"),
        }
        self._save()

        # Уведомляем воркеры
        for listener in self._listeners:
            try:
                listener(self._current_region)
            except Exception as e:
                logger.error("Ошибка уведомления слушателя региона: %s", e)

        logger.info("Регион поиска успешно изменен на: %s", self._current_region["name"])
        return self._current_region

    def find_cities(self, query: str) -> list[tuple[str, dict[str, str]]]:
        """Поиск городов по частичному совпадению названия."""
        q = query.lower().strip()
        if not q:
            return []

        # Сначала проверяем точное совпадение алиаса
        if q in CITY_ALIASES:
            key = CITY_ALIASES[q]
            return [(key, CITY_DATABASE[key])]

        results: list[tuple[str, dict[str, str]]] = []
        for key, data in CITY_DATABASE.items():
            name = data["name"].lower()
            if q == name or name.startswith(q) or q in name:
                results.append((key, data))

        return results

    def is_item_matching_current_region(self, location: str, url: str = "") -> bool:
        """
        Строгий валидатор региона для входящих лотов (Gatekeeper).
        Гарантирует, что при выбранном немосковском регионе (например, Екатеринбург)
        объявления из Москвы или других сторонних городов не просочатся пользователю.
        """
        curr = self.current
        key = curr.get("key", "moskva")
        if key == "all_russia":
            return True

        loc_lower = (location or "").lower()
        url_lower = (url or "").lower()
        combined = f"{loc_lower} {url_lower}"

        # 1. Если выбран НЕ регион Москвы, но в локации или ссылке явно Москва/МО — СТРОГО отсекаем
        if key != "moskva":
            moscow_markers = (
                "москв", "moskva", "зеленоград", "щербинк", "люберц", "балаших",
                "одинцов", "королев", "королёв", "мытищ", "химки", "подольск",
                "домодедово", "красногорск", "раменск", "серпухов", "коломн",
                "пушкин", "долгопрудн", "реутов", "жуковск", "щелков", "ногинск",
                "орехово-зуев", "видн", "чехов", "сергиев посад", "mytischi",
                "podolsk", "domodedovo", "himki", "balashiha", "lyubertsy"
            )
            for m in moscow_markers:
                if m in combined:
                    return False

        # 2. Проверяем совпадение с текущим регионом
        city_name = curr.get("name", "").lower()
        city_slug = curr.get("youla_slug", "").lower()

        target_aliases = [city_name, city_slug]
        if key:
            target_aliases.append(key)
        for alias, alias_key in CITY_ALIASES.items():
            if alias_key == key:
                target_aliases.append(alias)

        for alias in target_aliases:
            if not alias:
                continue
            stem = alias[:len(alias) - 1] if len(alias) > 4 else alias
            if stem in combined or alias in combined:
                return True

        # 3. Отсекаем явное упоминание других городов из базы
        for other_key, other_data in CITY_DATABASE.items():
            if other_key != key and other_key != "all_russia":
                other_name = other_data.get("name", "").lower()
                other_slug = other_data.get("youla_slug", "").lower()
                other_stem = other_name[:len(other_name) - 1] if len(other_name) > 4 else other_name
                if (other_stem and other_stem in loc_lower) or (other_slug and f"/{other_slug}/" in url_lower):
                    return False

        # По умолчанию (если город нейтральный или совпадает) разрешаем
        return True
