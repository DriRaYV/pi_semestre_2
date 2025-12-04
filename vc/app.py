import gradio as gr
import tensorflow as tf
import numpy as np

model = tf.keras.models.load_model("model.keras")
labels = ["limpa", "suja"]


def classify(image):
    image = image.resize((224, 224))
    image = np.array(image) / 255.0
    image = np.expand_dims(image, axis=0)
    preds = model.predict(image)[0]
    return {labels[i]: float(preds[i]) for i in range(len(labels))}


with gr.Blocks() as app:

    gr.HTML(
        """
    <style>
    body, .gradio-container, .fillable, .wrap, main, .contain {
        background: #0a1a2a !important;
        color: #ffffff !important;
    }
    * { background-color: transparent !important; }
    .header {
        display: flex;
        align-items: center;
        gap: 14px;
        padding-left: 8px;
        margin-bottom: 8px;
    }
    .header img:first-child { height: 42px; }
    .header img:last-child  { height: 32px; }
    h1.title {
        font-size: 2.0rem;
        font-weight: 650;
        color: #e9f2ff !important;
        margin: 10px 0 20px 0;
        text-align: left !important;
        padding-left: 8px;
    }
    .block.svelte-1plpy97 {
        background: #0f2237 !important;
        border-color: #18344f !important;
        border-radius: 14px !important;
        box-shadow: 0 0 10px rgba(0,0,0,0.4) !important;
    }
    label.svelte-19djge9 {
        color: white !important;
        font-weight: 600 !important;
    }
    button.svelte-8prmba {
        background: #10283f !important;
        border: 1px dashed #2f567a !important;
        color: white !important;
    }
    button.svelte-8prmba:hover {
        background: #163551 !important;
    }
    .icon-wrap svg { stroke: white !important; }
    .wrap.svelte-1vmd51o { color: white !important; }
    .output_class, .output_class * {
        color: #ffffff !important;
    }
    .svelte-1lyswbr span {
        background-color: #2ec4ff !important;
    }
    .btn-classificar {
        background: #2ec4ff !important;
        color: #04121e !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        padding: 12px 20px !important;
        width: 100%;
        margin-top: 14px;
    }
    .btn-classificar:hover {
        background: #1bb4ea !important;
    }
    </style>
    """
    )

    gr.HTML(
        """
    <div class="header">
        <img src="https://upload.wikimedia.org/wikipedia/commons/a/ab/EFEI_logo.png">
    </div>
    """
    )

    gr.Markdown("<h1 class='title'>Análise de Turbidez</h1>")

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                type="pil", label="Envie a foto do casco", height=360
            )

        with gr.Column(scale=1):
            output_label = gr.Label(
                label="Resultado", num_top_classes=2, elem_classes=["output_class"]
            )
            classify_btn = gr.Button("Classificar", elem_classes=["btn-classificar"])
            classify_btn.click(classify, inputs=image_input, outputs=output_label)

app.launch(server_name="0.0.0.0", server_port=7860, ssr_mode=False)
