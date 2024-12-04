import streamlit as st
from PIL import Image
import requests
import re
from unidecode import unidecode


api_path = 'https://wineadvisor-688101927459.europe-west1.run.app'
# api_path = 'http://127.0.0.1:8000'

# Set up the page configuration
st.set_page_config(page_title="Wine Advisor", page_icon="🍷", layout="centered")

# Display the logo
logo = Image.open("app/wine_advisor_logo.jpg")
st.image(logo, use_container_width=True)

# title and description
st.write("Upload a photo of a wine bottle to discover the top 10 recommended wines tailored to your taste. 🍇")

# Dropdown menu for wine type selection
wine_type = st.selectbox(
    "Select the type of wine",
    ["blanc", "rouge", "rose", "effervescent", "fortifie"]
)

# File uploader for wine bottle image
uploaded_file = st.file_uploader("Choose a file (JPG/PNG)", type=["jpg", "jpeg", "png"])

# Display the uploaded image
if st.button("Process Wine"):
    if uploaded_file and wine_type:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

        # Placeholder for predictions
        with st.spinner("Analyzing the image... Please wait."):
            # Send image to the backend API
            url = f"{api_path}/uploadfile_identification"
            files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
            response = requests.post(url, files=files)

            if response.status_code == 200:
                # Parse the response
                wine_info = response.json()

                # Add or modify the wine type
                wine_info["type_of_wine"] = [wine_type]

                # Step 2: Check for missing fields (winery or vintage)
                winery = wine_info.get("winery", [None])[0]
                vintage = wine_info.get("vintage", [None])[0]

                if not winery:
                    winery = st.text_input("Winery is missing. Please provide the winery name:")
                    if winery :
                        winery = unidecode(winery)
                        # Remove special characters
                        winery = re.sub(r'[^a-zA-Z0-9\s]', ' ', winery)
                        # Convert to lowercase
                        winery = winery.lower()
                        # Strip extra spaces
                        winery = winery.strip()
                if not vintage:
                    vintage = st.number_input(
                        "Vintage is missing. Please provide the vintage year:",
                        min_value=1800,
                        max_value=2100,
                        step=1,
                    )

                # Ensure both fields are filled before proceeding
                if winery and vintage:
                    # Add the missing fields to wine_info
                    wine_info["winery"] = [winery]
                    wine_info["vintage"] = [int(vintage)]

                    # Step 3: Call `/predict` API to get recommendations
                    url_predict = f"{api_path}/predict"
                    params = {
                        "winery": wine_info["winery"][0],
                        "type_of_wine": wine_info["type_of_wine"][0],
                        "alcohol": float(wine_info.get("alcohol", [0.0])[0]) if wine_info.get("alcohol", [None])[0] is not None else 0.0,  # Float, default: 0.13
                        "appellation": wine_info["appellation"][0],
                        "region": wine_info["region"][0],
                        "vintage": wine_info["vintage"][0]
                    }
                    response_predict = requests.get(url_predict, params=params)

                    if response_predict.status_code == 200:
                        # Parse the response
                        results = response_predict.json()

                        # Check if there are any recommendations
                        st.success("Here are your top recommended wines:")

                        # Iterate through the recommendations
                        for i, (key, wine_info) in enumerate(results.items(), start=1):
                            winery = wine_info.get("winery", "Unknown Winery")
                            cuvee = wine_info.get("cuvee", "No Cuvee")
                            vintage = int(wine_info.get("vintage", "Unknown Vintage"))
                            type_of_wine = wine_info.get("type_of_wine", "Unknown Type")
                            region = wine_info.get("region", "Unknown Region")
                            appellation = wine_info.get("appellation", "Unknown Appellation")
                            cepage = wine_info.get("cepage", "Unknown Cepage")
                            alcohol = wine_info.get("alcohol", "Unknown Alcohol")
                            price_usd = wine_info.get("price_usd", "Unknown Price")
                            rating = wine_info.get("rating", "Unknown Rating")
                            distance = wine_info.get("distance", "Unknown Distance")

                            # Display each wine recommendation
                            st.markdown(f"""
                            ### 🍇 {i}. {winery.capitalize()} - {cuvee.capitalize() if cuvee else "N/A"}
                            - **🍷 Type**: {type_of_wine.capitalize()}
                            - **📅 Vintage**: {vintage}
                            - **🌍 Region**: {region.capitalize()}
                            - **🏷️ Appellation**: {appellation.capitalize()}
                            - **🍃 Cepage**: {cepage.capitalize()}
                            - **🥂 Alcohol**: {f"{alcohol:.1%}" if alcohol else "N/A"}
                            - **💲 Price**: {price_usd}$
                            - **⭐ Rating**: {rating}/100
                            """)

                    else:
                        st.error("No recommendations found. Please try again.")
            else:
                st.error("Error: Unable to identify the wine. Please try again.")
    else:
        st.error("Please upload a wine image and select a wine type.")


st.markdown("""
    ---
    _Developed with ❤️ by Celine, Charles-Antoine & Carl. Le Wagon #1812_
""")
