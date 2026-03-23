# Subtext AI Model Artifact

This artifact has been aligned to the main research question of the project:

`Is emoji-aware intent detection better than normal text-based intent detection?`

Accordingly:
- the primary system is the exact-intent detection pipeline
- the dissonance module is treated as a secondary downstream application built on top of intent-related outputs

## 1. Dataset

### Source
- Raw labelled dialogue data is stored in:
  - `data/raw/train.tsv`
  - `data/raw/dev.tsv`
  - `data/raw/test.tsv`
- The `Source` column shows three dialogue sources:
  - `superstore`
  - `friends`
  - `bigbang`

### Size
- Total raw samples: `9,304`
- Official split sizes:
  - Train: `6,165` (`66.26%`)
  - Dev: `1,106` (`11.89%`)
  - Test: `2,033` (`21.85%`)

### Processed Datasets
- `data/processed/intent30/`
  - primary dataset for 30-class exact intent classification
- `data/processed/dissonance3/`
  - secondary dataset for 3-class dissonance classification derived from intent labels:
    - `Low`
    - `Medium`
    - `High`

### 3-Class Label Distribution
- Train:
  - `Low`: `4,498`
  - `High`: `986`
  - `Medium`: `681`
- Dev:
  - `Low`: `810`
  - `High`: `177`
  - `Medium`: `119`
- Test:
  - `Low`: `1,497`
  - `High`: `329`
  - `Medium`: `207`

## 2. Class Balancing

### Dissonance 3-Class Task
- This task is imbalanced, so class-weighted loss was used.
- Approximate training-set class weights:
  - `High`: `2.0842`
  - `Low`: `0.4569`
  - `Medium`: `3.0176`
- Balancing method:
  - Inverse-frequency class weights applied through weighted cross-entropy loss.
- No oversampling or undersampling was used.

### Intent 30-Class Task
- The 30-class task is also imbalanced.
- Class weighting was tested, but the weighted 30-class model performed very poorly.
- Therefore, the final exact-intent system used the baseline unweighted setting.

## 3. Tokenization and Vectorization

### Tokenization
- Final models use `roberta-base` tokenization.
- RoBERTa uses byte-level BPE tokenization.
- Maximum sequence length: `128`

### Vectorization
- Text is converted into contextual token embeddings by the pretrained transformer.
- Hidden size: `768`
- Vocabulary size: `50,265`

### Vectorization Techniques Used
- `text_only`:
  - Only the raw text field is tokenized and encoded.
- `text_emoji`:
  - Text and emoji are concatenated before tokenization.
  - Emojis are encoded as part of the input sequence.
- Dual-encoder experiment:
  - Text is encoded by RoBERTa.
  - Emojis are encoded separately with learned emoji embeddings and fused with text features.

## 4. Layers and Activation Functions

### Final Transformer-Based Models
- Architecture: `RobertaForSequenceClassification`
- Number of hidden transformer layers: `12`
- Attention heads: `12`
- Hidden size: `768`
- Intermediate size: `3072`
- Hidden activation function: `GELU`
- Attention normalization in self-attention uses `Softmax`
- Dropout:
  - Attention dropout: `0.1`
  - Hidden dropout: `0.1`

### Dual-Encoder Experimental Model
- Text encoder: pretrained `roberta-base`
- Emoji encoder: learned embedding layer
- Fusion classifier:
  - Linear layer
  - `ReLU`
  - Dropout `0.1`
  - Final linear output layer

## 5. Selection of Models

The following model families were evaluated in the project:
- Baseline transformer:
  - `roberta-base`
- Social-media-oriented pretrained transformer:
  - `vinai/bertweet-base`
- Class-weighted transformer:
  - `roberta-base` with weighted cross-entropy
- Dual-encoder architecture:
  - `roberta-base` text encoder plus learned emoji embeddings

