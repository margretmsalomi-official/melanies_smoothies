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

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
ingredients_list = st.multiselect('Choose Up to 5 Ingredients:', my_dataframe)

if len(ingredients_list) > 5:
    st.error('Please select no more than 5 ingredients!')
elif ingredients_list:
    ingredients_string = ''
    
    # Process each fruit chosen
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # --- NEW DYNAMIC SECTION ---
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # We concatenate the fruit_chosen variable into the URL string
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        
        # Display the JSON data as a dataframe
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        # ---------------------------

    # Prepare the insert statement for Snowflake
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
