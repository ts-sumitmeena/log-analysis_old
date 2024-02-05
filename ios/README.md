# Log Analysis
Provide analysis for call logs

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
4. Adding dependancy to run the script.
   ```
   conda install openpyxl
   conda update --all
   ```

## Use
  go to the path of log and run the script by giving the path of main.py 
  ```
   cd [path of log folder]
   python [path log-analysis]/ios/src/main.py
   ```






