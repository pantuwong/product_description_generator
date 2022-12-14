import pandas as pd
import torch
from torch.utils.data import Dataset, random_split
from transformers import GPT2Tokenizer, TrainingArguments, Trainer, GPTNeoForCausalLM, Pipeline

torch.manual_seed(42)

pretrained = 'EleutherAI/gpt-neo-125M'
tokenizer = GPT2Tokenizer.from_pretrained(pretrained, bos_token='<|startoftext|>',
                                                  eos_token='<|endoftext|>', pad_token='<|pad|>')
model = GPTNeoForCausalLM.from_pretrained(pretrained).cuda()
model.resize_token_embeddings(len(tokenizer))

descriptions = pd.read_excel('description_en_dataset_clean.xlsx')['combine']

max_length = max([len(tokenizer.encode(description)) for description in descriptions])

class DescriptionDataset(Dataset):
    def __init__(self, txt_list, tokenizer, max_length):
        self.input_ids = []
        self.attn_masks = []
        self.labels = []
        for txt in txt_list:
            encodings_dict = tokenizer('<|startoftext|>' + txt + '<|endoftext|>', truncation=True,
                                       max_length=max_length, padding="max_length")
            self.input_ids.append(torch.tensor(encodings_dict['input_ids']))
            self.attn_masks.append(torch.tensor(encodings_dict['attention_mask']))

    def __len__(self):
        return len(self.input_ids)

    def __getitem__(self, idx):
        return self.input_ids[idx], self.attn_masks[idx]

dataset = DescriptionDataset(descriptions, tokenizer, max_length=max_length)
train_size = int(0.9 * len(dataset))
train_dataset, val_dataset = random_split(dataset, [train_size, len(dataset) - train_size])

import gc
gc.collect()

torch.cuda.empty_cache()

training_args = TrainingArguments(output_dir='./results_th', num_train_epochs=20, logging_steps=50000, save_steps=50000,
                                  per_device_train_batch_size=2, per_device_eval_batch_size=2, load_best_model_at_end=True,
                                        save_strategy = "no",
                                  warmup_steps=100, weight_decay=0.01, logging_dir='./logs_th', report_to = 'none')

trainer = Trainer(model=model,  args=training_args, train_dataset=train_dataset, 
        eval_dataset=val_dataset, data_collator=lambda data: {'input_ids': torch.stack([f[0] for f in data]),
                                                              'attention_mask': torch.stack([f[1] for f in data]),
                                                              'labels': torch.stack([f[0] for f in data])})
trainer.train(resume_from_checkpoint = './results_th/checkpoint-350000')
trainer.save_model('./results_th')

