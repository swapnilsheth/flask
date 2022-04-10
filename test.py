from chat_processing_test_sb import chat_processing

x = chat_processing.read_file('Whatsappchat.txt')
y = chat_processing.text_clean(x)
z=chat_processing.convert_to_df(y)
a = chat_processing.df_enhance(z)
b = chat_processing.visualizations(a)
print("process complete")
