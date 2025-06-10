import os 
from tqdm import tqdm 
dirs = [ x for x in os.listdir() if os.path.isdir(x) and  x != "00_Alanine_zwitterion"]

for dir in tqdm(dirs):
    os.chdir(dir)

    os.system("python ~/PSID_server_room/packmol/generate_packmol_input.py")
    os.system("python ~/PSID_server_room/packmol/packmol_multiple.py")

    os.chdir("../")