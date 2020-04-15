Face Recognition and Detection 

In this hands-on project, the goal is to build a face detection and recognition model which includes building a face detector to locate the position of a face in an image.

Dataset: WIDER Face Dataset
WIDER FACE dataset is a face detection benchmark dataset, of which images are selected from the publicly available WIDER dataset. This data has 32,203 images and 393,703 faces are labelled with a high degree of variability in scale, pose and occlusion as depicted in the sample images.

In this project, we are using 500 images and 1100 faces for ease of computation.

Overview
In this problem, we use a pre-trained model trained on Face recognition to recognize similar faces.
Here, we are particularly interested in recognizing whether two given faces are of the same person or not. Below are the steps involved in the project.

● Load the dataset and create the metadata.
● Check some samples of metadata.
● Load the pre-trained model and weights.
● Generate Embedding vectors for each face in the dataset.
● Build distance metrics for identifying the distance between two given images.
● Use PCA for dimensionality reduction.
● Build SVM classifier to map each image to its right person.
● Predict using the SVM model

Data Set : http://mmlab.ie.cuhk.edu.hk/projects/WIDERFace/
