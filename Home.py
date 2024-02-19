import streamlit as st
import controller as ctrl
import requests

st.set_page_config(
    page_title="Iaora Stock Manager",
    page_icon="🇵🇫",
)

def main():
    stock = ctrl.Stock()
    st.write("# Stock manager")

    tab_search, tab_add = st.tabs([
        "Explore Produits", "Ajouter un produit"
    ])


    with tab_search:
        search_bar_value = st.text_input(
            ":mag: Nom du produit",
            value="",
            placeholder="Entrez le produit à chercher.."
            )

        search_res = stock.search_product(
            search_bar_value
        )
        
        st.session_state["products"] = stock.get_stock()
        if search_res.shape[0] >= 1:
            st.session_state["products"] = search_res
        else:
            st.warning(f"Aucun produit trouvé contenant : {search_bar_value}")


        if len(search_bar_value) == 0:
            st.write("**Tous les produits :**")

        N_cards_per_row = 3
        for n_row, row in st.session_state["products"].reset_index().iterrows():
            i = n_row%N_cards_per_row
            if i==0:
                cols = st.columns(N_cards_per_row, gap="large")

            with cols[n_row%N_cards_per_row]:
                ctrl.md.Product(row).show()
    
    with tab_add:
        st.write("**\*Tous les champs doivent être remplis.**")

        product_name = st.text_input("Nom du produit :", key="prd_name")
        product_barcode = st.text_input("Barcode value :", key="prd_barcode")
        product_location = st.text_input("Localisation au stock :", key="prd_location")

        col_img, col_preview = st.columns(2)

        with col_img:
            product_image = st.file_uploader("Image :", type=["png", "jpg"], key="prd_image")
        
        with col_preview:
            if product_image:
                st.write("**Image Preview :**")
                st.image(product_image, use_column_width=True)

        
        prd_val = ["name", "barcode", "image", "location"]

        proceed = True

        warning_placeholder = st.empty()

        if st.button("Ajouter le produit"):
            
            if proceed:
                stock.create_product(
                    product_name,
                    product_barcode,
                    product_image,
                    product_location
                )
                st.session_state["products"] = stock.get_stock()
            else:
                warning_placeholder.warning(
                    "Complétez tous les champs pour continuer..")

if __name__ == "__main__":
    main()
