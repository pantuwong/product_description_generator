import pandas as pd
from padthai import *

descriptions = pd.read_excel('description_th_dataset_clean.xlsx')['combine'].to_list()

flaxgpt2_model = FlaxGPT2FewShot('./results_th')
flaxgpt2_model.train(
    descriptions,
    logging_dir='./logs_th',
    num_train_epochs=100,
    train_size=0.9,
    batch_size=8,
    save_every_epochs=False
)