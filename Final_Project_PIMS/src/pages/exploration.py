import base64
import csv
import collections
import io
import altair as alt
import streamlit as st
import pandas as pd
import json
import datetime
import numpy as np
import seaborn as sns
import streamlit.components.v1 as components
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import rcParams


def select_source():
    st.info("Please select a source for analytics")
    sources = st.selectbox('Select', ['Calendar' , 'Browser History', 'My Activity', 'Email', 'Bookmarks'])
    if sources == "Calendar":
        upload_data_csv()
    if sources == "Browser History":
        upload_data_json()
    if sources == "Email":
        upload_data_mbox()
    if sources == "My Activity":
        upload_data_activity_json()
    if sources == "Bookmarks":
        upload_data_html()

def upload_data_csv():
    st.info(":smile: Please upload your dataset")
    dataset_file = st.file_uploader("Upload a file", type=["csv"])
    st.warning('Please make sure you uploaded the right dataset')

    if dataset_file:
        st.success('File uploaded')
        if st.checkbox('Show raw data'):
            show_raw_data_csv(dataset_file)
        elif st.checkbox('Preview transformed data'):
            transform_calendar_csv(dataset_file)
    else:
        st.error('No file is uploaded')


def upload_data_json():
    st.info(":smile: Please upload your dataset")
    dataset_file = st.file_uploader("Upload a file", type=["json"])
    st.warning('Please make sure you uploaded the right dataset')

    if dataset_file:
        st.success('File uploaded')
        transform_browser_json(dataset_file)
    else:
        st.error('No file is uploaded')


def upload_data_mbox():
    st.info(":smile: Please upload your dataset")
    dataset_file = st.file_uploader("Upload a file", type=["mbox"])
    st.warning('Please make sure you uploaded the right dataset')

    if dataset_file:
        st.success('File uploaded')
        # transform_email_mbox(dataset_file)
    else:
        st.error('No file is uploaded')


def upload_data_activity_json():
    st.info(":smile: Please upload your datasets")

    multiple_files = st.file_uploader('Multiple File Uploader', type="json", accept_multiple_files=True)
    if st.checkbox("Show raw data"):
        for file in multiple_files:
            data = json.load(file)
            df = pd.json_normalize(data)
            file.seek(0)
            st.dataframe(df.head())
        st.warning('My Activity datasets should include Chrome, Search, Gmail and YouTube')

        if len(multiple_files) == 4:
            st.success('All files uploaded')
            transform_activity_json(multiple_files)
        else:
            st.error('Missing file')


def upload_data_html():
    filename = st.text_input('Enter a file path:')

    if filename:
        HtmlFile = open(filename, 'r', encoding='utf-8')
        source_code = HtmlFile.read()
        components.html(source_code, width=800, height=800, scrolling=True)
    else:
        st.error('No file is uploaded')


def show_raw_data_csv(file):
    df = pd.read_csv(file)
    df = df.dropna(axis='columns')
    st.write("### Enter the number of rows to view")
    rows = st.number_input("", min_value=0, value=5)
    if rows > 0:
        st.subheader('Raw data')
        st.dataframe(df.head(rows))


def transform_calendar_csv(file):
    df = pd.read_csv(file)
    df = df.dropna(axis='columns')
    df = df.drop(['All day event', 'Reminder on/off', 'Reminder Date', 'Reminder Time', 'Description', 'Private',
                  'Show time as'], axis=1)
    df['Start Date'] = pd.to_datetime(df['Start Date'], format='%d/%m/%Y')
    df['End Date'] = pd.to_datetime(df['End Date'], format='%d/%m/%Y')
    st.dataframe(df.head())
    filter_by_date_calendar(df, df['Start Date'])


def transform_browser_json(file):
    if st.checkbox('Preview transformed data'):
        data = json.load(file)

        df = pd.json_normalize(data, record_path=['Browser History'])

        df = df.drop(['favicon_url', 'client_id'], axis=1)
        # st.write(df.dtypes)
        df['time_usec'] = pd.to_datetime(df['time_usec'] / 1000, unit='ms')
        df['date'] = pd.to_datetime(df['time_usec']).dt.date
        df['time'] = pd.to_datetime(df['time_usec']).dt.time
        df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
        # df['date'] = df["date"].dt.strftime("%d/%m/%Y")
        # df['date'] = pd.to_datetime(df['date'], format="%d/%m/%Y")
        # st.write(df.dtypes)
        df = df.drop('time_usec', axis=1)
        st.dataframe(df.head())
        filter_by_date_browser(df, df['date'])


# def transform_email_mbox(file):
#     if st.checkbox('Preview transformed data'):
#         pass

def transform_activity_json(multiplefiles):
    df_list = []
    if st.checkbox('Preview transformed data'):
        for file in multiplefiles:
            data = json.load(file)
            df = pd.json_normalize(data)
            df = df.drop(['products', 'titleUrl'], axis=1)
            df = df.dropna(axis='columns')
            df['time'] = pd.to_datetime(df['time'])
            df['date'] = pd.to_datetime(df['time']).dt.date
            df['time_in_day'] = pd.to_datetime(df['time']).dt.time
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
            # df['time_in_day'] = pd.to_datetime(df['time_in_day'])
            file.seek(0)
            df_list.append(df)
        final_df = pd.concat(df_list)
        st.dataframe(final_df.head())
        # st.write(final_df.dtypes)
        filter_by_date_activity(final_df, final_df['date'])


def filter_by_date(df, column):
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)
    st.sidebar.write(':date: Filtering by date')
    start_date = st.sidebar.date_input('Start date', today)
    end_date = st.sidebar.date_input('End date', tomorrow)
    start_date_str = str(start_date)
    end_date_str = str(end_date)

    # st.write(type(start_date_str))
    # st.write(type(end_date_str))

    after_start_date = column >= start_date_str
    before_end_date = column < end_date_str
    between_two_dates = after_start_date & before_end_date
    filtered_dates = df.loc[between_two_dates]

    return start_date, end_date, filtered_dates


