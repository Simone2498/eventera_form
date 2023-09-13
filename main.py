import streamlit as st
from PIL import Image
import boto3
import os
import json
from captcha.image import ImageCaptcha
import random, string

# Create S3 client
s3 = boto3.client('s3', aws_access_key_id=st.secrets['AWS_ACCESS_KEY'], aws_secret_access_key=st.secrets['AWS_SECRET_KEY'])

# Function to upload file to S3
def upload_to_s3(file_path, file_name):
    s3.upload_file(file_path, st.secrets['AWS_BUCKET_NAME'], file_name)

# Function to save email to a text file
def save_data(code, data):
    with open(f'{data["eventday"]}_{code}.txt', 'w') as fp:
        json.dump(data, fp)

def send_data(img, eventdata):
    code = ''.join(random.choices(string.ascii_lowercase, k=5))
    print(code)

    img.save(f'{eventdata["eventday"]}_{code}.jpg')

    # Save email to a text file
    save_data(code, eventdata)

    # Upload both files to S3
    upload_to_s3(f'{eventdata["eventday"]}_{code}.jpg', f'img/{eventdata["eventday"]}_{code}.jpg')
    upload_to_s3(f'{eventdata["eventday"]}_{code}.txt', f'json/{eventdata["eventday"]}_{code}.txt')

    # Clean up temporary files
    os.remove(f'{eventdata["eventday"]}_{code}.jpg')
    os.remove(f'{eventdata["eventday"]}_{code}.txt')

    st.success("Event correctly loaded, we will contact you if needed!")


length_captcha = 8
width = 200
height = 150
# define the function for the captcha control
def captcha_control():
    #control if the captcha is correct
    if 'controllo' not in st.session_state or st.session_state['controllo'] == False:
        st.title("Captcha Control 🤗")
        
        # define the session state for control if the captcha is correct
        st.session_state['controllo'] = False
        col1, col2 = st.columns(2)
        
        # define the session state for the captcha text because it doesn't change during refreshes 
        if 'Captcha' not in st.session_state:
                st.session_state['Captcha'] = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length_captcha))
        print("the captcha is: ", st.session_state['Captcha'])
        
        #setup the captcha widget
        image = ImageCaptcha(width=width, height=height)
        data = image.generate(st.session_state['Captcha'])
        col1.image(data)
        capta2_text = col2.text_area('Enter captcha text', height=30)
        
        
        if st.button("Verify the code"):
            print(capta2_text, st.session_state['Captcha'])
            capta2_text = capta2_text.replace(" ", "")
            # if the captcha is correct, the controllo session state is set to True
            if st.session_state['Captcha'].lower() == capta2_text.lower().strip():
                del st.session_state['Captcha']
                col1.empty()
                col2.empty()
                st.session_state['controllo'] = True
                st.experimental_rerun() 
            else:
                # if the captcha is wrong, the controllo session state is set to False and the captcha is regenerated
                st.error("🚨 Il codice captcha è errato, riprova")
                del st.session_state['Captcha']
                del st.session_state['controllo']
                st.experimental_rerun()
        else:
            #wait for the button click
            st.stop()

    
# Main Streamlit app
def main():
    st.title("Image Upload and Email Entry")
    
    eventdata = {}
    eventdata["email"] = st.text_input("Enter your email:")
    eventdata["eventname"] = st.text_input("Enter the event name:")
    eventdata["eventday"] = str(st.date_input("Enter the date of the event:", format="DD/MM/YYYY"))
    eventdata["eventtime"] = str(st.time_input("Enter the starting time of the event:"))
    eventdata["eventprice"] = st.number_input("Enter the price of the event or 0,00€ if free:", format="%.2f")
    eventdata["eventplace"] = st.text_input("Enter the place of the event:")

    uploaded_file = st.file_uploader("Choose an image...", type="jpg")

    if uploaded_file is not None:
        
        # Convert the image to squared shape and scale to 720x720
        img = Image.open(uploaded_file)
        img = img.resize((720, 720))
        img = img.crop((0, 0, 720, 720))

        # Display the image
        st.image(img, caption="Uploaded Image.", use_column_width=True)

        if st.button("SEND", type="primary", use_container_width=True):
            send_data(img, eventdata)
        

# Run the Streamlit app
if __name__ == '__main__':
    if 'controllo' not in st.session_state or st.session_state['controllo'] == False:
        captcha_control()
    else:
        main()
