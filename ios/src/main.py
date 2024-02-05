from pathlib import Path
import os
from CallLogReader import CallLogReader
from CSVCreator import CSVCreator

# main function
def main():
    """Main funcation"""
    print("Cool new_package project!")
    read_call_logs()

def search_file_path(root: Path, only_files: bool = True, file_name: str = ""):
    """A dummy docstring."""
    for path in sorted(root.rglob(file_name),key=os.path.getmtime):
        if only_files and not path.is_file() :
            continue

        yield path
   
def search_calllog():
    """A dummy docstring."""
    paths = search_file_path(Path("."), only_files=True,file_name = "MAVCALLSDK*")
    # paths_old = search_file_path(Path("."), only_files=True,file_name = "MAVCALLSDK_old")
    print(paths)
    call_record = CallLogReader()
    # for path in paths_old:
    #     call_record.read_file(path)
        
    for path in paths:
        print(path)
        call_record.read_file(path)

    call_record.readLogs()
    csv_creator = CSVCreator(call_record.call_dict)
    csv_creator.createCSV()

def read_call_logs():
    """A dummy docstring."""
    search_calllog()



if __name__ == "__main__":
    main()

