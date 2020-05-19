def submit_dates(browser, start_date, end_date):
    import time
    from selenium.webdriver.common.keys import Keys
    
    archive_form = browser.find_element_by_xpath("//form[@id='aspnetForm']")
    # Get start/end date entry forms and submit start and end date
    text_boxes = archive_form.find_elements_by_class_name("riTextBox")
    text_boxes[0].send_keys(start_date)
    time.sleep(1)
    text_boxes[0].send_keys(Keys.RETURN)
    time.sleep(1)
    archive_form = browser.find_element_by_xpath("//form[@id='aspnetForm']")
    # Get start/end date entry forms and submit start and end date
    text_boxes = archive_form.find_elements_by_class_name("riTextBox")
    text_boxes[1].send_keys(end_date)
    time.sleep(1)
    text_boxes[1].send_keys(Keys.RETURN)
    
    archive_form = browser.find_element_by_xpath("//form[@id='aspnetForm']")
    # Get start/end date entry forms and submit start and end date
    text_boxes = archive_form.find_elements_by_class_name("riTextBox")
    text_boxes[0].send_keys(start_date)
    time.sleep(1)
    text_boxes[0].send_keys(Keys.RETURN)
    time.sleep(1)
    archive_form = browser.find_element_by_xpath("//form[@id='aspnetForm']")
    # Get start/end date entry forms and submit start and end date
    text_boxes = archive_form.find_elements_by_class_name("riTextBox")
    text_boxes[1].send_keys(end_date)
    time.sleep(1)
    text_boxes[1].send_keys(Keys.RETURN)
    
    # Drop escalator and elevator data
    escalator_box = browser.find_element_by_css_selector('#ctl00_ContentPlaceHolder1_chkHideElevatorEscalator')
    escalator_box.click()
    
    #Get the update button
    update_button = browser.find_element_by_xpath("//input[@value='Update']")
    
    time.sleep(1)
    update_button.click()
    
# Scrape the data from a given browser while iterating through all the pages
def scrape_data(browser, verbose = True):
    import progressbar
    import sys
    import time
    
    current_page = 1
    last_page = int(browser.find_element_by_css_selector('#ctl00_ContentPlaceHolder1_gridMessages_ctl00 > thead > tr.rgPager > td > div > div.rgWrap.rgInfoPart > strong:nth-child(2)').text)
    # Row follow the format of: '','Date','Agency','Subject','Message'
    AGENCY = 'NYC'

    data_rows = []

    if verbose:
        widgets = [progressbar.Percentage(), progressbar.Bar(), progressbar.Variable('date')]
        bar = progressbar.ProgressBar(widgets=widgets, max_value=last_page).start()
                                      
    while current_page != last_page:
        results_table = browser.find_element_by_xpath("//table[@class='rgMasterTable rgClipCells']")

        # Figure out where we are in the results
        page_list = results_table.find_element_by_class_name("rgNumPart")
        current_page = int(page_list.find_element_by_class_name("rgCurrentPage").text)
        
        #print("On page {} of {}".format(current_page, last_page))

        for row in results_table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr'):
            data = [c.text for c in row.find_elements_by_tag_name('td')]

            # Only collect data for the specific agency, drop SIR
            if data[2] == AGENCY and 'SIR' not in data[3]:
                data_rows.append(data[1:])

        #print("Last date processed {}".format(data[1]))
        if verbose:
            sys.stdout.flush()
            bar.update(current_page, date=data[1].split()[0])
        # Had some issues finding the next_button, so just use css_selector copied from chrome dev tools
        next_button = browser.find_element_by_css_selector('#ctl00_ContentPlaceHolder1_gridMessages_ctl00 > tfoot > tr.rgPager > td > div > div.rgWrap.rgArrPart2 > button.t-button.rgActionButton.rgPageNext')        
        next_button.click()

    if verbose:
        bar.finish()

    return data_rows