### Why Pretrained Models Were Used
- The dataset is moderate in size, so full training from scratch would be inefficient.
- Pretrained language models provide strong contextual representations and faster convergence.
- RoBERTa was chosen as the main backbone because it is stable, widely used, and easy to fine-tune for classification.

## 6. Project Architecture

### Overall System Architecture
- The project follows a multi-stage architecture:
  - Data layer
  - Preprocessing layer
  - Model training layer
  - Inference/API layer
  - Frontend visualization layer

### Data Layer
- Raw labelled dialogue datasets are stored in `data/raw/`.
- Uploaded WhatsApp chat exports are stored temporarily in `data/uploads/`.
- Processed modelling datasets are stored in `data/processed/`.

### Preprocessing Layer
- Raw TSV files are converted into structured CSV datasets by `scripts/prepare_split_datasets.py`.
- This stage:
  - normalizes text fields
  - keeps official train/dev/test boundaries
  - creates `source_id` values for traceability
  - maps 30 intents into 3 dissonance classes
  - prepares both `text_only` and `text+emoji` compatible datasets

### Model Training Layer
- Training scripts are responsible for fine-tuning transformer models:
  - `scripts/train_model.py`
  - `scripts/train_arch_comparison.py`
  - `scripts/train_dual_encoder.py`
- The training layer supports:
  - baseline transformer classification
  - class-weighted loss for imbalance handling
  - pretrained BERTweet comparison
  - dual-encoder text-plus-emoji fusion

### Inference Layer
- The trained models are loaded through `src/model/interface.py`.
- This layer:
  - loads the saved tokenizer and model
  - performs preprocessing at inference time
  - runs softmax classification
  - returns dissonance level, score, and exact intent where applicable

### Backend/API Layer
- The backend is built with FastAPI in `src/main.py` and `src/api/routes.py`.
- Main API responsibilities:
  - accept uploaded WhatsApp `.txt` files
  - parse the chat using the WhatsApp parser
  - run message-level inference
  - return structured JSON results

### Parsing Layer
- WhatsApp exports are parsed by `src/parser/whatsapp_parser.py`.
- Parsing extracts:
  - timestamp
  - sender
  - message content
  - platform-specific formatting differences

### Frontend Layer
- The frontend is a React + Vite application in `ui/`.
- It communicates with the FastAPI backend through `/api/v1`.
- The frontend is used to:
  - upload chat exports
  - display analysis results
  - present dissonance scores and predicted labels

### Deployed Prediction Architecture
- Current deployed workflow:
  1. User uploads a WhatsApp `.txt` export
  2. Backend parses the file into structured messages
  3. Intent model predicts the most likely exact dialogue act
  4. Optional dissonance model predicts `Low`, `Medium`, or `High`
  5. API returns intent-first results to the frontend, with dissonance as a secondary signal

## 7. Methodology

### Research Methodology Overview
- The project follows an experimental machine learning methodology.
- The main goal was to compare whether emoji-aware intent detection performs better than text-only intent detection.
- A secondary goal was to demonstrate how intent-related outputs can be used in a practical dissonance-analysis application.

### Step 1: Problem Definition
- Two related classification problems were defined:
  - primary task: exact intent classification with 30 dialogue-act labels
  - secondary task: dissonance classification with 3 classes: `Low`, `Medium`, `High`
- The 3-class dissonance task was derived from the 30-label intent taxonomy and treated as an application-oriented downstream task.

### Step 2: Data Collection and Preparation
- Existing labelled dialogue data from the raw split files was used as the base dataset.
- Raw splits were preserved to avoid leakage.
- Each sample was converted into a processed record with:
  - source identifier
  - split name
  - text
  - emoji field
  - target label
  - auxiliary label metadata

### Step 3: Label Engineering
- For the intent task:
  - the original 30 labels were kept unchanged
- For the dissonance task:
  - labels were mapped into:
    - `High`
    - `Medium`
    - `Low`
- This allowed both a fine-grained intent experiment and a simpler application-facing dissonance classifier.

### Step 4: Feature Construction
- Two feature settings were tested:
  - `text_only`
  - `text+emoji`
