import json

import dash
import dash_mantine_components as dmc
import feffery_antd_components as fac
from dash import Input, Output, callback, html

app = dash.Dash(__name__)

SECTION_STYLE = {"display": "flex", "flexDirection": "row", "gap": "16px", "alignItems": "flex-start"}
CODE_STYLE = {"flex": "1", "minWidth": "0"}
SELECTOR_STYLE = {"width": "300px", "flexShrink": "0"}

_STRUCTURE = {
    "Electronics": {
        "Phones": ["iPhone 15", "iPhone 14", "Samsung Galaxy S24", "Pixel 8", "OnePlus 12", "Xiaomi 14", "Sony Xperia 1", "Nokia G60", "Motorola Edge", "Fairphone 5"],
        "Laptops": ["MacBook Pro", "MacBook Air", "ThinkPad X1", "Dell XPS 15", "HP Spectre", "Surface Pro", "Asus ZenBook", "Razer Blade", "LG Gram", "Acer Swift"],
        "Tablets": ["iPad Pro", "iPad Air", "Samsung Tab S9", "Surface Go", "Kindle Fire", "Lenovo Tab P12", "Huawei MatePad", "Amazon Echo Show", "Xiaomi Pad 6", "OnePlus Pad"],
        "TVs": ["Samsung QLED", "LG OLED", "Sony Bravia", "Philips Ambilight", "Hisense U8K", "TCL 6-Series", "Panasonic OLED", "Bang & Olufsen", "Vizio P-Series", "Sharp Aquos"],
        "Audio": ["AirPods Pro", "Sony WH-1000XM5", "Bose QC45", "Sennheiser HD800", "Jabra Evolve2", "Bang & Olufsen H95", "Beats Studio", "Audio-Technica ATH", "Shure SE846", "Beyerdynamic DT900"],
        "Cameras": ["Canon EOS R5", "Nikon Z9", "Sony A7 IV", "Fujifilm X-T5", "Leica M11", "Panasonic S5", "Olympus OM-1", "Ricoh GR IIIx", "Hasselblad X2D", "Phase One IQ4"],
        "Gaming": ["PS5", "Xbox Series X", "Nintendo Switch", "Steam Deck", "Asus ROG Ally", "Meta Quest 3", "Razer Edge", "Logitech G Cloud", "Backbone One", "GameSir X2"],
        "Wearables": ["Apple Watch Ultra", "Galaxy Watch 6", "Garmin Fenix 7", "Fitbit Sense 2", "Polar Vantage V3", "Suunto Race", "Coros Vertix 2", "Whoop 4", "Oura Ring", "Amazfit GTR 4"],
        "Smart Home": ["Nest Thermostat", "Ring Doorbell", "Philips Hue", "Amazon Echo", "Google Home", "Arlo Camera", "Eufy RoboVac", "August Lock", "Lutron Caseta", "Sonos One"],
        "Networking": ["Eero Pro 6E", "Netgear Orbi", "Asus ZenWiFi", "TP-Link Deco", "Ubiquiti UniFi", "Google Nest WiFi", "Linksys Velop", "Synology Router", "Aruba Instant On", "MikroTik hAP"],
    },
    "Clothing": {
        "Tops": ["Oxford Shirt", "Polo Shirt", "Linen Shirt", "Flannel Shirt", "Crew T-Shirt", "V-Neck T-Shirt", "Henley", "Turtleneck", "Tank Top", "Compression Shirt"],
        "Bottoms": ["Slim Jeans", "Straight Jeans", "Chinos", "Cargo Pants", "Joggers", "Dress Trousers", "Shorts", "Linen Trousers", "Corduroy Pants", "Sweatpants"],
        "Outerwear": ["Puffer Jacket", "Trench Coat", "Wool Overcoat", "Denim Jacket", "Bomber Jacket", "Raincoat", "Fleece", "Peacoat", "Windbreaker", "Parka"],
        "Footwear": ["Running Shoes", "Leather Boots", "Chelsea Boots", "Loafers", "Sneakers", "Sandals", "Hiking Boots", "Oxford Shoes", "Slip-Ons", "Derby Shoes"],
        "Activewear": ["Running Tights", "Sports Bra", "Gym Shorts", "Yoga Pants", "Compression Top", "Track Jacket", "Swimming Trunks", "Cycling Jersey", "Tennis Skirt", "Hiking Pants"],
        "Formal": ["Suit Jacket", "Dress Shirt", "Waistcoat", "Tuxedo", "Dress Trousers", "Blazer", "Cummerbund", "Tie", "Bow Tie", "Pocket Square"],
        "Knitwear": ["Cashmere Jumper", "Cable Knit", "Cardigan", "Merino Wool", "Fair Isle", "Chunky Knit", "Turtleneck Knit", "Zip-Up Knit", "Shawl Collar", "Fisherman Knit"],
        "Accessories": ["Leather Belt", "Canvas Belt", "Silk Scarf", "Wool Scarf", "Baseball Cap", "Beanie", "Panama Hat", "Fedora", "Gloves", "Sunglasses"],
        "Underwear": ["Boxer Briefs", "Trunks", "Briefs", "Thermal Top", "Thermal Bottoms", "Vest", "Long Johns", "Sports Socks", "Dress Socks", "No-Show Socks"],
        "Swimwear": ["Board Shorts", "Swim Briefs", "Rash Guard", "Wetsuit Top", "Swim Shorts", "One-Piece", "Bikini Top", "Bikini Bottom", "Cover-Up", "Swim Cap"],
    },
    "Food": {
        "Fruit": ["Apple", "Banana", "Orange", "Mango", "Pineapple", "Strawberry", "Blueberry", "Watermelon", "Grape", "Peach"],
        "Vegetables": ["Carrot", "Broccoli", "Spinach", "Tomato", "Cucumber", "Pepper", "Courgette", "Aubergine", "Cauliflower", "Kale"],
        "Meat": ["Chicken Breast", "Beef Mince", "Lamb Chops", "Pork Belly", "Duck Breast", "Turkey", "Venison", "Rabbit", "Veal", "Quail"],
        "Fish": ["Salmon", "Cod", "Tuna", "Sea Bass", "Mackerel", "Haddock", "Trout", "Halibut", "Sardines", "Prawns"],
        "Dairy": ["Whole Milk", "Skimmed Milk", "Cheddar", "Brie", "Parmesan", "Greek Yoghurt", "Butter", "Cream", "Mozzarella", "Feta"],
        "Bakery": ["Sourdough", "Baguette", "Croissant", "Bagel", "Rye Bread", "Ciabatta", "Focaccia", "Brioche", "Pita", "Naan"],
        "Pasta & Grains": ["Spaghetti", "Penne", "Risotto Rice", "Basmati Rice", "Quinoa", "Couscous", "Bulgur Wheat", "Polenta", "Orzo", "Farro"],
        "Snacks": ["Crisps", "Popcorn", "Pretzels", "Trail Mix", "Rice Cakes", "Hummus", "Granola Bar", "Dark Chocolate", "Nuts", "Crackers"],
        "Drinks": ["Sparkling Water", "Orange Juice", "Oat Milk", "Coconut Water", "Green Tea", "Espresso", "Kombucha", "Smoothie", "Craft Beer", "Prosecco"],
        "Condiments": ["Olive Oil", "Soy Sauce", "Sriracha", "Mustard", "Ketchup", "Mayonnaise", "Balsamic Vinegar", "Fish Sauce", "Tahini", "Miso Paste"],
    },
}


