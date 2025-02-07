# Istari

## SuPAErnova

### Old Workflow

1. [salt_model_make_dataset.ipynb](https://github.com/georgestein/suPAErnova/blob/main/notebooks/salt_model_make_dataset.ipynb)
    - This requires a few files from '/global/homes/g/gstein/src/snfdata/' and "mask_info_wmin_wmax.txt". mask_info_wmin_wmax.txt I just forwarded in an email from Greg
        - It then compiles individual SN text files into the 3D arrays we discussed. 
        - It also creates salt spectra for each real spectra.
        - Then saves `snf_data_wSALT.npy', which is what is used for train.test splitting and model training
2. [make_train_test_data.py](https://github.com/georgestein/suPAErnova/blob/main/suPAErnova/make_datasets/make_train_test_data.py)
    - Splits into train test sets and does additional processing (masks laser lines)
3. [train_ae.py](https://github.com/georgestein/suPAErnova/blob/main/scripts/train_ae.py )
    - Uses the above to train the AE based on params in the config
4. [train_flow.py](https://github.com/georgestein/suPAErnova/blob/main/scripts/train_flow.py)
    - Trains the flow using params in the config
5. [run_posterior_analysis.py](https://github.com/georgestein/suPAErnova/blob/main/scripts/run_posterior_analysis.py)
    - Runs posterior analysis (uses the PAE model to fit the observations & gets error bars) 
6. [submit_train.slr](https://github.com/georgestein/suPAErnova/blob/main/scripts/slurm/submit_train.slr)
    - This is the slurm submission script that does the above 3 steps in 1 go
6. [plots_and_analysis.ipynb](https://github.com/georgestein/suPAErnova/blob/main/notebooks/plots_and_analysis.ipynb)
    - Makes plots and analyses the outputs of step #5