- In the emoji-aware setting, the emoji token was concatenated with the text input before tokenization.
- A dual-encoder architecture was also explored to represent text and emoji separately before fusion.

### Step 5: Leakage Control
- Earlier pipeline versions had leakage risk because augmented rows could be split randomly.
- The corrected methodology avoided this by:
  - using official raw train/dev/test splits directly
  - keeping processed examples inside their original split
  - avoiding row-level re-splitting of augmented duplicates across train and validation

### Step 6: Model Selection and Training
- Several architectures were compared:
  - RoBERTa baseline
  - RoBERTa with class weighting
  - BERTweet baseline
  - dual-encoder text+emoji model
- Training was carried out using Hugging Face `Trainer`.
- Comparison criteria:
  - dev accuracy
  - dev weighted F1
  - held-out test performance

### Step 7: Experimental Comparison
- The experiments were structured to answer:
  - whether emoji-aware input improves intent classification
  - whether a simpler 3-class dissonance task can act as a useful secondary analysis layer
  - whether class weighting helps on imbalanced labels

### Step 8: Final Model Choice
- The final deployed models were selected based on:
  - test performance
  - stability
  - interpretability for the application
- This led to:
  - text+emoji baseline RoBERTa for exact intent as the primary model
  - text+emoji weighted RoBERTa for 3-class dissonance as a secondary application model
- The text-only models were retained as baseline comparison models for the core research question.

### Step 9: Deployment and Integration
- The selected models were integrated into the backend inference interface.
- A WhatsApp upload pipeline was connected to the parser, model interface, and API routes.
- The frontend was configured to call the backend and display exact intent predictions, with dissonance shown as an additional analytic signal.

### Step 10: Evaluation and Interpretation
- Performance was assessed on held-out dev and test sets.
- Accuracy and weighted F1 were used as the main quantitative measures.
- Generalization was interpreted using dev-test gaps to identify:
  - acceptable fit
  - mild overfitting
  - underfitting
- Experimental findings were also interpreted in light of dataset validity, especially the effect of synthetic emoji assignment.

## 8. Final Model Used

### Final Primary Model
- Model: `models/intent30_text_emoji_baseline`
- Task: 30-class intent classification
- Input: text + emoji
- Backbone: `roberta-base`
- Loss: standard cross-entropy

### Final Secondary Model
- Model: `models/dissonance3_text_emoji_weighted`
- Task: 3-class dissonance classification
- Input: text + emoji
- Backbone: `roberta-base`
- Loss: weighted cross-entropy

### Text-Only Baseline Comparison Models
- `models/intent30_text_only_baseline`
- `models/dissonance3_text_only_weighted`
- These were retained as baseline models for ablation and comparison, but the main research comparison centers on the exact-intent models.

## 9. Train-Test Split

- The project now uses the official raw split files directly:
  - train: `data/raw/train.tsv`
  - dev: `data/raw/dev.tsv`
  - test: `data/raw/test.tsv`
- This avoids the earlier leakage issue caused by row-level splitting of augmented data.
- The processed train/dev/test CSV files preserve the official split boundaries.

## 10. Hyperparameter Tuning

### Training Configuration for Final Comparison Runs
- Epochs: `5`
- Batch size:
  - Train: `8`
  - Eval/Test: `8`
- Warmup steps: `50`
- Weight decay: `0.01`
- Max sequence length: `128`
- Seed: `42`
- Best model selection metric: weighted F1 on dev set

### Learning Setup
- Optimizer: Hugging Face Trainer default (`AdamW`)
- Learning rate:
  - Not manually overridden in the comparison script
  - Hugging Face default was used (`5e-5`)

### Tuning Strategy
- Manual experimental comparison was used rather than grid search or Bayesian optimization.
- The main tuning dimensions were:
  - model family
  - weighted vs unweighted loss
  - text-only vs text+emoji input
  - number of output classes (`30` vs `3`)

