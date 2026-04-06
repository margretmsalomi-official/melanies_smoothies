# Import python packages
import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose your favourite fruit")

name_on_order = st.text_input("Name on Smoothie ")
st.write("The name on your smoothie will be : ", name_on_order)

# Set up Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# UPDATE: Load both FRUIT_NAME and SEARCH_ON columns
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Display FRUIT_NAME in the multiselect UI
ingredients_list = st.multiselect('Choose Up to 5 Ingredients:', my_dataframe, max_selections=5)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # UPDATE: Find the SEARCH_ON value for the fruit_chosen
        # This looks into our dataframe to find the match for the name shown in the UI
        search_on_df = my_dataframe.filter(col('FRUIT_NAME') == fruit_chosen).to_pandas()
        search_on = search_on_df.iloc[0]['SEARCH_ON']
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # UPDATE: Use the 'search_on' variable in the API URL
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Prepare the insert statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
