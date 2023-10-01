# import statements
from flask import Flask, request, Response
import json
app = Flask(__name__)

# data storage of all transactions for the current user
total_points = 0
points_system = list()

'''
home page that shows the current total points for the user
'''
@app.route('/')
def main_page():
    return("Your total points available are " + str(total_points) + ".")

'''
add points to the user account (transaction consists of payer, points, and timestamp)
'''
@app.route("/add", methods = ["POST"])
def add_points():
    global points_system
    global total_points
    points_dic = {"payer" : request.json["payer"],
                  "points" : request.json["points"],
                  "timestamp": request.json["timestamp"]}
    points_system.append(points_dic)
    # sort transactions by the timestamp
    points_system = sorted(points_system, key= lambda x: x["timestamp"])
    total_points += request.json["points"]
    return Response("", 200)

'''
spend points from payers in chronological order of the timestamps,
returns the points deducted from each payer
'''
@app.route("/spend", methods = ["POST"])
def spend_points():
    global points_system
    global total_points
    balance = request.json["points"]
    # return error statement if not enough points to spend in account
    if total_points < balance:
        return Response("Not enough points to spend", status = 400)
    else:
        ret_dict = dict()
        i = 0
        # keep looping through the transactions until number of points to spend are reached
        while balance > 0:
            # if payer points are less than or equal to spending points, set to 0 and continue
            if points_system[i]["points"] <= balance:
                balance -= points_system[i]["points"]
                reduction = points_system[i]["points"]
                points_system[i]["points"] = 0
            # else if current payer points are more than spending points, deduct from payer points
            else:
                points_system[i]["points"] -= balance
                reduction = balance
                balance = 0
            # add to a dictionary to keep track of points deducted
            if points_system[i]["payer"] not in ret_dict:
                ret_dict[points_system[i]["payer"]] = -1 * reduction
            else:
                ret_dict[points_system[i]["payer"]] += -1 * reduction
            total_points -= reduction
            i += 1
        ret_list = list()
        # convert to list of dictionary for returning purposes (with title, ex: 'payer')
        for key, val in ret_dict.items():
            ret_list.append({"payer" : key, "points" : val})
        return json.dumps(ret_list), 200

'''
return the balance of points per payer
'''
@app.route("/balance", methods = ["GET"])
def balance_points():
    global points_system
    global total_points
    ret_dict = dict()
    for transaction in points_system:
        if transaction["payer"] not in ret_dict:
            ret_dict[transaction["payer"]] = transaction["points"]
        else:
            ret_dict[transaction["payer"]] += transaction["points"]
    return json.dumps(ret_dict), 200



# run application
if __name__ == '__main__':
    app.run(port = 8000 , debug=True)