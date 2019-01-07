#
import time,os
import lxml,html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin

def downloader( user_id, pass_id, caseId, folderId):
    hrome_options = Options()
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--no-sandbox')
   chrome_options.add_argument('--disable-dev-shm-usage')
   driver = webdriver.Chrome('path/to/chromedriver',option = chrome_options)
   # For windows users I found out that (r"C:\path\to\chromedriver.exe") works the best.
   download_dir = "path/to/it"
   if not os.path.exists(download_dir):
     os.mkdir(download_dir)

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

  base_url = 'https://verysecure.come/stuff/'
  username = user_id
  password = pass_id
  driver.get(base_url)
  time.sleep(3) # make sure the browser - although in headless mode - is ready
  passw = driver.find_element_by_xpath("//input[@name='password']") # you might have to change this. Inspect element first
  userid = driver.find_element_by_xpath("//input[@name='username']")# same as above
  loginbtn = driver.find_elemt_by_xpath("//input[@name='submitButton']")


  userid.send_keys(username)
  passw.send_key(password)
  loginbtn.click()

  crt_url = driver.current_url
  driver.get(crt_url)
  driver.switch_to.frame(driver.find_element_by_name("idx")) #switch to the first frame
  driver.find_element_by_link_text("linkText").click() # in this frame click on the link which opens a form in another frame
  driver.switch_to_default.content() # switch back to the default and then switch to the second frame
  driver.switch_to.frame(driver.find_element_by_xpath("//frame[@name='body']")) # do your own find_element

  caseId = driver.find_element_by_xpath("//input[@name='caseId']")
  folderId = driver.find_element_by_xpath("//input[@name='folderId']")
  caseId.send_keys["the caseid"]
  folderId.send_keys["the folderid"]
  driver.find_element_by_xpath("//input[@name='listDocs']").click() # or submit or whatever. Always inspect the element to find out

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
