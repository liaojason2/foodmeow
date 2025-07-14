foodMultiple = 0.5
foodmeowVersion = "1.3.1 Beta 1"
category = {
    "food": {
        "cht_name": "食物",
        "addition": 0.5
    },
    "education": {
        "cht_name": "教育", 
        "addition": 0
    },
    "family_utility": {
        "cht_name": "家裡費用",
        "addition": 0
    },
    "family_support": {
        "cht_name": "家裡支援",
        "addition": 0
    },
    "borrow": {
        "cht_name": "代墊款",
        "addition": 0
    },
    "rent": {
        "cht_name": "房租",
        "addition": -1, #fix
    },
    "others": {
        "cht_name": "其他",
        "addition": 0
    }
}

def getFoodMultiple(): 
    return foodMultiple

def getFoodmeowVersion():
    return foodmeowVersion

# TODO: Change data structure to dictionary in dictionary and merge multiple
def getCategory():
    return category