import streamlit as st
from barcode import Code128
from barcode.writer import ImageWriter
import requests
from io import BytesIO
from PIL import Image

SCOPE = ['https://www.googleapis.com/auth/drive']

class BarCode:
    
    def __init__(self, value):
        self.value = value
        self.barcode = self.__get_barcode_img()
    
    def __get_barcode_img(self) -> Image:
        """Return Image."""
        barcode_image = BytesIO()

        code128 = Code128(
            self.value, writer=ImageWriter()
        )
        code128.write(barcode_image)

        img = Image.open(barcode_image)

        return img
@st.cache_resource(show_spinner="Loading product..")
class Product:
    def __init__(self, row) -> None:
        self.photo = self._get_photo(row["product_photo_id"])
        self.name = row["product_name"]
        self.location = row["product_location"]
        self.barcode = BarCode(
            row["product_barcode"]
        )
    
    def _get_photo(self, photo_id: str) -> str:
        res = requests.get(
            f"https://drive.google.com/uc?id={photo_id}"
        )

        img = ""
        if res.status_code == 200:
            img = res.content
        
        return img
    
    def show(self):
        with st.container(border=True):
            st.image(self.photo, use_column_width =True)
            st.caption(self.name)
            st.markdown(f"Location: {self.location.strip()}")
            st.image(self.barcode.barcode, use_column_width=True)