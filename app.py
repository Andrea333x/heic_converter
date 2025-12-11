import streamlit as st
from PIL import Image
from pillow_heif import register_heif_opener
import io
import zipfile

# Registra il supporto HEIC per Pillow
register_heif_opener()

# Configurazione pagina
st.set_page_config(
    page_title="HEIC to JPG Converter",
    page_icon="📸",
    layout="centered"
)

st.title("Convertitore HEIC to JPG 📸")
st.write("Carica le tue foto .HEIC e scaricale convertite in .JPG")

# Slider per la qualita JPG
quality = st.slider("Qualita JPG", min_value=50, max_value=100, value=95)

# Widget per caricare i file (permette selezione multipla)
uploaded_files = st.file_uploader(
    "Trascina qui i file HEIC",
    type=["heic", "HEIC"],
    accept_multiple_files=True
)

if uploaded_files:
    st.info(f"Caricati {len(uploaded_files)} file")

    # Se e stato caricato un solo file
    if len(uploaded_files) == 1:
        file = uploaded_files[0]

        try:
            image = Image.open(file)

            # Mostra anteprima
            st.image(image, caption="Anteprima", use_container_width=True)

            # Convertiamo in memoria
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='JPEG', quality=quality)
            img_byte_arr = img_byte_arr.getvalue()

            # Nome file output
            output_name = file.name.lower().replace(".heic", ".jpg")

            st.download_button(
                label="Scarica JPG",
                data=img_byte_arr,
                file_name=output_name,
                mime="image/jpeg"
            )
        except Exception as e:
            st.error(f"Errore durante la conversione: {e}")

    # Se sono stati caricati piu file (creiamo uno ZIP)
    else:
        if st.button(f"Converti {len(uploaded_files)} immagini"):
            zip_buffer = io.BytesIO()

            # Barra di progresso
            progress_bar = st.progress(0)
            status_text = st.empty()

            success_count = 0
            fail_count = 0

            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for i, file in enumerate(uploaded_files):
                    status_text.text(f"Conversione: {file.name}")

                    try:
                        # Conversione
                        image = Image.open(file)
                        img_byte_arr = io.BytesIO()
                        image.save(img_byte_arr, format='JPEG', quality=quality)

                        # Aggiunta allo ZIP
                        filename = file.name.lower().replace(".heic", ".jpg")
                        zip_file.writestr(filename, img_byte_arr.getvalue())
                        success_count += 1

                    except Exception as e:
                        st.warning(f"Errore con {file.name}: {e}")
                        fail_count += 1

                    # Aggiorna barra
                    progress_bar.progress((i + 1) / len(uploaded_files))

            status_text.empty()

            if success_count > 0:
                st.success(f"Conversione completata! {success_count} file convertiti, {fail_count} errori")

                st.download_button(
                    label="Scarica tutto (ZIP)",
                    data=zip_buffer.getvalue(),
                    file_name="immagini_convertite.zip",
                    mime="application/zip"
                )
            else:
                st.error("Nessun file convertito con successo")

# Footer
st.markdown("---")
st.markdown("*Convertitore HEIC to JPG - I file vengono elaborati in memoria e non salvati sul server*")
