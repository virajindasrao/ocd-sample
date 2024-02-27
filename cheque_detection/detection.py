import os
import cv2
import torch
import torchvision
import supervision as sv
import pytorch_lightning as pl
import matplotlib.pyplot as plt

from transformers import DetrImageProcessor, DetrForObjectDetection
from torch.utils.data import DataLoader


image_processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")

CHECKPOINT = "facebook/detr-resnet-50"
MODEL_PATH = 'model'
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
CONFIDENCE_TRESHOLD = 0.5

def validate_data():
    dataset = 'sample_data'
    ANNOTATION_FILE_NAME = '_annotations.coco.json'
    TRAIN_DIRECTORY = os.path.join(dataset,"train")
    TEST_DIRECTORY = os.path.join(dataset,"test")
    VALID_DIRECTORY = os.path.join(dataset,"valid")


    class CocoDetection(torchvision.datasets.CocoDetection):

        def __init__(self,
                    image_directory_path:str,
                    image_processor,
                    train:bool = True):
            annotation_file_path = os.path.join(image_directory_path, ANNOTATION_FILE_NAME)
            super(CocoDetection, self).__init__(image_directory_path, annotation_file_path)
            self.image_processor = image_processor

        def __getitem__(self, idx):
            images, annotations = super(CocoDetection, self).__getitem__(idx)
            image_id = self.ids[idx]
            annotations = {'image_id': image_id, 'annotations':annotations}
            encoding = self.image_processor(images=images, annotations=annotations, return_tensors="pt")
            pixel_values = encoding["pixel_values"].squeeze()
            target = encoding["labels"][0]

            return pixel_values, target

    TRAIN_DATASET = CocoDetection(image_directory_path=TRAIN_DIRECTORY, image_processor=image_processor, train=True)
    VAL_DATASET = CocoDetection(image_directory_path=VALID_DIRECTORY, image_processor=image_processor, train=False)
    TEST_DATASET = CocoDetection(image_directory_path=TEST_DIRECTORY, image_processor=image_processor, train=False)

    print("Number of training examples:", len(TRAIN_DATASET))
    print("Number of validation examples:", len(VAL_DATASET))
    print("Number of test examples:", len(TEST_DATASET))

    return {
        'TRAIN_DATASET': TRAIN_DATASET,
        'VAL_DATASET': VAL_DATASET,
        'TEST_DATASET': TEST_DATASET
    }


def collate_fn(batch):
    pixel_values = [item[0] for item in batch]
    encoding = image_processor.pad(pixel_values, return_tensors="pt")
    labels = [item[1] for item in batch]
    return {
        'pixel_values': encoding['pixel_values'],
        'pixel_mask': encoding['pixel_mask'],
        'labels': labels
    }


def train_model():
    # Load data
    TRAIN_DATALOADER = DataLoader(dataset=TRAIN_DATASET, collate_fn=collate_fn, batch_size=4, shuffle=True)
    VAL_DATALOADER = DataLoader(dataset=VAL_DATASET, collate_fn=collate_fn, batch_size=4)
    TEST_DATALOADER = DataLoader(dataset=TEST_DATASET, collate_fn=collate_fn, batch_size=4)


    class Detr(pl.LightningModule):

        def __init__(self, lr, lr_backbone, weight_decay):
            super().__init__()
            self.model = DetrForObjectDetection.from_pretrained(
                pretrained_model_name_or_path=CHECKPOINT,
                num_labels=len(id2label),
                ignore_mismatched_sizes=True
            )

            self.lr = lr
            self.lr_backbone = lr_backbone
            self.weight_decay = weight_decay

        def forward(self, pixel_values, pixel_mask):
            return self.model(pixel_values=pixel_values, pixel_mask=pixel_mask)

        def common_step(self, batch, batch_idx):
            pixel_values = batch["pixel_values"]
            pixel_mask = batch["pixel_mask"]
            labels = [{k: v.to(self.device) for k, v in t.items()} for t in batch["labels"]]

            outputs = self.model(pixel_values=pixel_values, pixel_mask=pixel_mask, labels=labels)

            loss = outputs.loss
            loss_dict = outputs.loss_dict

            return loss, loss_dict

        def training_step(self, batch, batch_idx):
            loss, loss_dict = self.common_step(batch, batch_idx)
            # logs metrics for each training_step, and the average across the epoch
            self.log("training_loss", loss)
            for k,v in loss_dict.items():
                self.log("train_" + k, v.item())

            return loss

        def validation_step(self, batch, batch_idx):
            loss, loss_dict = self.common_step(batch, batch_idx)
            self.log("validation/loss", loss)
            for k, v in loss_dict.items():
                self.log("validation_" + k, v.item())

            return loss

        def configure_optimizers(self):
            # DETR authors decided to use different learning rate for backbone
            # you can learn more about it here:
            # - https://github.com/facebookresearch/detr/blob/3af9fa878e73b6894ce3596450a8d9b89d918ca9/main.py#L22-L23
            # - https://github.com/facebookresearch/detr/blob/3af9fa878e73b6894ce3596450a8d9b89d918ca9/main.py#L131-L139
            param_dicts = [
                {
                    "params": [p for n, p in self.named_parameters() if "backbone" not in n and p.requires_grad]},
                {
                    "params": [p for n, p in self.named_parameters() if "backbone" in n and p.requires_grad],
                    "lr": self.lr_backbone,
                },
            ]
            return torch.optim.AdamW(param_dicts, lr=self.lr, weight_decay=self.weight_decay)

        def train_dataloader(self):
            return TRAIN_DATALOADER

        def val_dataloader(self):
            return VAL_DATALOADER

    model = Detr(lr=1e-4, lr_backbone=1e-5, weight_decay=1e-4)

    batch = next(iter(TRAIN_DATALOADER))
    outputs = model(pixel_values=batch['pixel_values'], pixel_mask=batch['pixel_mask'])

    # Train the model
    MAX_EPOCHS = 100
    trainer = pl.Trainer(devices=1, accelerator="gpu", max_epochs=MAX_EPOCHS, gradient_clip_val=0.1, accumulate_grad_batches=8, log_every_n_steps=5)
    trainer.fit(model)

    # Export model
    model.model.save_pretrained(MODEL_PATH)


