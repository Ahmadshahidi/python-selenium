
# Python + Selenium Complex Web Scraping
have you ever tried to download JavaScript embedded pdfs from a website with proxy,
 authentication, certificate verification, cookies, and other safeguards implemented
 all together? If your answer is yes then you know why I have the word "complex" in then
 title :wink:.

 This instruction is written to help me remember what I did when I was working on a project
 that required such a downloading and hopefully help others who might be searching and
 stumble upon this git-page. Obviously the webpages, usernames, and passwords mentioned in the codes are
 just made-up and need to be adjusted in any real application.

 ## Set Up:
 - **Chrome headless + Chrome driver:** use the most recent versions.
 - **Selenium + Python 3.7**
 Let's start by necessary imports:
```
import time,os
 import lxml,html
 from selenium import webdriver
 from selenium.webdriver.chrome.options import Options
 from urllib.parse import urljoin
```

 ## Set up the chrome options:
 You will need to download the **chromedriver** and point to its location. I realized that sometimes for Linux users it is required to
 run a 'chmod +x' on the downloaded file for it to be executable. If you are using windows just place the exe file somewhere and point to it.

```{python}
chrome_options = Options()
 chrome_options.add_argument('--headless')
 chrome_options.add_argument('--no-sandbox')
 chrome_options.add_argument('--disable-dev-shm-usage')
 driver = webdriver.Chrome('path/to/chromedriver',option = chrome_options)
 # For windows users I found out that (r"C:\path\to\chromedriver.exe") works the best.
```

 Next we setup a download directory:

```{python}
download_dir = "path/to/it"
if not os.path.exists(download_dir):
  os.mkdir(download_dir)
```

For security reasons chrome in headless mode does not automatically download files, and since there is no browser window to click for download, we have to manually set the default to download upon opening a file's link.

```{python}
driver.command_executor._commands["send_command"] = (
  "POST",
  '/session/$sessionId/chromium/send_command'
  )
  params = {
    'cmd': 'Page_setDownloadBehavior',
    'params':{
      'behavior': 'allow'
      'downloadPath': download_dir
    }
  }
  driver.execute("send_command",params)
```

We are almost ready to start. We use the selenium to quietly start a browser window and the log into it. While it might be possible to use the *requests* package to log in, but I couldn't do so. The website I was dealing with had complex security features. For example several javascripts runs to determine the access level before letting a user in. While it might be possible to run those scripts and take care of the other complexities using non browser tools, I at the end thought the best way is to just use a browser in the headless mode which by the way is very fast and can be run on a server without X. This last requirement was the reason that I had to use the headless browser (yes I tried PhantomJs, without any luck. It could not properly handle those javascripts I mentioned earlier).

```{python}
base_url = 'https://verysecure.come/stuff/'
username = 'abc_andmore'
password = '123_andevenmore'
driver.get(base_url)
time.sleep(3) # make sure the browser - although in headless mode - is ready
passw = driver.find_element_by_xpath("//input[@name='password']") # you might have to change this. Inspect element first
userid = driver.find_element_by_xpath("//input[@name='username']")# same as above
loginbtn = driver.find_elemt_by_xpath("//input[@name='submitButton']")


userid.send_keys(username)
passw.send_key(password)
loginbtn.click()
```


Hopefully you are now logged in. The site I was dealing with had different frames. I had to click on a link in one frame that would open a window in another frame which then I could fill and submit to get to the desired page with documents' links. You have to switch between frames and the best way to know which frame you are in and which one you want to switch is to inspect the source of the webpage in a browser window and use the tools provided to inspect and trace changes.

```{python}
crt_url = driver.current_url
driver.get(crt_url)
driver.switch_to.frame(driver.find_element_by_name("idx")) #switch to the first frame
driver.find_element_by_link_text("linkText").click() # in this frame click on the link which opens a form in another frame
driver.switch_to_default.content() # switch back to the default and then switch to the second frame
driver.switch_to.frame(driver.find_element_by_xpath("//frame[@name='body']")) # do your own find_element
```

At this point I had a form opened in which I could submit different information about the case that I was looking to download materials belonging to it. Here I assume you have a *caseId* and a *folderId* that need to be submitted.

```{python}
caseId = driver.find_element_by_xpath("//input[@name='caseId']")
folderId = driver.find_element_by_xpath("//input[@name='folderId']")
caseId.send_keys["the caseid"]
folderId.send_keys["the folderid"]
driver.find_element_by_xpath("//input[@name='listDocs']").click() # or submit or whatever. Always inspect the element to find out
```

Now you should have be in the page with links to the desired pdfs. In my case, I had a page with several links each link containing a pdf. using a browser one can click and open the documents, but the main difficulty is that these links are URI's generated by a javascript function. In order to access them one has to first run the javascript and generate the links which are usually *base_url+javascript embedded uri*. Here is the result of the code to do that.

```{python}
html = driver.page_source # getting the page source to process later
dom = lxml.html.fromstring(html)
links = [] # using listcomp will be more concise but we go for readability here
for link in dom.xpath("//a[text() = 'textLink']@herf"): #select the url in herf for all a tags(links)
  links.append(link)

full_links = [urljoin(base_url,link) for link in links]

source_links = []
for f_links in full_links:
  r = driver.get(f_link)
  innerHTML = driver.execute_script("return document.body.innerHTML")# run the javascript and return the generated html.
  source_links.append(innerHTML)

pdf_links = []
for sl in source_links:
  begin = sl.find("https") #figuring out where the links are
  end = sl.find(".pdf")+4
  pdf_links.append(sl[begin:end])

for pdf in pdf_links:
  driver.get(pdf)   # we already configured the driver to download

driver.close
```
