import streamlit as st
import controller as ctrl
import requests

st.set_page_config(
    page_title="Iaora Stock Manager",
    page_icon="🇵🇫",
)

def main():
    stock = ctrl.Stock()

    authenticator = ctrl.auth_usr()
    name, authentication_status, username = authenticator.login(
        "main", 2, fields={'Form name': 'Login'})

    if authentication_status:

        st.write("# Stock manager")

        authenticator.logout('Logout', 'main')

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


            st.session_state["products"] = st.session_state["products"].sort_values(by='product_location')
            
            N_cards_per_row = 3
            for n_row, row in st.session_state["products"].reset_index().iterrows():
                i = n_row%N_cards_per_row
                if i==0:
                    cols = st.columns(N_cards_per_row, gap="large")

                with cols[n_row%N_cards_per_row]:
                    ctrl.md.Product(row).show()
        
        with tab_add:
            st.write("**\*Tous les champs doivent être remplis.**")

            with st.form("new_product", clear_on_submit=True, border=True):
                product_name = st.text_input("Nom du produit :", key="prd_name")
                product_barcode = st.text_input("Barcode value :", key="prd_barcode")
                product_location = st.text_input("Localisation au stock :", key="prd_location")
                product_image = st.file_uploader("Photo du produit :", type=["png", "jpg"], key="prd_image")

                warning_place_holder = st.empty()

                submitted = st.form_submit_button("Enregistrer")

                if submitted:
                    prd_val = ["name", "barcode", "image", "location"]
                    save_new_product = True

                    for field_name in prd_val:
                        value = st.session_state["prd_" + field_name]
                        if value is None or value == "":
                            save_new_product = False
                            break
                    
                    if save_new_product:
                        existing_products = st.session_state["products"]
                        execute = True

                        # Check location:
                        all_loc = existing_products["product_location"].tolist()
                        if product_location in all_loc:
                            ex_product = existing_products[
                                existing_products["product_location"] == product_location
                            ].iloc[0, 0]
                            warning_place_holder = warning_place_holder.error(
                                f"'{ex_product}' est déjà enregistré à la position '{product_location}'"
                            )
                            execute = False

                        if execute:
                            # Update stock
                            stock.create_product(
                                product_name,
                                product_barcode,
                                product_image,
                                product_location
                            )

                            # Update local product list with new change
                            st.session_state["products"] = stock.get_stock()
                    else:
                        warning_place_holder.warning(
                            "Tous les champs doivent être remplis pour sauvegarder le produit.")

    elif authentication_status == False:
        st.error('Username/mot de passe incorrect')
    elif authentication_status == None:
        st.warning('Identifiez vous pour continuer')


if __name__ == "__main__":
    main()
