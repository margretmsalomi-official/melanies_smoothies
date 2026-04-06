# Import python packages
import requests
import streamlit as st
import pandas as pd  # Added Pandas
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie :cup_with_straw:")
st.write("Choose your favourite fruit")

name_on_order = st.text_input("Name on Smoothie ")
st.write("The name on your smoothie will be : ", name_on_order)

# Set up Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# 1. Load the Snowflake table
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# 2. Convert the Snowflake Dataframe to a Pandas Dataframe so we can use .loc
pd_df = my_dataframe.to_pandas()

# Display FRUIT_NAME in the multiselect UI
# We still use the original my_dataframe for the list of options
ingredients_list = st.multiselect('Choose Up to 5 Ingredients:', my_dataframe, max_selections=5)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # 3. Use the specific Pandas statement to get the "Search On" value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen, ' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        
        # 4. Use the search_on variable for the API call
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Prepare the insert statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
