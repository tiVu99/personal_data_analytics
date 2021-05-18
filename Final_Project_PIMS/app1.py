import sys

import streamlit as st
import pandas as pd
import json
import sqlite3
import datetime
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# -*- coding: utf-8 -*-
import sys

print(sys.stdout.encoding)

import src.pages.about
import src.pages.home
import src.pages.exploration

PAGES = {
    "Home": src.pages.home,
    "Exploration": src.pages.exploration,
    "About": src.pages.about,
}

def main():
    """Main function of the App"""
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Go to", list(PAGES.keys()))

    page = PAGES[selection]

    with st.spinner(f"Loading {selection} ..."):
        page.write()

if __name__ == "__main__":
    main()