def load_model():
    # Loading model
    model = DetrForObjectDetection.from_pretrained(MODEL_PATH)
    model.to(DEVICE)

    return model

def query_model(model, image):
    
    with torch.no_grad():
        # load image and predict
        inputs = image_processor(images=image, return_tensors='pt').to(DEVICE)
        outputs = model(**inputs)
   
         # post-process
        target_sizes = torch.tensor([image.shape[:2]]).to(DEVICE)
        results = image_processor.post_process_object_detection(
            outputs=outputs,
            threshold=CONFIDENCE_TRESHOLD,
            target_sizes=target_sizes
        )[0]


        detections = sv.Detections.from_transformers(transformers_results=results)

    return detections

if __name__ == '__main__':
    
    vdata = validate_data()

    model = load_model()

    image = cv2.imread('sample_data/test/Cheque-309063_1_jpg.rf.a093639ecf7ac747f502531e24dc4b6f.jpg')

    res = query_model(model, image)
    
    categories = vdata['TEST_DATASET'].coco.cats
    id2label = {k: v['name'] for k,v in categories.items()}
    box_annotator = sv.BoxAnnotator()

    labels = [f"{id2label[class_id]} {confidence:.2f}" for _, confidence, class_id, _ in res]
    frame_detections = box_annotator.annotate(scene=image.copy(), detections=res, labels=labels)
    print(res)

    plt.imsave('output/result.jpg', cv2.cvtColor(frame_detections, cv2.COLOR_BGR2RGB))

    detections = res.xyxy.tolist()
    ids = res.class_id.tolist()

    print(detections)
    image = cv2.imread('sample_data/test/Cheque-309063_1_jpg.rf.a093639ecf7ac747f502531e24dc4b6f.jpg', 0)
    cropped = []

    for i, coord in enumerate(detections):
        x_min, y_min, x_max, y_max = int(coord[0]), int(coord[1]), int(coord[2]), int(coord[3])
        if x_min >= 0 and x_max >= 0 and y_min >= 0 and y_max >= 0:
            cropped.append(image[y_min:y_max, x_min:x_max])
            cv2.imwrite(f'output/cropped_{i}.png', image[y_min:y_max, x_min:x_max])

            # Call OCR
            label = id2label[ids[i]]

    '''   fig, axs = plt.subplots(1, len(cropped), figsize=(10*len(cropped), 10))
    for i in range(len(cropped)):
        axs[i].plot(cropped[i])
        axs[0].axis('off')        
    plt.savefig('output/cropped.jpg')
    '''
    #final = cv2.vconcat(cropped)
    #cv2.imsave('output/cropped.jpg', final)

    #plt.imsave('output/result.jpg', cv2.cvtColor(frame_detections, cv2.COLOR_BGR2RGB))
