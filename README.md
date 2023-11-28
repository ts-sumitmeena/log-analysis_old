# Feedback / Log Analysis
Provide analysis for feedback/log data of Link app

## Environment Setup
1. Install conda for package manager. You can you others like pip, apt but conda is recommended for jupyter notebook.

   From [download page](https://www.anaconda.com/download)
   
   From commandline:
   ```
   brew install anaconda export PATH="/usr/local/anaconda3/bin:$PATH"
   ```
3. Create `your_playground` environment with conda
   ```
   conda activate base
   conda create —name your_playground
   conda active your_playground
   ```
4. Adding libraries. If new libraries are introduced, we need to install it.
   ```
   conda install pandas jupyter bottleneck numexpr matplotlib pandas-reader
   conda update —all
   ```
5. If you do not have python, install it.
   ```
   brew install python
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
   

## Sample
[Feedback] August 2023 
* Android https://confluence.rakuten-it.com/confluence/display/ONEAPP/iOS+Analysis
* iOS https://confluence.rakuten-it.com/confluence/display/ONEAPP/iOS+Analysis
