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
3. Create `your_playground` environment with conda
   ```
   conda activate base
   
   conda create --name your_playground
   conda create --name your_playground python=3.9 // if you already have python intalled
  
   conda activate your_playground

   // to deactivate
   conda deactivate your_playground
   ```
4. Adding libraries: basically we setup new library for your_playground. If new libraries are introduced, we need to install it.
   ```
   conda install pandas jupyter bottleneck numexpr matplotlib pandas-datareader
   conda update -all
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
