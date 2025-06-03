import os 
for i in range(0, 9):
    print(i)
    os.system("obabel -i mol 0%s_Aminobutyric-acid_zwitterion.mol -o xyz -O 0%s_Aminobutyric-acid_zwitterion.xyz"%(i,i))
    