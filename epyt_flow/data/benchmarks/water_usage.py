import os
import numpy as np
import pandas as pd

from ..networks import download_if_necessary
from ...utils import get_temp_folder


def load_water_usage(download_dir:str=None, return_X_y:bool=True) -> dict:
    """
    "Monitoring domestic water consumption: A comparative study of model-based and data-driven 
    end-use disaggregation methods" by P. Pavlou, S. Filippou, S. Solonos, S. G. Vrachimis, 
    K. Malialis, D. G. Eliades, T. Theocharides, M. M. Polycarpou is a benchmark concerning the 
    monitoring of water usage of different household appliances. Informing consumers about it has 
    been shown to have an impact on their behavior toward drinking water conservation. The data 
    were created using the STochastic Residential water End-use Model (STREaM) 
    (Cominola et al., 2018), a modelling software developed that generates synthetic time series 
    data of a household.

    This benchmark data set is for identifying active appliances from the aggregated water 
    consumption -- i.e. a multi-class classification probelm. The data set considers the use 
    of standard toilet, standard shower, standard faucet, high efficiency clothes washer, 
    and standard dishwasher in a 2-person household for a period of 180 days (6 months) and 
    it has a resolution of 10s.
    The data set is already split into 3 sub-sets for training (90 days), validation (45 days), 
    and testing (45 days).

    For more information see https://github.com/KIOS-Research/Water-Usage-Dataset/

    .. note::

        Note that altough this data set is synthetic, only the final data set is provided.

    Parameters
    ----------
    download_dir : `str`, optional
        Path to the data files -- if None, the temp folder will be used.
        If the path does not exist, the data files will be downloaded to the give path.

        The default is None.
    return_X_y : `bool`, optional
        If True, the data is returned together with the multi-class labels as two Numpy arrays, 
        otherwise the data is returned as Pandas data frame.

        The default is True.
        
    Returns
    -------
    `dict`
        The data set as a dictionary with entries "train", "validation", and "test" containing 
        the respective data.
    """
    # Download data if necessary
    download_dir = download_dir if download_dir is not None else get_temp_folder()

    url_train_data = "https://github.com/KIOS-Research/Water-Usage-Dataset/raw/main/Dataset/Trainset.csv"
    url_valid_data = "https://github.com/KIOS-Research/Water-Usage-Dataset/raw/main/Dataset/Validationset.csv"
    url_test_data = "https://github.com/KIOS-Research/Water-Usage-Dataset/raw/main/Dataset/Testset.csv"

    f_train_in = os.path.join(download_dir, "train_water_usage.csv")
    f_valid_in = os.path.join(download_dir, "valid_water_usage.csv")
    f_test_in = os.path.join(download_dir, "test_water_usage.csv")

    download_if_necessary(f_train_in, url_train_data)
    download_if_necessary(f_valid_in, url_valid_data)
    download_if_necessary(f_test_in, url_test_data)

    # Load and return data
    df_data_train = pd.read_csv(f_train_in)
    df_data_valid = pd.read_csv(f_valid_in)
    df_data_test = pd.read_csv(f_test_in)

    if return_X_y is False:
        return {"train": df_data_train, "validation": df_data_valid, "test": df_data_test}
    else:
        r = {"train": None, "validation": None, "test": None}

        for k, df_data in zip(["train", "validation", "test"],
                              [df_data_train, df_data_valid, df_data_test]):
            X = df_data["TOTAL"].to_numpy()
            del df_data["TOTAL"]

            y = df_data.to_numpy()
            y = (y != 0).astype(np.int8)

            r[k] = (X, y)

        return r