from zipfile import ZipFile
import pathlib
import settings

base_path = pathlib.Path(__file__).parent.resolve(strict=True)

working_folder = base_path.joinpath(settings.INPUT_LOGS_FOLDER)
ARCHIVES_TO_CHECK = [".zip"]
FILES_ZIPPED = 1


def unzip_files():
    for path_object in working_folder.iterdir():
        if path_object.is_file() and path_object.suffix in ARCHIVES_TO_CHECK:
            name = path_object.stem
            with ZipFile(path_object, "r") as myzip:
                zipped_files = myzip.namelist()
                if len(zipped_files) > FILES_ZIPPED:
                    raise Exception
                for file in myzip.namelist():
                    myzip.extract(file)
                    extracted_file = pathlib.Path(file)
                    new_name = extracted_file.parent.joinpath(
                        name
                    ).with_suffix(".txt")
                    extracted_file.rename(new_name)
            path_object.unlink()
