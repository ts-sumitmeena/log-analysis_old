# Log Analysis
Provide analysis for feedback/log data of Link app

## Environment Setup
1. Install conda for package manager. You can you others like pip, apt but conda is recommended for jupyter notebook.

   From [download page](https://www.anaconda.com/download)
   
   From commandline:
   ```
   brew install anaconda export PATH="/usr/local/anaconda3/bin:$PATH"
   ```
2. If you do not have python, install it.
   ```
   brew install python
   ```
3. You can create `your_playground` environment with conda or use the default `base` one"
   ```
   // to active default base
   conda activate base 

   // to create your environment
   conda create --name your_playground
   conda create --name your_playground python=3.9 // if you already have python intalled

   // to active your environment 
   conda activate your_playground

   // to deactivate
   conda deactivate your_playground
   ```
4. Adding libraries: after activated the environment, we need to install required libraries for it. These libraries are for running `log_extraction_sms_flow_dc_ott.ipynb` script.
   ```
   conda install pandas jupyter bottleneck numexpr matplotlib pandas-datareader
   conda update --all
   ```

## IDE
1. Open jupyter notebook in browser:
   ```
   jupyter notebook file_name
   ```
2. Visual Studio Code
   
   Install extension
   ```
   searching jupyter notebook in extension
   install Jupyter
   ```

   Active your_playground environment [Visual Code Jupyter Notebook](https://code.visualstudio.com/docs/datascience/jupyter-notebooks)
   Choose `your_playground` activated before, it should have all the required dependencies.
   

## Sample
[Feedback] August 2023 
* Android https://confluence.rakuten-it.com/confluence/display/ONEAPP/iOS+Analysis
* iOS https://confluence.rakuten-it.com/confluence/display/ONEAPP/iOS+Analysis
