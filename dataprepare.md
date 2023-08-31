# Data Preparation

BatteryML currently supports public datasets that are applicable for battery lifetime prediction in early cycles. Please download the raw files from the data source and then run `scripts/preprocess.py` for data preparation.

## MATR

MATR datasets contain four batches of lithium-ion phosphate (LFP)/graphite cells. Download the [three batches](https://data.matr.io/1/projects/5c48dd2bc625d700019f3204) used in [1] and the [last batch](https://data.matr.io/1/projects/5d80e633f405260001c0b60a/batches/5dcef1fe110002c7215b2c94) used in [2]. Create the folder `data/raw` and place the four batches in `data/raw/MATR`:

```tree
data/raw/MATR
├── 2017-05-12_batchdata_updated_struct_errorcorrect.mat
├── 2017-06-30_batchdata_updated_struct_errorcorrect.mat
├── 2018-04-12_batchdata_updated_struct_errorcorrect.mat
└── 2019-01-24_batchdata_updated_struct_errorcorrect.mat
```

Finally, run the preprocessing script

```bash
python scripts/preprocess.py
```

## HUST

HUST dataset contains 77 LFP cells using different discharge protocols [3]. The dataset is available via [Mendeley Data](https://data.mendeley.com/datasets/nsc7hnsg4s/2). Create the folder `data/raw` and place raw file in `data/raw/HUST`:

```tree
data/raw/HUST
└── hust_data.zip
```

Finally, run the preprocessing script

```bash
python scripts/preprocess.py
```

## CALCE

CALCE dataset [4] is publicly available at [here](https://calce.umd.edu/battery-data#Citations). Download the CS2 and CX2 series batteries and organize them as follows.

```tree
├── CS2_33.zip
├── CS2_34.zip
├── CS2_35.zip
├── CS2_36.zip
├── CS2_37.zip
├── CS2_38.zip
├── CX2_16.zip
├── CX2_33.zip
├── CX2_34.zip
├── CX2_35.zip
├── CX2_36.zip
├── CX2_37.zip
└── CX2_38.zip
```

Note that we did not use all the cells due to data format issues. We plan to include more cells in future. Run the preprocessing script to convert the files.

```bash
python scripts/preprocess.py
```

Note that the processing may take hours due to the many excel files.

## RWTH

RWTH dataset [5] is available at [here](https://publications.rwth-aachen.de/record/818642).

```tree
data/raw/RWTH
└── raw.zip
```

Finally, run the preprocessing script

```bash
python scripts/preprocess.py
```

## SNL, UL-PUR, HNEI

SNL[6], UL-PUR[7], and HNEI [8] datasets are hosted by [Battery Archive](https://www.batteryarchive.org/). They current no longer provide direct download links to these datasets. Users should apply for access first. After downloading the raw files, the file structure should look like

```tree
data/raw
├── HNEI
|   ├── HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_a_cycle_data.csv
|   ├── HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_a_timeseries.csv
|   ├── HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_cycle_data.csv
|   ├── HNEI_18650_NMC_LCO_25C_0-100_0.5-1.5C_b_timeseries.csv
...
├── SNL
|   ├── SNL_18650_LFP_15C_0-100_0.5-1C_a_cycle_data.csv
|   ├── SNL_18650_LFP_15C_0-100_0.5-1C_a_timeseries.csv
|   ├── SNL_18650_LFP_15C_0-100_0.5-1C_b_cycle_data.csv
|   ├── SNL_18650_LFP_15C_0-100_0.5-1C_b_timeseries.csv
...
├── UL_PUR
|   ├── UL-PUR_N10-EX9_18650_NCA_23C_0-100_0.5-0.5C_i_cycle_data.csv
|   ├── UL-PUR_N10-EX9_18650_NCA_23C_0-100_0.5-0.5C_i_timeseries.csv
|   ├── UL-PUR_N10-NA7_18650_NCA_23C_0-100_0.5-0.5C_g_cycle_data.csv
|   ├── UL-PUR_N10-NA7_18650_NCA_23C_0-100_0.5-0.5C_g_timeseries.csv
... 
```

Finally, run the preprocessing script

```bash
python scripts/preprocess.py
```

## Reference
[1] Severson et al. "Data-driven prediction of battery cycle life before capacity degradation." Nature Energy volume 4, pages 383–391 (2019).

[2] Attia et al. "Closed-loop optimization of fast-charging protocols for batteries with machine learning." Nature 578, 397–402 (2020).

[3] Ma et al. "Real-time personalized health status prediction of lithium-ion batteries using deep transfer learning." Energy & Environmental Science 15.10 (2022): 4083-4094.

[4] He et al. "Prognostics of lithium-ion batteries based on dempster–shafer theory and the bayesian monte carlo method." volume 196(23), pages 10314–10321, 2011.

[5] Li et al. "One-shot battery degradation trajectory prediction with deep learning." Journal of power sources, page 230024, 2021.

[6] Preger et al. "Degradation of commercial lithium-ion cells as a function of chemistry and cycling conditions." Journal of The Electrochemical Society, 167:120532, 2020.

[7] Juarez-Robles et al. "Degradation-safety analytics in lithium-ion cells: Part i. aging under charge/discharge cycling." Journal of The Electrochemical Society, 167:160510, 2020.

[8] Devie et al. "Intrinsic variability in the degradation of a batch of commercial 18650 lithium-ion cells." Energies, 11:1031, 2018.