def filter_by_date_calendar(df, column):
    start_date, end_date, filtered_dates = filter_by_date(df, column)
    if st.checkbox("Filter by date"):
        if start_date < end_date:
            st.success('Start date: `%s`\n\n End date: `%s`' % (start_date, end_date))
            st.dataframe(filtered_dates)
            plot_calendar(df, filtered_dates)
        else:
            st.error('Error: End date must fall after start date.')


def filter_by_date_browser(df, column):
    start_date, end_date, filtered_dates = filter_by_date(df, column)
    if st.checkbox("Filter by date"):
        if start_date < end_date:
            st.success('Start date: `%s`\n\n End date: `%s`' % (start_date, end_date))
            if filtered_dates.empty:
                st.warning("Your period of time contained no events")
            else:
                st.dataframe(filtered_dates)
                cloud_words(filtered_dates)
                word_search(filtered_dates)
        else:
            st.error('Error: End date must fall after start date.')


def filter_by_date_activity(df, column):
    start_date, end_date, filtered_dates = filter_by_date(df, column)
    if st.checkbox("Filter by date"):
        if start_date < end_date:
            st.success('Start date: `%s`\n\n End date: `%s`' % (start_date, end_date))
            if filtered_dates.empty:
                st.warning("Your period of time contained no events")
            else:
                st.dataframe(filtered_dates)
                cloud_words(filtered_dates)
                timeline_chart(filtered_dates)
                word_search(filtered_dates)

        else:
            st.error('Error: End date must fall after start date.')


def plot_calendar(df, filtered_date):
    if filtered_date.empty:
        st.warning("Your period of time contained no events")
    else:
        if st.selectbox("", ["Pie Chart"]):
            fig, ax = plt.subplots()
            ax.pie(filtered_date.iloc[:, 0].value_counts(), autopct="%1.1f%%")
            ax.axis('equal')
            ax.legend(filtered_date.iloc[:, 0].value_counts().index.tolist(),
                      title="Subject",
                      loc="center left",
                      bbox_to_anchor=(1, 0, 0.5, 1))
            ax.set_title("Lecture time allocated for each subject")
            # st.write(filtered_date.iloc[:, 0].value_counts().plot.pie(autopct="%1.1f%%"))
            st.pyplot(fig)
            with st.beta_expander("Insights provided here"):
                filtered_date = filtered_date.rename(columns={'Subject': 'Lecture Time (hours)'})
                st.write(filtered_date.iloc[:, 0].value_counts())


def cloud_words(filtered_date):
    if st.selectbox("", ["Words Cloud"]):
        comment_words = ''
        stopwords = set(STOPWORDS)
        stopwords.update(["visited", "searched", "watched"])
        # iterate through the csv file
        for val in filtered_date.title:

            # typecaste each val to string
            val = str(val)

            # split the value
            tokens = val.split()

            # Converts each token into lowercase
            for i in range(len(tokens)):
                tokens[i] = tokens[i].lower()

            comment_words += " ".join(tokens) + " "

        wordcloud = WordCloud(width=800, height=800,
                              background_color='black',
                              colormap='Set2',
                              collocations=False,
                              stopwords=stopwords,
                              random_state=1,
                              min_font_size=10).generate(comment_words)

        # plot the WordCloud image
        fig, ax = plt.subplots(figsize=(8, 8), facecolor=None)
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        plt.tight_layout(pad=0)
        st.pyplot(fig)

        if st.checkbox("Top Words"):
            all_titles = ' '.join(filtered_date['title'].str.lower())
            bad_chars = [';', '|', '&', "-"]
            for i in bad_chars:
                all_titles = all_titles.replace(i, '')

            filtered_words = [word for word in all_titles.split() if word not in stopwords]
            counted_words = collections.Counter(filtered_words)

            words = []
            counts = []
            for letter, count in counted_words.most_common(10):
                words.append(letter)
                counts.append(count)

            colors = cm.rainbow(np.linspace(0, 1, 10))

            fig, ax = plt.subplots(figsize=(20, 10))
            ax.set_title('Top words in the browser titles')
            ax.set_xlabel('Count')
            ax.set_ylabel('Words')
            ax.barh(words, counts, color=colors)
            st.pyplot(fig)


def word_search(filtered_date):
    if st.checkbox("Filter by keyword"):
        word = st.sidebar.text_input("Enter your keyword for searching")
        df1 = filtered_date[filtered_date['title'].str.contains(word)]
        st.dataframe(df1)
        st.markdown(get_table_download_link(df1), unsafe_allow_html=True)


def timeline_chart(filtered_date):
    if st.selectbox("", ["Timeline chart by day"]):
        alt.renderers.enable('jupyterlab')

        filtered_date = filtered_date[filtered_date['header'].isin(['Chrome', 'Search', 'Gmail', 'YouTube'])]
        filtered_date = filtered_date.rename(columns={'header': 'activity'})
        # st.write(filtered_date)

    c = alt.Chart(filtered_date).mark_circle().encode(
        x='time',
        y='activity',
        color=alt.Color('activity', scale=alt.Scale(scheme='dark2'))
    )

    st.altair_chart(c, use_container_width=True)


def get_table_download_link(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(
        csv.encode()
    ).decode()  # some strings <-> bytes conversions necessary here
    return f'<a href="data:file/csv;base64,{b64}" download="myfilename.csv">Download csv file</a>'


def write():
    """Used to write the page in the app.py file"""
    with st.spinner("Loading Exploration ..."):
        st.title('PIMS')
    select_source()
