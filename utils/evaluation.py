import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import mean_squared_error


def evaluate_model(
    model,
    dataset: tuple[pd.DataFrame, pd.Series],
    pred: np.ndarray,
    save_dir: str | Path | None = None,
    ):
    
    # --- RMSE metric ---
    rmse = np.sqrt(mean_squared_error(dataset[1], pred))
    print(f"RMSE: {rmse:.3f}")    


    # --- Plot Observed v.s Predicted ---
    fig, ax = plt.subplots(figsize=(20,8))

    ax.plot(dataset[1].index, dataset[1], label="Observed")
    ax.plot(dataset[1].index, pred, label="Predicted", alpha=0.6)

    ax_pr = ax.twinx()

    ax_pr.bar(
        dataset[1].index,
        dataset[0]["pr"],
        width=1,
        alpha=0.3,
        label="Precip"
    )

    ax.set_ylim(0, dataset[1].max() * 2)
    ax_pr.invert_yaxis()
    ax_pr.set_ylim(dataset[0]["pr"].max() * 2.2, 0)

    ax.legend(loc="upper left")
    ax_pr.legend(loc="upper right")
    plt.title(label=f"RMSE: {rmse:.3f}")

    plt.tight_layout()
    # plt.show()


    # Optional save of run
    if save_dir is not None:
        runs = [p for p in Path(save_dir).glob("*/")]
        
        if len(runs) > 0:
            last_run = sorted(runs)[-1]
            last_run_id = str(last_run).split("_")[1]
            new_run_id = int(last_run_id) + 1
            
            last_run_rmse = float(str(last_run).split("_")[-1])
            new_run_rmse = rmse
            
            # Check the runs
            last_run_check = f"run_{int(last_run_id)}_rmse_{last_run_rmse:.3f}"
            new_run_check = f"run_{new_run_id - 1}_rmse_{new_run_rmse:.3f}"            
            
            
            if last_run_check == new_run_check:
                print("Run yet exists, run is not saved")
                return
            else:
                new_run_id = f"{new_run_id:04d}"
                run_name = f"run_{new_run_id}_rmse_{rmse:.3f}"

                save_path = Path(save_dir) / run_name
                save_path.mkdir(parents=True, exist_ok=True)
        
        else:
            run_name = f"run_0000_rmse_{rmse:.3f}"
            
            folder_path = Path(save_dir) / run_name
            folder_path.mkdir(parents=True, exist_ok=True)
        
        
        # --- Create Hyperparameter log ---
        hparams = {
            "n_estimators": model.n_estimators,
            "max_depth": model.max_depth,
            "learning_rate": model.learning_rate,
            "objective": model.objective,
            "random_state": model.random_state,
            "early_stopping_rounds": model.early_stopping_rounds
        }
        
        
        hparams_path = Path(folder_path) / "hparams.txt"
        
        with open(hparams_path, "w") as file:
            file.write(json.dumps(hparams, indent=2))
          
            
        # --- Save plot ---
        plot_path = Path(folder_path) / "observed_vs_predicted.png"
        plt.savefig(plot_path, dpi=600)
