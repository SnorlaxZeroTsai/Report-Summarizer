# %%
import glob
from Utils.pdf_processor import PDFProcessor
import dotenv

dotenv.load_dotenv(".env")

# %%
if __name__ == "__main__":
    target_folder = "./network_md_files/"
    files = glob.glob("/pdf_parser/network_pdf/*.*")
    pdf_processor = PDFProcessor(files=files, target_folder=target_folder)
    pdf_processor.run_parse()

# %%
