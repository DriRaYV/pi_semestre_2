import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras import layers, models

train_dir = "data/"

datagen = ImageDataGenerator(validation_split=0.2, rescale=1 / 255)

img_size = (224, 224)
batch_size = 16

train_gen = datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="training",
)

val_gen = datagen.flow_from_directory(
    train_dir,
    target_size=img_size,
    batch_size=batch_size,
    class_mode="categorical",
    subset="validation",
)

base = MobileNetV2(input_shape=img_size + (3,), include_top=False, weights="imagenet")
base.trainable = False

model = models.Sequential(
    [
        base,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation="relu"),
        layers.Dense(2, activation="softmax"),
    ]
)

print("\nClasses detectadas:", train_gen.class_indices)

model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

history = model.fit(train_gen, validation_data=val_gen, epochs=5)

model.save("model.keras", include_optimizer=False)
