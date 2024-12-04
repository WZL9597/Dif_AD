import os
from glob import glob

import numpy as np
from PIL import Image
from torch.utils.tensorboard import SummaryWriter

from datasets.mvtec import MVTecDataset

from utils.load_dataset import DatasetSplit


class AeBAD_VDataset(MVTecDataset):

    def get_image_data(self):
        imgpaths_per_class = {}

        for classname in self.classnames_to_use:
            classpath = os.path.join(self.source, classname, self.split.value)
            imgpaths_per_class[classname] = {}
            if self.split == DatasetSplit.TRAIN:
                anomaly_types = ["good"]

                for anomaly in anomaly_types:
                    anomaly_path = os.path.join(classpath, anomaly)
                    if os.path.isdir(anomaly_path):
                        crucial_word = "*/*.jpg"
                        anomaly_files = glob(os.path.join(anomaly_path, crucial_word))

                        imgpaths_per_class[classname][anomaly] = anomaly_files
            else:
                video_types = [self.cfg.DATASET.domain_shift_category]

                # video_types有问题
                for video_name in video_types:
                    video_path = os.path.join(classpath, video_name)
                    if os.path.isdir(video_path):
                        anomaly_types = [i for i in os.listdir(video_path)
                                         if os.path.isdir(os.path.join(video_path, i))]
                        for anomaly in anomaly_types:
                            anomaly_path = os.path.join(video_path, anomaly)
                            if os.path.isdir(anomaly_path):
                                crucial_word = "*.jpg"
                                anomaly_files = glob(os.path.join(anomaly_path, crucial_word))

                                imgpaths_per_class[classname][anomaly] = anomaly_files

        # Unrolls the data dictionary to an easy-to-iterate list.
        data_to_iterate = []
        writer = SummaryWriter("logss")
        for classname in sorted(imgpaths_per_class.keys()):
            for anomaly in sorted(imgpaths_per_class[classname].keys()):
                for i, image_path in enumerate(imgpaths_per_class[classname][anomaly]):
                    data_tuple = [classname, anomaly, image_path]
                    data_tuple.append(None)
                    data_to_iterate.append(data_tuple)
                   # 自加：使用tensorboard展示图片
                    img_PIL = Image.open(image_path)
                    img_array = np.array(img_PIL)
                    writer.add_image("train", img_array, i, dataformats='HWC')
                    # 以上为自加：使用tensorboard展示图片
        writer.close()
        return imgpaths_per_class, data_to_iterate
