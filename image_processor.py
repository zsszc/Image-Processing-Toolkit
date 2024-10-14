import os
from PIL import Image
import tifffile
import numpy as np
from tqdm import tqdm
import shutil

# 定义一个函数，用于对图像进行下采样
def downsample(image, scale_factor):
    """
    对图像进行下采样。

    参数:
    image (PIL.Image): 输入图像。
    scale_factor (float): 缩放因子。

    返回:
    PIL.Image: 下采样后的图像。
    """
    width, height = image.size  # 获取图像的宽度和高度
    new_size = (int(width / scale_factor), int(height / scale_factor))  # 计算新的尺寸
    return image.resize(new_size, Image.LANCZOS)  # 使用LANCZOS算法对图像进行缩放

# 定义一个函数，用于将图像分割成多个小块
def split_image(image, target_size):
    """
    将图像分割成多个小块。

    参数:
    image (PIL.Image): 输入图像。
    target_size (tuple): 每个小块的目标尺寸。

    返回:
    generator: 生成器，逐个返回图像小块。
    """
    width, height = image.size  # 获取图像的宽度和高度
    # 确保宽度和高度都是目标尺寸的整数倍
    adjusted_width = (width // target_size[0]) * target_size[0]
    adjusted_height = (height // target_size[1]) * target_size[1]

    # 使用两层循环，按照目标尺寸将图像分割成多个小块，并逐个返回
    for i in range(0, adjusted_width, target_size[0]):
        for j in range(0, adjusted_height, target_size[1]):
            yield image.crop((i, j, i + target_size[0], j + target_size[1]))

# 定义一个函数，用于将图像裁剪成正方形（基于最小边）
def make_square(image, fill_color=(0, 0, 0)):
    """
    将图像裁剪成正方形（基于最小边）。

    参数:
    image (PIL.Image): 输入图像。
    fill_color (tuple): 填充颜色，默认为黑色。

    返回:
    PIL.Image: 正方形图像。
    """
    width, height = image.size  # 获取图像的宽度和高度
    min_side = min(width, height)  # 选择较小的边
    new_image = Image.new(image.mode, (min_side, min_side), fill_color)  # 创建新的正方形图像
    new_image.paste(image.crop((0, 0, min_side, min_side)))  # 将原图像粘贴到新图像上
    return new_image

# 定义一个函数，用于处理单个图像文件
def process_image(source_path, output_path, scale_factor, small_block_size, make_square_flag=False):
    """
    处理单个图像文件。

    参数:
    source_path (str): 源文件路径。
    output_path (str): 输出文件路径。
    scale_factor (float): 缩放因子。
    small_block_size (int): 小块尺寸。
    make_square_flag (bool): 是否裁剪成正方形。
    """
    base_output_path = os.path.splitext(output_path)[0]  # 定义基础输出路径

    with tifffile.TiffFile(source_path) as tif:
        image_array = tif.asarray()
    img = Image.fromarray(image_array)

    # 使用原始图像或下采样后的图像
    if scale_factor != 0:
        img = downsample(img, scale_factor)
        downsampled_output_path = f"{base_output_path}_downsampled.png"
        img.save(downsampled_output_path)

        # 保存缩放矩阵
        S = np.array([
            [1 / scale_factor, 0, 0],
            [0, 1 / scale_factor, 0],
            [0, 0, 1]
        ])
        np.save(os.path.splitext(downsampled_output_path)[0] + '_scaling_matrix.npy', S)

    # 如果需要，将图像裁剪成正方形
    if make_square_flag:
        img = make_square(img)

    img.save(output_path)  # 保存处理后的图像

    # 如果需要，将图像分割成小块
    if small_block_size > 0:
        split_count = 0
        for segment in split_image(img, (small_block_size, small_block_size)):
            split_output_path = f"{base_output_path}_part_{split_count}.jpg"
            segment.save(split_output_path)
            split_count += 1

# 定义一个函数，用于遍历文件夹并处理其中的图像文件
def process_folder(source_folder, output_folder, scale_factor, small_block_size, make_square_flag=False):
    """
    遍历文件夹并处理其中的图像文件。

    参数:
    source_folder (str): 源文件夹路径。
    output_folder (str): 输出文件夹路径。
    scale_factor (float): 缩放因子。
    small_block_size (int): 小块尺寸。
    make_square_flag (bool): 是否裁剪成正方形。
    """
    # 如果输出文件夹不存在，则创建它
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    items = os.listdir(source_folder)  # 列出源文件夹中的所有文件和子文件夹

    # 使用tqdm显示进度条，并遍历所有文件和子文件夹
    for item in tqdm(items, desc=f"Processing {source_folder}", unit="file"):
        source_item_path = os.path.join(source_folder, item)  # 构建源文件的完整路径

        # 如果当前项是子文件夹，则递归处理该子文件夹
        if os.path.isdir(source_item_path):
            output_subfolder_path = os.path.join(output_folder, item)  # 构建输出子文件夹的完整路径
            if not os.path.exists(output_subfolder_path):  # 如果输出子文件夹不存在，则创建它
                os.makedirs(output_subfolder_path)
            process_folder(source_item_path, output_subfolder_path, scale_factor, small_block_size, make_square_flag)

        # 如果当前项是TIFF文件，则处理该文件
        elif item.lower().endswith(('.tif', '.tiff')):
            new_file_name = f"{os.path.splitext(item)[0]}_small.tif"  # 构建输出文件的名称
            new_file_path = os.path.join(output_folder, new_file_name)  # 构建输出文件的完整路径
            process_image(source_item_path, new_file_path, scale_factor, small_block_size, make_square_flag)



class TifFileManager:
    def __init__(self, folder_path):
        self.folder_path = folder_path

    def select_and_copy_tif(self, new_folder_path, max_files=10):
        """
        选择并复制没有对应同名文件夹的 .tif 文件到新文件夹。
        :param new_folder_path: 目标文件夹路径
        :param max_files: 最大选择文件数
        """
        tif_files_without_folder = []

        for file_name in os.listdir(self.folder_path):
            if file_name.lower().endswith('.tif'):
                file_path = os.path.join(self.folder_path, file_name)
                file_name_without_ext = os.path.splitext(file_name)[0]
                target_folder_path = os.path.join(self.folder_path, file_name_without_ext)

                if os.path.isfile(file_path) and not os.path.exists(target_folder_path):
                    tif_files_without_folder.append(file_path)

                    if len(tif_files_without_folder) == max_files:
                        break

        if len(tif_files_without_folder) > 0:
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                print(f"新文件夹已创建: {new_folder_path}")

            for file_path in tif_files_without_folder:
                shutil.copy(file_path, new_folder_path)
                print(f"复制文件 {os.path.basename(file_path)} 到 {new_folder_path}")

    def organize_tif_files(self):
        """
        为文件夹中的每个 .tif 文件创建一个同名文件夹。
        """
        for file_name in os.listdir(self.folder_path):
            if file_name.lower().endswith('.tif'):
                file_path = os.path.join(self.folder_path, file_name)
                file_name_without_ext = os.path.splitext(file_name)[0]
                target_folder_path = os.path.join(self.folder_path, file_name_without_ext)

                if os.path.isfile(file_path) and not os.path.exists(target_folder_path):
                    os.makedirs(target_folder_path)
                    print(f"已创建文件夹: {target_folder_path}")

    def move_tif_to_folder(self):
        """
        将文件夹中的每个 .tif 文件移动到一个同名文件夹中。
        """
        for file_name in os.listdir(self.folder_path):
            if file_name.lower().endswith('.tif'):
                file_path = os.path.join(self.folder_path, file_name)
                file_name_without_ext = os.path.splitext(file_name)[0]
                target_folder_path = os.path.join(self.folder_path, file_name_without_ext)

                if os.path.isfile(file_path):
                    if not os.path.exists(target_folder_path):
                        os.makedirs(target_folder_path)
                        print(f"已创建文件夹: {target_folder_path}")

                    shutil.move(file_path, target_folder_path)
                    print(f"已将文件 {file_name} 移动到 {target_folder_path}")

# # 示例使用代码文件
# if __name__ == "__main__":
#     # 使用 process_folder 函数处理图像文件夹
#     source_folder = "path/to/your/source/folder"
#     output_folder = "path/to/your/output/folder"
#     scale_factor = 2  # 缩放因子
#     small_block_size = 512  # 小块大小
#     make_square_flag = True  # 是否裁剪为正方形
#
#     # 调用 process_folder 函数
#     process_folder(source_folder, output_folder, scale_factor, small_block_size, make_square_flag)
#     print("图片处理完成。")

# 示例使用
# if __name__ == "__main__":
#     folder_path = '/home/BigData/newimage/'
#     tif_manager = TifFileManager(folder_path)
#
#     # 选择并复制没有对应同名文件夹的 .tif 文件
#     new_folder_path = '/home/BigData/copied_tif_files/'
#     tif_manager.select_and_copy_tif(new_folder_path)
#
#     # 为每个 .tif 文件创建一个同名文件夹
#     tif_manager.organize_tif_files()
#
#     # 将每个 .tif 文件移动到同名文件夹中
#     tif_manager.move_tif_to_folder()