## 11. Model Testing and Evaluation

### Evaluation Procedure
- Training was performed on the train split.
- Model selection was based on dev-set weighted F1.
- Final performance was reported on the held-out test split.

### Metrics Used
- Accuracy
- Weighted F1-score
- Loss
- Throughput:
  - samples per second
  - steps per second

## 12. Evaluation Scores

### 30-Class Exact Intent Results

#### Text-Only Baseline Model
- Dev accuracy: `0.5814`
- Dev weighted F1: `0.5731`
- Test accuracy: `0.5863`
- Test weighted F1: `0.5773`

#### Text+Emoji Baseline Model
- Dev accuracy: `0.9665`
- Dev weighted F1: `0.9664`
- Test accuracy: `0.9528`
- Test weighted F1: `0.9527`

#### 30-Class Weighted Model
- Dev accuracy: `0.0958`
- Dev weighted F1: `0.0168`
- Test accuracy: `0.1067`
- Test weighted F1: `0.0206`
- Conclusion:
  - Class weighting was harmful for the 30-class exact-intent setup in this project.

### 3-Class Dissonance Results

#### Text-Only Weighted Model
- Dev accuracy: `0.8020`
- Dev weighted F1: `0.8009`
- Test accuracy: `0.7762`
- Test weighted F1: `0.7740`

#### Text+Emoji Weighted Model
- Dev accuracy: `0.9846`
- Dev weighted F1: `0.9846`
- Test accuracy: `0.9852`
- Test weighted F1: `0.9854`

## 13. Cross Validation

- K-fold cross validation was **not** used in the final pipeline.
- Reason:
  - the dataset already provides official train/dev/test splits
  - preserving these splits made the evaluation cleaner and avoided leakage from augmented variants
- Instead of cross validation, a fixed held-out dev set and a separate held-out test set were used.

## 14. Model Overfitting and Underfitting

### 3-Class Text-Only Weighted Model
- Dev F1: `0.8009`
- Test F1: `0.7740`
- Interpretation:
  - small generalization gap
  - mild overfitting at most
  - overall acceptable generalization

### 3-Class Text+Emoji Weighted Model
- Dev F1: `0.9846`
- Test F1: `0.9854`
- Interpretation:
  - no obvious dev-test gap
  - however, performance is likely inflated by highly informative synthetic emoji features
  - this should be treated as a strong experimental result, not necessarily real-world generalization

### 30-Class Text-Only Baseline Model
- Dev F1: `0.5731`
- Test F1: `0.5773`
- Interpretation:
  - no meaningful overfitting
  - likely some underfitting because the 30-class task is difficult using text alone

### 30-Class Text+Emoji Baseline Model
- Dev F1: `0.9664`
- Test F1: `0.9527`
- Interpretation:
  - only a small generalization gap
  - but the result is likely inflated because emoji assignment is synthetic and strongly correlated with label

### 30-Class Weighted Model
- Very low dev and test performance indicates optimization failure or harmful reweighting.
- This is best described as underfitting or unstable training for that setup.

## 15. Important Validity Note

- The emoji-aware models clearly outperform the text-only models on the prepared datasets in this project.
- However, the current emoji field is synthetically assigned from intent-aware rules during dataset preparation.
- Therefore:
  - it is valid to say that emoji-aware intent detection outperformed text-only prediction in this experimental setup
  - it is not yet valid to claim that the same improvement magnitude will automatically transfer to real-world WhatsApp chats without further testing on naturally occurring emoji data

## 16. Recommended Dissertation Framing

- Main system result:
  - 30-class intent, text+emoji, baseline RoBERTa
- Main baseline comparison:
  - 30-class intent, text-only, baseline RoBERTa
- Secondary application result:
  - 3-class dissonance, text+emoji, weighted RoBERTa
- Main research conclusion:
  - emoji-aware intent detection outperformed text-only intent detection on the prepared dataset
- Limitation:
  - emoji features were synthetically generated and may inflate measured gains
