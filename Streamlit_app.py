# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session --
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie :cup_with_straw:")

st.write("Choose your favourite fruit")

name_on_order = st.text_input("Name on Smoothie ")
st.write("The name on your smoothie will be : ",name_on_order)

session = get_active_session()

#cnx=st.connection("snowflake")
#session=cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
ingredients_list = st.multiselect('Choose Up to 5 Ingredients:', my_dataframe)

if len(ingredients_list) > 5:
    st.error('Please select no more than 5 ingredients!')
elif ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
