import os  
import sys  
import subprocess  
from time import time  
  
def main():  
    if len(sys.argv) != 4:  
        raise ValueError('Usage: convert_kfb2tif.py [src_folder_name] [des_folder_name] [layer]')    
    exe_path = r'D:\kfb2tif\KFbioConverter.exe'  
    if not os.path.exists(exe_path):  
        raise FileNotFoundError('Could not find conversion tool.')  
  
    _, src_folder_name, des_folder_name, layer_str = sys.argv  
   
    layer = int(layer_str)  
    if not 2 <= layer <= 9:  
        raise ValueError('Layer must be between 2 and 9.')  
  
    pwd = os.getcwd()  
    
    full_path = os.path.join(pwd, src_folder_name)  
    dest_path = os.path.join(pwd, des_folder_name)  
    
    if not os.path.exists(full_path):  
        raise FileNotFoundError(f'Could not find directory: {src_folder_name}')  
    
    if not os.path.exists(dest_path):  
        os.makedirs(dest_path)  
   
    kfb_list = [f for f in os.listdir(full_path) if f.endswith('.kfb')]  
  
    print(f'Found {len(kfb_list)} slides, transferring to TIF format ...')  
    for elem in kfb_list:  
        st = time()  
        kfb_elem_path = os.path.join(full_path, elem)  
        tif_dest_path = os.path.join(dest_path, elem.replace('.kfb', '.tif'))  
   
        command = [exe_path, kfb_elem_path, tif_dest_path, str(layer)]  
  
        print(f'Processing {elem} ...')  
        subprocess.run(command, check=True)  
  
        print(f'Finished {elem}, time: {time() - st}s ...')  
  
if __name__ == "__main__":  
    main()