def _make_key(title):
    return title.lower().replace(" ", "-").replace("&", "and")


def _expand_to_50(items):
    """Extend a list of seed names to 50 items by appending numbers to seeds."""
    result = list(items)
    i = 2
    while len(result) < 50:
        result.append(f"{items[i % len(items)]} {i}")
        i += 1
    return result[:50]


TREE_DATA = [
    {
        "title": category,
        "key": _make_key(category),
        "value": _make_key(category),
        "children": [
            {
                "title": subcategory,
                "key": _make_key(subcategory),
                "value": _make_key(subcategory),
                "children": [
                    {"title": item, "key": _make_key(item), "value": _make_key(item)}
                    for item in _expand_to_50(items)
                ],
            }
            for subcategory, items in subcategories.items()
        ],
    }
    for category, subcategories in _STRUCTURE.items()
]

CASCADER_OPTIONS = [
    {
        "label": node["title"],
        "value": node["value"],
        "children": [
            {
                "label": child["title"],
                "value": child["value"],
                "children": [
                    {"label": grandchild["title"], "value": grandchild["value"]}
                    for grandchild in child.get("children", [])
                ],
            }
            for child in node.get("children", [])
        ],
    }
    for node in TREE_DATA
]

DMC_TREE_DATA = CASCADER_OPTIONS  # dmc.Tree uses the same label/value/children format

app.layout = dmc.MantineProvider(
    html.Div(
        [
            html.H2("AntdTreeSelect"),
            html.Div(
                [
                    fac.AntdTreeSelect(
                        id="tree-select",
                        treeData=TREE_DATA,
                        placeholder="Select items...",
                        treeCheckable=True,
                        showCheckedStrategy="show-child",
                        locale="en-us",
                        listHeight=300,
                        maxTagCount="responsive",
                        style=SELECTOR_STYLE,
                    ),
                    dmc.CodeHighlight(id="tree-output", code="null", language="json", style=CODE_STYLE),
                ],
                style=SECTION_STYLE,
            ),
            html.H2("AntdCascader"),
            html.Div(
                [
                    fac.AntdCascader(
                        id="cascader",
                        options=CASCADER_OPTIONS,
                        placeholder="Select category...",
                        multiple=True,
                        showCheckedStrategy="show-child",
                        locale="en-us",
                        maxTagCount="responsive",
                        style=SELECTOR_STYLE,
                    ),
                    dmc.CodeHighlight(id="cascader-output", code="null", language="json", style=CODE_STYLE),
                ],
                style=SECTION_STYLE,
            ),
            html.H2("dmc.Tree"),
            html.Div(
                [
                    dmc.Tree(
                        id="dmc-tree",
                        data=DMC_TREE_DATA,
                        checkboxes=True,
                        style=SELECTOR_STYLE,
                    ),
                    dmc.CodeHighlight(id="dmc-tree-output", code="null", language="json", style=CODE_STYLE),
                ],
                style=SECTION_STYLE,
            ),
        ],
        style={"padding": "20px", "display": "flex", "flexDirection": "column", "gap": "24px"},
    )
)


@callback(Output("tree-output", "code"), Input("tree-select", "value"))
def show_tree_value(value):
    return json.dumps(value, indent=2)


@callback(Output("cascader-output", "code"), Input("cascader", "value"))
def show_cascader_value(value):
    # AntdCascader always returns the full path for each selection e.g. [["electronics", "phones", "iphone"]].
    # Unlike AntdTreeSelect, there is no prop to flatten this to just leaf values — a callback would be needed.
    return json.dumps(value, indent=2)


@callback(Output("dmc-tree-output", "code"), Input("dmc-tree", "checked"))
def show_dmc_tree_checked(checked):
    # dmc.Tree only allows leaves to be checked, so checked is already a flat list of leaf values.
    return json.dumps(checked, indent=2)


if __name__ == "__main__":
    app.run(debug=True)
