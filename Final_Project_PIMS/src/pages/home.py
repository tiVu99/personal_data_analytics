import streamlit as st
import pandas as pd

def write():
    """Used to write the page in the app.py file"""
    with st.spinner("Loading Home ..."):
        st.balloons()
        st.subheader('Personal Information Management System (PIMS)')

    st.info('This application will provide you with some analytics on you personal data!')
    st.warning('Before going to Exploration Page, you will need to download datasets and get them ready for uploading!')

    st.markdown(' :calendar: For `calendar data`, we will use the data exported from Microsoft Outlook as CSV file.')

    st.markdown('Go to Microsoft Outlook App, '
                '_Select File_ -> _Open & Export_ '
                '-> _Import/Export_ ->  _Select Export to a file_ '
                '-> _Select Comma Separated Value (CSV)_ -> _My Timetable_ '
                '-> _Save Exported File_  -> _Set Date Range_ -> _Ready to Download_')
    st.markdown(':clipboard: For `Google data` including `Browser History`, `My Activity`, `Email`, we will need to download the data from [Google TakeOut](https://takeout.google.com/settings/takeout?pli=1)')

    st.markdown('1. For `Browser History` and `Bookmarks` -> Select `Chrome` -> Select `Browser History` and `Bookmarks` -> Create export -> Download')
    st.markdown('2. For `My Activity`, we only use `Chrome`, `Gmail`, `Search`, `YouTube`, -> Select all of these sources -> Create export -> Download')
    st.error(':fire: Remember to change the file format to JSON on activity records')
    st.markdown('3. For `Email`, as we do not want to download all the emails, you need to go to `Gmail` to filter and label some of them (ex. Inbox YTD)')
    st.markdown('Then you can go back to `Google TakeOut` -> Select the label you just created -> Create export -> Download')

    st.warning(":clock1: This will take a few minutes up to 10/15 mins depends on your file size")
    st.success(":wink: Now you have got the datasets, let's go the Exploration Page!")