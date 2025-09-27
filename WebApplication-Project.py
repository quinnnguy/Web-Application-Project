# Name: Ngoc Nguyen
# Email: nnguy20@uic.edu
# I hereby attest that I have adhered to the rules for quizzes and projects as well as UIC’s Academic Integrity standards. Signed: Ngoc Nguyen

"""
(1)
- Have a funtion called "scrape" which uses Beautiful Soup to scrape all names, emails, office hours, and teaching schedules of UIC MSCS faculty
- Save all information in a JSON file that is easy to read & search through
- If there is a pre-existing JSON file, running this function should erase it rift & then re-write the data to it. 
- Missing data should be left blank 

(2)
- Use Flask to create a website, allows user to search through MSCS faculty info in 2 different ways. 
- Use JSON file created earlier to search through data instead of web-scraping

    + 1st:  user should be able to enter name of a faculty member 
            & webpage should display their email address & office hours (if any)
    + 2nd:  your website should allow user to enter class name (like MCS 275) 
            & your website should display names of all faculty who are teaching MORE THAN ONE section of that class
            
"""
from bs4 import BeautifulSoup
import urllib3
from flask import Flask, render_template, request, redirect, url_for
import json

def scrape():
    """
    - Scrape all of the names, emails, office hours, and teaching schedules
    - Save all this information in a JSON file
    """
    
    http = urllib3.PoolManager()
    mscs_url = "https://mscs.uic.edu/people/faculty/"
    requested1 = http.request('GET', mscs_url)
    soup1 = BeautifulSoup(requested1.data.decode('utf-8'), "html.parser")
    
    people = soup1.find_all("div", attrs={"class":"_colB"})
    
    # Look for links to each falculty member
    links = []
    for p in people:
        links.append(p.find("span", attrs={"class":"_name"}).find("a")["href"])
    
    # Initialize lists to store information 
    names = []
    emails = [] 
    hours = []
    schedules = []
    
    for link in links:
        http = urllib3.PoolManager()
        requested2 = http.request('GET', link)
        soup2 = BeautifulSoup(requested2.data.decode('utf-8'), "html.parser")
        
        # Look for names 
        n_info = soup2.find("div", attrs={"class":"profile-header"}).find("div", attrs={"class":"_colB"}).find_next("h1").text
        
        names.append(n_info)
        
        # Look for email 
        e_info = soup2.find('h2', attrs = {'class' : '_label'}, text = 'Email:').find_next().text
        if e_info:
            emails.append(e_info)
        else:
            emails.append(None) # This will leave as "Null" in JSON file
    
        # Look for office hours
        try: 
            h_info = soup2.find("h2", text = "Office hours")
            get_h = h_info.find_next("p").text
            hours.append(get_h)
        except:
            hours.append(None)
    
    # Look for teaching schedules
        try: 
            s_info = soup2.find("h2", text = "Teaching schedule").find_next("ul")
            each_sche =[]
            for sche in s_info.find_all("li"):
                get_sche = sche.text.replace("\n","").strip()
                each_sche.append(get_sche)
            schedules.append(each_sche)
        except:
            schedules.append(None)
    
    # Create JSON file
    my_list = []

    num = len(names)
    for i in range(num):
        # Each faculty will have their own dictionary 
        each_member = {'Name': names[i] ,'Email': emails[i], 'Office Hours': hours[i], 'Teaching Schedules': schedules[i]}
        my_list.append(each_member) # Append dictionaries to the list
    
    with open("test.json", "w") as f:
        json.dump(my_list, f, indent = 2) # "Dump" the list into JSON file

    # Read the file
    with open("test.json", "r") as file:
        data = json.load(file)                                  
    
    app = Flask(__name__)

    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':                            # If method is POST
            user_input = request.form['user_input']             # Get user input from text box
            search_type = request.form['search_type']           # Get search type from the selection of radio button
            search_results = []
            if search_type == 'name':
                search_results = SearchByName(user_input)
            else:
                search_results = SearchByCourse(user_input)
            return render_template('index.html', user_input=user_input, search_type=search_type, faculties=search_results)
        else:                                                   # If method is GET
            return render_template('index.html')

    # Name (input) will be checked again each MSCS faculty member. If found a match, the faculty will be added to results.
    # More than one results will occur if user input contains in faculty's name. 
    def SearchByName(name):
        results = []
        for faculty in data:
            if(faculty['Name'].replace('  ',' ').find(name) != -1):         # When the result of find is other than -1, the faculty name contains the user input for name.
                results.append(faculty)
        return results


    # Course name (input) will be checked again each MSCS faculty teach schedules. If found a match, the counter will be incremented.
    # If the counter is more than one after checking, the faculty will be added to the results.
    def SearchByCourse(course_name):
        results = []
        for faculty in data:
            count = 0
            if faculty['Teaching Schedules'] != None:
                for course in faculty['Teaching Schedules']:
                    if(course.find(course_name) != -1):                    # When the result of find is other than -1, the course contains the user input for course.
                        count += 1
            
                if count > 1:                                              # Check this to return only faculty members who teach more than one sessions of the course.
                    results.append(faculty)
    
        return results

    if __name__ == '__main__':
        app.run(debug=True)
    



    