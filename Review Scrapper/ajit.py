from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq

app = Flask(__name__)


@app.route('/',methods=["GET"])
@cross_origin()
def homepage():
    return render_template("index.html")

@app.route('/review',methods=['POST','GET'])
@cross_origin
def index():
    if request.method == 'POST':
        try:
            searchstring = request.form['content'].replace(' ','')
            flipkart_url = "https://www.flipkart.com/search?q=" + searchstring
            uclient = uReq(flipkart_url)
            flipkart_page = uclient.read()
            uclient.close()
            flipkart_html = bs(flipkart_page,'html.parser')
            bigboxes = flipkart_html.find_all("div", {"class": "_1AtVbE col-12-12"})
            box = bigboxes[3]
            product_link = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(product_link)
            prod_html = bs(prodRes.text,'html.parser')
            commentboxes = prod_html.find_all("div",{"class":"_16PBlm"})
            filename = searchstring + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews=[]
            for commentbox in commentboxes:
                try:
                   name = commentbox.find_all("p", {"class": "_2sc7ZR _2V5EHH"})[0].text

                except:
                   name = 'No Name'

                try:
                   rating = commentbox.find_all("div", {"class": "_3LWZlK _1BLPMq"})[0].text

                except:
                   rating = "No Rating"

                try:
                   commenthead = commentbox.find_all('p', {'class': '_2-N8zT'})[0].text

                except:
                   commenthead = "No Comment Heading"

                try:
                   comment = commentbox.find_all("div", {"class": ""})[0].div.text

                except:
                   comment = "No Comment"

                mydict = {"Product": searchstring, "Name": name, "Rating": rating, "CommentHead": commenthead,
                          "Comment": comment}
                reviews.append(mydict)

            return render_template('results.html',reviews = reviews)

        except Exception as e:
            print("The Exception message is ",e)
            return 'Something is wrong'

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8001, debug=True)
