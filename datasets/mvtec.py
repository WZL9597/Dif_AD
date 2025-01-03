import os

import PIL.Image as PIL_Image
import numpy as np
import torch
from PIL import Image
from torch.utils.tensorboard import SummaryWriter
from torchvision import transforms

from torchvision.datasets.folder import default_loader

from utils.load_dataset import DatasetSplit
from torchvision.transforms.functional import InterpolationMode

_CLASSNAMES = [
    "bottle",
    "cable",
    "capsule",
    "carpet",
    "grid",
    "hazelnut",
    "leather",
    "metal_nut",
    "pill",
    "screw",
    "tile",
    "toothbrush",
    "transistor",
    "wood",
    "zipper",
]
# 常用的一种归一化imagenet的 RGB模式
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class MVTecDataset(torch.utils.data.Dataset):
    """
    PyTorch Dataset for MVTec.
    """

    def __init__(
            self,
            source,
            classname,
            resize=256,
            imagesize=224,
            split=DatasetSplit.TRAIN,
            cfg=None,
            **kwargs
    ):
        # super().__init__() 就是调用父类的init方法， 同样可以使用super()去调用父类的其他方法。
        super().__init__()
        self.source = source
        self.split = split
        self.classnames_to_use = [classname] if classname is not None else _CLASSNAMES
        self.cfg = cfg

        self.imgpaths_per_class, self.data_to_iterate = self.get_image_data()

        # for test
        self.transform_img = [
            transforms.Resize((resize, resize)),
            transforms.CenterCrop(imagesize),
            transforms.ToTensor()
        ]
        self.transform_img.append(transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD))

        self.transform_img = transforms.Compose(self.transform_img)

        # for train
        self.transform_img_MMR = transforms.Compose([
            # 随机裁剪然后缩放到统一尺寸
            # imagesize表示裁剪输出的图像大小。
            # scale表示裁剪区域大小范围的下限和上限比例。scale参数表示随机裁剪区域的大小范围占原始图像的比例
            # interpolation表示裁剪后图像的插值方法。
            transforms.RandomResizedCrop(imagesize,
                                         scale=(cfg.TRAIN.MMR.DA_low_limit,
                                                cfg.TRAIN.MMR.DA_up_limit),
                                         interpolation=InterpolationMode.BICUBIC),
            # 随机水平旋转
            transforms.RandomHorizontalFlip(),
            # 从numpy.ndarray (形状为H x W x C)数据范围是[0, 255]
            # 到一个 Torch.FloatTensor，其形状 (C x H x W) 在 [0.0, 1.0] 范围内
            transforms.ToTensor(),
            # 归一化处理output = (input - mean) / std
            transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)])

        transform_mask = [
            transforms.Resize((resize, resize)),
            transforms.CenterCrop(imagesize),
            transforms.ToTensor(),
        ]
        self.transform_mask = transforms.Compose(transform_mask)

        self.imagesize = (3, imagesize, imagesize)

    def __getitem__(self, idx):
        classname, anomaly, image_path, mask_path = self.data_to_iterate[idx]

        image = default_loader(image_path)
        if self.split.value == "train":
            image = self.transform_img_MMR(image)
        else:
            image = self.transform_img(image)

        if self.split == DatasetSplit.TEST and mask_path is not None:
            # mask的预处理
            mask = PIL_Image.open(mask_path)
            mask = self.transform_mask(mask)
            # avoid erasing the abnormal mask via center crop避免通过中心裁剪来擦除不正常的mask，
            if torch.max(mask) == 0:
                mask = torch.zeros([1, *image.size()[1:]])
                anomaly = "good"
            else:
                mask = mask / torch.max(mask)
        else:
            mask = torch.zeros([1, *image.size()[1:]])

        # image name need to be replaced
        return {
            "image": image,
            "mask": mask,
            "classname": classname,
            "anomaly": anomaly,
            "is_anomaly": int(anomaly != "good"),
            "image_name": "/".join(image_path.split("/")[-4:]),
            "image_path": image_path,
        }

    def __len__(self):
        return len(self.data_to_iterate)

    def get_image_data(self):
        imgpaths_per_class = {}
        maskpaths_per_class = {}

        for classname in self.classnames_to_use:
            classpath = os.path.join(self.source, classname, self.split.value)
            maskpath = os.path.join(self.source, classname, "ground_truth")
            # 这段代码通过遍历目录,高效地获取了分类i数据集的所有类别名称
            anomaly_types = [i for i in os.listdir(classpath)
                             if os.path.isdir(os.path.join(classpath, i))]

            imgpaths_per_class[classname] = {}
            maskpaths_per_class[classname] = {}

            for anomaly in anomaly_types:
                anomaly_path = os.path.join(classpath, anomaly)
                if os.path.isdir(anomaly_path):
                    # 这行代码使用os模块下的listdir和sorted函数获取了一个目录下所有文件并排序。
                    anomaly_files = sorted(os.listdir(anomaly_path))
                    imgpaths_per_class[classname][anomaly] = [
                        os.path.join(anomaly_path, x) for x in anomaly_files
                    ]
                    # 如果是测试且品类不为good
                    if self.split == DatasetSplit.TEST and anomaly != "good":
                        anomaly_mask_path = os.path.join(maskpath, anomaly)

                        # use the filename in anomaly file
                        maskpaths_per_class[classname][anomaly] = [
                            os.path.join(anomaly_mask_path, x.split(".")[0] + "_mask.png") for x in anomaly_files
                        ]
                    else:
                        maskpaths_per_class[classname]["good"] = None

        # Unrolls the data dictionary to an easy-to-iterate list.
        data_to_iterate = []
        for classname in sorted(imgpaths_per_class.keys()):
            for anomaly in sorted(imgpaths_per_class[classname].keys()):
                for i, image_path in enumerate(imgpaths_per_class[classname][anomaly]):
                    data_tuple = [classname, anomaly, image_path]
                    if self.split == DatasetSplit.TEST and anomaly != "good":
                        data_tuple.append(maskpaths_per_class[classname][anomaly][i])
                    else:
                        data_tuple.append(None)
                    data_to_iterate.append(data_tuple)

        return imgpaths_per_class, data_to_iterate
