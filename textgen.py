import sys
import csv
from g4f.client import Client
from pathlib import Path
import re


KEY_WORD = sys.argv[1]
RATING_ITERATIONS = int(sys.argv[2])

# file_path = str(Path(__file__).parent.resolve()) + "\\" + KEY_WORD + '.csv'
analysis_path = "C:\\Users\\Abishta\\Documents\\YIS\\analysis.csv"
info_path = "C:\\Users\\Abishta\\Documents\\YIS\\stock_list.csv"
# if not Path(file_path).is_file():
#     print("CSV does not exist, Creating file...")
#     with open(file_path, mode = "w") as csvfile:
#         fieldnames = ["ticker", "rating", "info"]
#         writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
#         writer.writeheader()
#     print("CSV Made! Restart program")
#     exit()
    
print("Reading File...")
def readData(file_path):
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        rows = list(reader)
        return rows
analysis_rows = readData(analysis_path)
info_rows = readData(info_path)

def writeData(index, rating, ETFinfo, file_path, rows):
    # rows = readData(file_path)
    rows[index][1] = rating
    rows[index][2] = ETFinfo.choices[0].message.content

    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
    return rows

def responseParse(response):
    letters = "abcdefgh"
    returned = {}
    for i in range(len(response)):
        cLetter = response[i]
        number = ""
        if cLetter in letters and len(response) != i-1:
            if response[i+1] == "(":
                j = 2
                while True:
                    if response[i+j] == ")":
                        break
                    number += response[i+j]
                    j+=1
                returned[cLetter] = int(number)
    return returned

for i in range(len(info_rows)):
    ticker=info_rows[i][0]
    if ticker == "ticker":
        continue

    client = Client()
    ETFinfo = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
                {"role": "assistant", "content": 
                    f"""
                        {info_rows[0][0]} : {info_rows[i][0]}\n
                        {info_rows[0][1]} : {info_rows[i][1]}\n
                        {info_rows[0][2]} : {info_rows[i][2]}\n
                        {info_rows[0][3]} : {info_rows[i][3]}\n
                        {info_rows[0][4]} : {info_rows[i][4]}\n
                        {info_rows[0][5]} : {info_rows[i][5]}\n
                        {info_rows[0][6]} : {info_rows[i][6]}\n
                        {info_rows[0][7]} : {info_rows[i][7]}\n
                        {info_rows[0][8]} : {info_rows[i][8]}\n
                        {info_rows[0][9]} : {info_rows[i][9]}\n
                        Please provide a summary of this fund and provide each of these topics in your summary: Fund Geographical Focus, Fund Industry Focus, Fund Asset Class Focus, Fund Market Cap Focus, Strategy, Expense Ratio, Maturity Band, Fund Rating Class Focus
                    """
                }],
        temperature=.8,
    )
    print(ticker + "\t" + "Sum. Asked")

    question = ETFinfo.choices[0].message.content + "\n" + f"Rate what you think about this ETF in terms of how much it encompasses these topics: Fund Geographical Focus (a), Fund Industry Focus (b), Fund Asset Class Focus (c), Fund Market Cap Focus (d), Strategy (e), Expense Ratio (f), Maturity Band (g), Fund Rating Class Focus (h)"
    
    numRating = 0
    a = b = c = d = e = f = g = h = 0
    working = RATING_ITERATIONS

    for j in range(RATING_ITERATIONS):
        client = Client()
        rating = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                    {"role": "system", "content": 
                     """
                     For the following messages I will ask you to rate something based on some topics \n
                     The question will be along the lines of <topic> (<letter>)\n
                     And your rating should be <letter>(<rating>) \n
                     Each rating should be a number between 1-100 \n
                     So if I were to ask you 'Rate a cake based on the topics of icing (a), creaminess (b), and deliciousness (c)'\n
                     You would respond with a rating like: \n
                     a(<rating for icing>)\n
                     b(<rating for creaminess>)\n 
                     c(<rating for deliciousness>)\n
                     ONLY respond in this format and do not include any words in your response
                     """
                     },
                    {"role": "user", "content": question}],
            temperature=.8,
        )
        print(ticker + "\t" +  "Rat. Asked\t" + f"\tIt. {j+1}")

        error = rating.choices[0].message.content
        formatted = responseParse(rating.choices[0].message.content)
        print(str(formatted))
        # try:
        #     pattern = r'\d+'
        #     match = re.search(pattern, rating.choices[0].message.content)
        #     if match:
        #         first_number = int(match.group())
        # except:
        #     working -= 1
        #     print(ticker+"\t"+f"ERROR: Response {j+1} included no rating")
        # else:
        #     pattern = r'\d+'
        #     match = re.search(pattern, rating.choices[0].message.content)
        #     print(ticker + "\t" +  "Rat. Given\t" + f"\t{match}")
        #     if match:
        #         sum += int(match.group())
        a = formatted["a"]
        b = formatted["b"]
        c = formatted["c"]
        d = formatted["d"]
        e = formatted["e"]
        f = formatted["f"]
        g = formatted["g"]
        h = formatted["h"]

        numRating = (
            formatted["a"] * .01 * .30 +
            formatted["b"] * .01 * .25 +
            formatted["c"] * .01 * .15 +
            formatted["d"] * .01 * .10 +
            formatted["e"] * .01 * .10 +
            formatted["f"] * .01 * .05 +
            formatted["g"] * .01 * .03 +
            formatted["h"] * .01 * .02
        )

            
  
    numRating /= working
    a /= working
    b /= working
    c /= working
    d /= working
    e /= working
    f /= working
    g /= working
    h /= working
    numRating = str(numRating)
    print(numRating)

    if working == 0:
        writeData(i, error, ETFinfo)
    else:
        writeData(i, numRating, ETFinfo)
    print(ticker+"\t"+"Rating finished. Writing Data...")
    writeData(i, numRating, ETFinfo)





