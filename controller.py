import pandas as pd
import model as md
import streamlit as st
from datetime import datetime
from pytz import timezone
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.oauth2 import service_account
import google
from io import BytesIO
import mimetypes
import streamlit_authenticator as stauth

class Stock:
    """Stock class to manage the stock."""

    def __init__(self):
        origin = st.secrets["gdrive"]
        self.__url = origin["url"]
        self.__name = origin["sheet_name"]
        self.__id = origin["sheet_id"]
        self.local_tz = timezone('Pacific/Tahiti')


        self.__files = build(
            'drive',
            'v3',
            credentials=self.__credentials()
        ).files()

        self.__sheet =  build(
            'sheets',
            'v4',
            credentials=self.__credentials()
        ).spreadsheets().values()


    def __credentials(self) -> google.oauth2.service_account.Credentials:
        """Return credentials."""

        creds = dict(st.secrets["credentials"])

        return service_account.Credentials.from_service_account_info(
            creds,
            scopes = md.SCOPE
        )
    

    def __img_metadata(self, img_hash: str) -> dict:
        """Return image metadata."""
        return {
            'name': img_hash,
            'parents': [
                st.secrets['gdrive']['IMG_LOCATION_ID']
            ]
        }


    def __get_currentDateTimeStamp(self):
        """Return current datetimestemp."""
        return datetime.now(self.local_tz).strftime('%Y-%m-%d %H:%M:%S')


    def create_product(self, 
            product_name: str,
            product_barcode: str,
            product_image,
            product_location: str,
            progress_bar) -> None:
        """Update the stock."""

        progress_bar.progress(70, text="Saving image to storage..")
        # Save Image and get its ID
        img_id = self.save_photo(
            product_image,
            product_barcode
        )

        progress_bar.progress(80, text="Saving product to stock..")

        # Row parsing
        body = {
            "values": [
                [
                    product_name,
                    product_barcode,
                    img_id,
                    product_location,
                    self.__get_currentDateTimeStamp()
                ]
            ]
        }

        # Update google sheet with new obj data
        self.__sheet.append(
            spreadsheetId=self.__id,
            range=self.__name,
            valueInputOption='RAW',
            body=body
        ).execute()

        st.toast("Product created", icon="✔️")


    def save_photo(self, photo, photo_hash: str) -> str:
        """Save given photo with the name photo_hash."""
        img_metadata = self.__img_metadata(photo_hash)
        
        # Convert the uploaded file to BytesIO object
        img_bytes = BytesIO(photo.read())

        # Retrieve the MIME type based on the file extension
        mime_type, _ = mimetypes.guess_type(photo.name)

        # Create the media body
        media_body = MediaIoBaseUpload(
            img_bytes,
            mimetype=mime_type,
            resumable=True
        )

        # Upload the file to Google Drive
        file_metadata = self.__files.create(
            body=img_metadata,
            media_body=media_body
        ).execute()

        return file_metadata["id"]
    
    def get_url(self):
        return self.__url.format(
                sheet_name = self.__name,
                sheet_id = self.__id
            )

    def get_stock(self) -> pd.DataFrame:
        """Return the overall stock."""
        return pd.read_csv(
            self.get_url()
            , dtype=str
        )
    
    def search_product(self, text: str):

        df = self.get_stock()

        filter_df = df.copy(deep=True)
        filter_df["product_name"] = filter_df["product_name"].map(lambda x: x.lower())

        return df[filter_df["product_name"].str.contains(text.lower())]


# Security

def auth_usr() -> stauth.Authenticate:
    """Authenticate user."""

    config = st.secrets["auth"]
    authenticator = stauth.Authenticate(
      config.credentials.to_dict(),
      config.cookie.name,
      config.cookie.key,
      config.cookie.expiry_days,
      config.preauthorized.to_dict()
    )

    return authenticator


def display_products(in_products: pd.DataFrame,
                     order_by: list=[],
                     N_cards_per_row=3) -> None:
    """Display products."""
    products = in_products.copy(deep=True)

    # Sort products
    products = products.sort_values(by=order_by)
    
    # Display products
    for n_row, row in products.reset_index().iterrows():
        i = n_row%N_cards_per_row
        if i==0:
            cols = st.columns(N_cards_per_row, gap="large")

        with cols[n_row%N_cards_per_row]:
            md.Product(row).show()

