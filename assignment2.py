import os
import time
from datetime import date

def save_text(input_text: str) -> str:
    """
    This function receives string text and saves it in a text file
    in a directory named as today's date.
    
    :param input_text: text to be saved
    :return: path to the saved file
    """
    
    curr_date = date.today()                                                            # taking today's date
    curr_date = curr_date.strftime('%d-%m-%Y')                                          # formatting and storing date in 'dd-mm-yyyy' format
    
    if not os.path.exists(curr_date):                                                   # checking if today's date named directory exists in current path ,i.e., path where this module is saved
        os.makedirs(curr_date)                                                          # creating today's date named directory if it doesn't exits already

    file_name = "file" + "_" + str(time.time()).split(".")[0] + ".txt"                  # generating unique file_name for every file by appending timestamp

    file_obj = open(f"{curr_date}/{file_name}","w")                                     # opening file file_name in write mode
    file_obj.write(input_text)                                                          # writing input_text to the file
    file_obj.close()                                                                    # closing the file

    path_to_file = f"{os.getcwd()}/{curr_date}/{file_name}"
    print(f"\nFile is saved in a directory : {path_to_file}")                           # notifying user by printing the file path

    return path_to_file                                                                 # returns path of the saved file


if __name__ == '__main__':
    inp_text = input("Please enter file contents? ")                                    # taking text input from user
    saved_file_path = save_text(inp_text)                                               # calling save_text function with the text to save
