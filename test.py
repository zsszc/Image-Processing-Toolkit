from image_processor import process_folder,TifFileManager

# 使用 process_folder 函数处理图像文件夹
#如果单独使用切小块功能只需要将scale_factor = 0 ，make_square_flag = False
source_folder = "path/to/your/source/folder"
output_folder = "path/to/your/output/folder"
scale_factor = 2  # 缩放因子
small_block_size = 512  # 小块大小
make_square_flag = True  # 是否裁剪为正方形

# 调用 process_folder 函数
process_folder(source_folder, output_folder, scale_factor, small_block_size, make_square_flag)
print("图片处理完成。")



#这边的功能是对转换完毕的tif图每张图创建一个单独的文件夹存放
folder_path = '/home/BigData/newimage/'
tif_manager = TifFileManager(folder_path)

# 选择并复制没有对应同名文件夹的 .tif 文件
new_folder_path = '/home/BigData/copied_tif_files/'
tif_manager.select_and_copy_tif(new_folder_path)

# 为每个 .tif 文件创建一个同名文件夹
tif_manager.organize_tif_files()

# 将每个 .tif 文件移动到同名文件夹中
tif_manager.move_tif_to_folder()